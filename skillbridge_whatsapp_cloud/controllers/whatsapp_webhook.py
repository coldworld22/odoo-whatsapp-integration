import hashlib
import hmac
import json
import logging

from odoo import _, http
from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo.tools import html_escape

_logger = logging.getLogger(__name__)


class WhatsAppWebhookController(http.Controller):
    """Handle WhatsApp webhook verification and callbacks with signature validation."""

    @http.route("/whatsapp/webhook", auth="public", csrf=False, methods=["GET", "POST"])
    def whatsapp_webhook(self, **kwargs):
        if request.httprequest.method == "GET":
            return self._handle_verification(kwargs)
        return self._handle_callback()

    @http.route("/whatsapp/webhook/ping", auth="public", csrf=False, methods=["GET"])
    def whatsapp_webhook_ping(self, **kwargs):
        """Lightweight endpoint to verify reachability from Meta or monitoring tools."""
        params = request.env["ir.config_parameter"].sudo()
        verify_token = params.get_param("skillbridge_whatsapp_cloud.webhook_verify_token")
        app_secret = params.get_param("skillbridge_whatsapp_cloud.app_secret")
        if not verify_token or not app_secret:
            _logger.warning("Webhook ping failed: missing verify token or app secret.")
            return http.Response(_("Webhook not configured"), status=503, mimetype="text/plain")
        return http.Response(_("OK"), status=200, mimetype="text/plain")

    def _handle_verification(self, params):
        verify_token = request.env["ir.config_parameter"].sudo().get_param(
            "skillbridge_whatsapp_cloud.webhook_verify_token"
        )
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge")

        if mode == "subscribe" and token and token == verify_token:
            return http.Response(challenge or "", status=200, mimetype="text/plain")
        _logger.warning("WhatsApp webhook verification failed: mode=%s token=%s", mode, token)
        return http.Response(_("Verification failed"), status=403, mimetype="text/plain")

    def _handle_callback(self):
        # Validate signature
        app_secret = request.env["ir.config_parameter"].sudo().get_param(
            "skillbridge_whatsapp_cloud.app_secret"
        )
        if not app_secret:
            _logger.error("WhatsApp webhook received but app secret is not configured.")
            raise AccessDenied()

        signature = request.httprequest.headers.get("X-Hub-Signature-256")
        body_bytes = request.httprequest.get_data(cache=False, as_text=False)

        if not self._is_valid_signature(app_secret, signature, body_bytes):
            _logger.warning("Invalid WhatsApp webhook signature.")
            raise AccessDenied()

        # Parse JSON payload safely
        try:
            payload = json.loads(body_bytes.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            _logger.warning("WhatsApp webhook received invalid JSON.")
            return http.Response(_("Invalid payload"), status=400, mimetype="text/plain")

        # Lightly log top-level info without sensitive content
        summary = payload.get("entry", [{}])[0].get("id")
        _logger.info("WhatsApp webhook received for entry id: %s", summary)

        self._process_messages(payload)
        self._process_status_updates(payload)
        return http.Response(status=200)

    @staticmethod
    def _is_valid_signature(app_secret, header_signature, body):
        if not header_signature or not header_signature.startswith("sha256="):
            return False
        try:
            received_sig = header_signature.split("=", 1)[1]
        except IndexError:
            return False
        expected = hmac.new(app_secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, received_sig)

    def _process_messages(self, payload):
        """Persist inbound messages to chatter/log for traceability."""
        entries = payload.get("entry") or []
        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value") or {}
                for message in value.get("messages") or []:
                    self._handle_inbound_message(message)

    def _handle_inbound_message(self, message):
        msg_id = message.get("id")
        sender = (message.get("from") or "").strip()
        msg_type = message.get("type")
        text_body = ""
        if msg_type == "text":
            text_body = (message.get("text") or {}).get("body") or ""
        elif msg_type == "button":
            text_body = (message.get("button") or {}).get("text") or ""

        # Find partner by mobile/phone with or without leading +
        Partner = request.env["res.partner"].sudo()
        search_numbers = [sender]
        if sender and not sender.startswith("+"):
            search_numbers.append("+" + sender)
        partner = Partner.search(
            ["|", ("mobile", "in", search_numbers), ("phone", "in", search_numbers)], limit=1
        )

        order = False
        if partner:
            order = request.env["sale.order"].sudo().search(
                [("partner_id", "=", partner.id)], order="id desc", limit=1
            )

        # Log inbound message
        log_vals = {
            "message_id": msg_id or "",
            "order_id": order.id if order else False,
            "partner_id": partner.id if partner else False,
            "direction": "inbound",
            "status": msg_type or "",
            "last_payload": json.dumps(message),
        }
        request.env["whatsapp.message.log"].sudo().create(log_vals)

        # Post to chatter on order if available, otherwise on partner
        body_parts = []
        if sender:
            body_parts.append(html_escape(_("Incoming WhatsApp from %s") % sender))
        if text_body:
            body_parts.append(html_escape(text_body))
        if body_parts:
            body_html = "<br/>".join(body_parts)
            if order:
                order.message_post(body=body_html, message_type="comment")
            elif partner:
                partner.message_post(body=body_html, message_type="comment")
        self._trigger_keyword_actions(partner or order and order.partner_id, text_body)

    def _process_status_updates(self, payload):
        """Update message logs and chatter for failed/undelivered statuses."""
        entries = payload.get("entry") or []
        for entry in entries:
            for change in entry.get("changes", []):
                value = change.get("value") or {}
                for status in value.get("statuses") or []:
                    msg_id = status.get("id")
                    status_text = status.get("status")
                    errors = status.get("errors") or []
                    self._update_log_and_chatter(msg_id, status_text, errors, status)

    def _update_log_and_chatter(self, message_id, status_text, errors, raw_status):
        if not message_id:
            return
        log_record = request.env["whatsapp.message.log"].sudo().search(
            [("message_id", "=", message_id)], limit=1
        )
        if not log_record:
            _logger.info("Received WhatsApp status for unknown message id: %s", message_id)
            return

        error_code = None
        if errors and isinstance(errors, list):
            error_code = errors[0].get("code")

        log_record.write(
            {
                "status": status_text or log_record.status,
                "error_code": error_code or log_record.error_code,
                "last_payload": json.dumps(raw_status),
            }
        )
        self._update_campaign_queue(log_record, message_id, status_text, errors)

        order = log_record.order_id
        if status_text in ("delivered", "read"):
            return

        if status_text in ("failed", "undelivered") or errors:
            if order:
                body_parts = [_("WhatsApp message %s: %s") % (message_id, status_text or "")]
                if errors:
                    body_parts.append(_("Errors: %s") % errors)
                order.message_post(body="<br/>".join(body_parts), message_type="comment")
                if order.user_id:
                    order.activity_schedule(
                        "mail.mail_activity_data_warning",
                        user_id=order.user_id.id,
                        summary=_("WhatsApp send failed"),
                        note=_("Message %s failed: %s") % (message_id, errors or status_text),
                    )
            _logger.warning(
                "WhatsApp delivery issue for message %s on order %s: status=%s errors=%s",
                message_id,
                order.display_name if order else "n/a",
                status_text,
                errors,
            )

    def _update_campaign_queue(self, log_record, message_id, status_text, errors):
        """Mirror webhook delivery feedback onto campaign queue lines to avoid drip progression on failures."""
        if not log_record.campaign_id:
            return
        Queue = request.env["whatsapp.campaign.queue"].sudo()
        queue_line = Queue.search(
            [("campaign_id", "=", log_record.campaign_id.id), ("message_id", "=", message_id)],
            limit=1,
        )
        if not queue_line and log_record.partner_id:
            queue_line = Queue.search(
                [("campaign_id", "=", log_record.campaign_id.id), ("partner_id", "=", log_record.partner_id.id)],
                limit=1,
            )
        if not queue_line:
            return

        if status_text in ("failed", "undelivered") or errors:
            err_parts = []
            for err in errors or []:
                if isinstance(err, dict):
                    title = err.get("title") or err.get("message") or ""
                    code = err.get("code")
                    err_parts.append(f"[{code}] {title}" if code else title)
                else:
                    err_parts.append(str(err))
            err_msg = "; ".join([p for p in err_parts if p]) or (status_text or "")
            queue_line.write({"status": "failed", "last_error": err_msg})
        elif status_text in ("delivered", "read"):
            # Keep status as sent but ensure it isn't marked pending in edge cases.
            queue_line.write({"status": "sent"})

    def _trigger_keyword_actions(self, partner, text_body):
        if not partner or not text_body:
            return
        keyword = text_body.strip().upper()
        mapping = {
            "PAY": _("Customer requested payment help."),
            "HELP": _("Customer requested assistance."),
            "CALL": _("Customer requested a call back."),
        }
        if keyword in mapping:
            user_id = partner.user_id.id if partner and partner.user_id else request.env.user.id
            partner.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=user_id,
                summary=_("WhatsApp keyword: %s") % keyword,
                note=mapping[keyword],
            )
