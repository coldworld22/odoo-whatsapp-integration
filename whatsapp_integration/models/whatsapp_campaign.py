import logging
import re
from datetime import datetime, time, timedelta

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)
MOBILE_PATTERN = re.compile(r"^\+?[1-9]\d{6,14}$")


class WhatsAppCampaign(models.Model):
    _name = "whatsapp.campaign"
    _description = "WhatsApp Campaign"
    _order = "create_date desc"

    name = fields.Char(required=True)
    message_mode = fields.Selection(
        [("text", "Plain Text"), ("template", "Template"), ("media_image", "Image")],
        default="text",
        required=True,
    )
    template_id = fields.Many2one("whatsapp.template", string="Template")
    message_body = fields.Text(string="Message")
    media_url = fields.Char(string="Image URL")
    partner_tag_ids = fields.Many2many("res.partner.category", string="Partner Tags")
    partner_domain = fields.Text(
        string="Additional Partner Domain",
        help="Optional domain to further filter partners. Example: [('country_id.code','=','US')]",
        default="[]",
    )
    throttle_batch_size = fields.Integer(string="Batch Size", default=50)
    window_start = fields.Float(string="Send Window Start (hour)", help="0-24 in server timezone", default=8.0)
    window_end = fields.Float(string="Send Window End (hour)", help="0-24 in server timezone", default=20.0)
    state = fields.Selection(
        [("draft", "Draft"), ("running", "Running"), ("paused", "Paused"), ("done", "Done")],
        default="draft",
        required=True,
    )
    last_run = fields.Datetime(string="Last Run")
    next_run = fields.Datetime(string="Next Run")
    queue_ids = fields.One2many("whatsapp.campaign.queue", "campaign_id", string="Queue Lines")
    step_ids = fields.One2many("whatsapp.campaign.step", "campaign_id", string="Drip Steps")
    total_pending = fields.Integer(compute="_compute_totals", store=False)
    total_sent = fields.Integer(compute="_compute_totals", store=False)
    total_failed = fields.Integer(compute="_compute_totals", store=False)
    total_delivered = fields.Integer(compute="_compute_totals", store=False)
    total_read = fields.Integer(compute="_compute_totals", store=False)

    def action_generate_queue(self):
        for campaign in self:
            domain = [("mobile", "!=", False)]
            if campaign.partner_tag_ids:
                domain.append(("category_id", "in", campaign.partner_tag_ids.ids))
            try:
                extra_domain = safe_eval(campaign.partner_domain or "[]")
                domain += extra_domain
            except Exception:
                raise UserError(_("Invalid partner domain syntax."))
            partners = self.env["res.partner"].search(domain)
            existing_partner_ids = set(campaign.queue_ids.mapped("partner_id").ids)
            to_create = []
            for partner in partners:
                if partner.id in existing_partner_ids:
                    continue
                to_create.append(
                    {
                        "campaign_id": campaign.id,
                        "partner_id": partner.id,
                        "status": "pending",
                        "step_id": campaign._get_first_step().id if campaign._get_first_step() else False,
                        "next_attempt_at": fields.Datetime.now(),
                    }
                )
            if to_create:
                self.env["whatsapp.campaign.queue"].create(to_create)
        return True

    def action_start(self):
        self.write({"state": "running", "next_run": fields.Datetime.now()})
        return True

    def action_pause(self):
        self.write({"state": "paused"})
        return True

    def action_done(self):
        self.write({"state": "done"})
        return True

    def _compute_totals(self):
        for rec in self:
            rec.total_pending = len(rec.queue_ids.filtered(lambda l: l.status == "pending"))
            rec.total_sent = len(rec.queue_ids.filtered(lambda l: l.status == "sent"))
            rec.total_failed = len(rec.queue_ids.filtered(lambda l: l.status == "failed"))
            logs = self.env["whatsapp.message.log"].sudo().search([("campaign_id", "=", rec.id)])
            rec.total_delivered = len(logs.filtered(lambda l: l.status == "delivered"))
            rec.total_read = len(logs.filtered(lambda l: l.status == "read"))

    def _within_window(self):
        now = fields.Datetime.context_timestamp(self, datetime.utcnow()).time()
        start_hour = self.window_start or 0
        end_hour = self.window_end or 24
        start_time = time(int(start_hour), int((start_hour % 1) * 60))
        end_time = time(int(end_hour), int((end_hour % 1) * 60))
        if start_time <= end_time:
            return start_time <= now <= end_time
        return now >= start_time or now <= end_time

    def _cron_run_batch(self, limit=None):
        campaigns = self.search([("state", "=", "running")])
        for campaign in campaigns:
            if not campaign._within_window():
                continue
            batch_limit = limit or campaign.throttle_batch_size or 50
            now = fields.Datetime.now()
            lines = campaign.queue_ids.filtered(
                lambda l: l.status == "pending" and (not l.next_attempt_at or l.next_attempt_at <= now)
            )[:batch_limit]
            if not lines:
                campaign.write({"state": "done"})
                continue
            for line in lines:
                campaign._send_line(line)
            campaign.write({"last_run": fields.Datetime.now()})
        return True

    def _get_whatsapp_credentials(self):
        # Reuse sale.order helper to honor per-company whatsapp.account fallback
        return self.env["sale.order"]._get_whatsapp_credentials()

    def _send_line(self, line):
        partner = line.partner_id
        mobile = (partner.mobile or "").strip()
        if not mobile or not MOBILE_PATTERN.match(mobile):
            line.write({"status": "failed", "last_error": _("Invalid mobile number")})
            return
        if hasattr(partner, "whatsapp_opt_in") and not partner.whatsapp_opt_in:
            line.write({"status": "failed", "last_error": _("Partner has not opted in for WhatsApp")})
            return
        token, phone_number_id = self._get_whatsapp_credentials()
        try:
            mode, template, body, media_url = self._get_line_payload(line)
            if mode == "template":
                if not template:
                    raise UserError(_("Template is required for template campaigns."))
                msg_id = self._send_template(mobile, token, phone_number_id, template)
            elif mode == "media_image":
                if not media_url:
                    raise UserError(_("Image URL is required for media campaigns."))
                msg_id = self._send_media_image(mobile, token, phone_number_id, media_url, body)
            else:
                if not body:
                    raise UserError(_("Message body is required for text campaigns."))
                msg_id = self._send_text(mobile, token, phone_number_id, body)
            line.write({"status": "sent", "message_id": msg_id or False, "attempts": line.attempts + 1})
            self._log_message(msg_id, partner)
            self._schedule_next_step(line)
        except Exception as exc:
            _logger.warning("Campaign send failed for partner %s: %s", partner.id, exc)
            attempts = line.attempts + 1
            backoff_minutes = min(60, 5 * attempts)
            next_attempt = fields.Datetime.now() + timedelta(minutes=backoff_minutes)
            status = "failed" if attempts >= 3 else "pending"
            line.write(
                {
                    "status": status,
                    "last_error": str(exc),
                    "attempts": attempts,
                    "next_attempt_at": next_attempt,
                }
            )

    def _send_text(self, mobile, token, phone_number_id, message_body):
        url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": mobile,
            "type": "text",
            "text": {"body": message_body},
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if not response.ok:
            raise UserError(_("WhatsApp API error (%s): %s") % (response.status_code, response.text))
        return self._extract_message_id(response)

    def _send_template(self, mobile, token, phone_number_id, template):
        url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": mobile,
            "type": "template",
            "template": {
                "name": template.template_name,
                "language": {"code": template.language_code or "en_US"},
            },
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if not response.ok:
            raise UserError(_("WhatsApp API error (%s): %s") % (response.status_code, response.text))
        return self._extract_message_id(response)

    def _send_media_image(self, mobile, token, phone_number_id, media_url, caption=None):
        url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": mobile,
            "type": "image",
            "image": {"link": media_url, "caption": caption or ""},
        }
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if not response.ok:
            raise UserError(_("WhatsApp API error (%s): %s") % (response.status_code, response.text))
        return self._extract_message_id(response)

    def _extract_message_id(self, response):
        try:
            payload = response.json()
        except ValueError:
            return None
        messages = payload.get("messages") or []
        if messages and isinstance(messages, list):
            return messages[0].get("id")
        return None

    def _log_message(self, msg_id, partner):
        self.env["whatsapp.message.log"].sudo().create(
            {
                "message_id": msg_id or "",
                "partner_id": partner.id,
                "campaign_id": self.id,
                "direction": "outbound",
                "status": "sent",
            }
        )

    def _get_line_payload(self, line):
        step = line.step_id
        if step:
            return step.message_mode, step.template_id, step.message_body, step.media_url
        media_url = self.media_url or self.env["ir.config_parameter"].sudo().get_param(
            "whatsapp_integration.default_media_url"
        )
        return self.message_mode, self.template_id, self.message_body, media_url

    def _get_first_step(self):
        return self.step_ids.sorted("sequence")[:1]

    def _get_next_step(self, current_step):
        steps = self.step_ids.sorted("sequence")
        for idx, step in enumerate(steps):
            if step.id == current_step.id and idx + 1 < len(steps):
                return steps[idx + 1]
        return False

    def _schedule_next_step(self, line):
        current_step = line.step_id
        next_step = self._get_next_step(current_step) if current_step else False
        if not next_step:
            line.write({"status": "sent"})
            return
        delay_hours = next_step.delay_hours or 0
        line.write(
            {
                "status": "pending",
                "step_id": next_step.id,
                "next_attempt_at": fields.Datetime.now() + timedelta(hours=delay_hours),
                "attempts": 0,
                "message_id": False,
                "last_error": False,
            }
        )
