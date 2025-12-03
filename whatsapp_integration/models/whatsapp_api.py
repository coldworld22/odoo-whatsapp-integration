import logging
import re
from typing import Optional, Tuple

import requests

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WhatsAppAPI(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        auto_send = (
            self.env["ir.config_parameter"].sudo().get_param("whatsapp_integration.auto_send_on_confirm") == "True"
        )
        if auto_send:
            for order in self:
                try:
                    order._send_whatsapp_payloads(
                        message_body=order._get_default_whatsapp_message(),
                        message_mode="text",
                        include_sale_order_pdf=True,
                        include_invoice_pdf=False,
                    )
                except Exception as exc:
                    _logger.warning("Auto WhatsApp send on confirm failed for %s: %s", order.name, exc)
        return res

    def action_send_whatsapp(self):
        """Open wizard to send WhatsApp message with optional PDFs."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Send via WhatsApp"),
            "res_model": "whatsapp.send.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_order_id": self.id,
                "default_message_body": self._get_default_whatsapp_message(),
                "active_model": self._name,
                "active_id": self.id,
            },
        }

    def _get_default_whatsapp_message(self):
        self.ensure_one()
        return _("Hello %(customer)s, here is your order %(order)s.") % {
            "customer": self.partner_id.name or "",
            "order": self.name or "",
        }

    def _get_whatsapp_credentials(self) -> Tuple[str, str]:
        company = self.env.company
        account = (
            self.env["whatsapp.account"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("is_default", "=", True),
                    ("token", "!=", False),
                    ("phone_number_id", "!=", False),
                ],
                limit=1,
            )
        )
        if account:
            return account.token, account.phone_number_id
        token = self.env["ir.config_parameter"].sudo().get_param("whatsapp_integration.token")
        phone_number_id = self.env["ir.config_parameter"].sudo().get_param("whatsapp_integration.phone_number_id")
        if not token or not phone_number_id:
            raise UserError(_("WhatsApp API credentials are not configured in Settings."))
        return token, phone_number_id

    def _get_whatsapp_mobile(self) -> str:
        self.ensure_one()
        mobile = (self.partner_id.mobile or "").strip()
        if not mobile:
            raise UserError(_("The customer mobile number is missing on this order."))
        if not re.match(r"^\+?[1-9]\d{6,14}$", mobile):
            raise UserError(_("The customer mobile number must be in international format (E.164)."))
        if hasattr(self.partner_id, "whatsapp_opt_in") and not self.partner_id.whatsapp_opt_in:
            raise UserError(_("Customer has not opted in for WhatsApp messaging."))
        return mobile

    def _send_whatsapp_text(self, mobile, token, phone_number_id, message_body):
        url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": mobile,
            "type": "text",
            "text": {"body": message_body},
        }
        response = self._dispatch_whatsapp_request(
            url, headers=headers, json=payload, timeout=10, return_response=True
        )
        return self._extract_message_id(response)

    def _send_whatsapp_template(self, mobile, token, phone_number_id, template, components=None):
        url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": mobile,
            "type": "template",
            "template": {
                "name": template.template_name,
                "language": {"code": template.language_code or "en_US"},
                "components": components or [],
            },
        }
        response = self._dispatch_whatsapp_request(
            url, headers=headers, json=payload, timeout=10, return_response=True
        )
        return self._extract_message_id(response)

    def _send_whatsapp_interactive_buttons(self, mobile, token, phone_number_id, body_text, buttons):
        url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        action_buttons = []
        for idx, title in enumerate(buttons[:3], start=1):
            action_buttons.append(
                {
                    "type": "reply",
                    "reply": {
                        "id": f"btn_{idx}",
                        "title": title,
                    },
                }
            )
        payload = {
            "messaging_product": "whatsapp",
            "to": mobile,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {"buttons": action_buttons},
            },
        }
        response = self._dispatch_whatsapp_request(
            url, headers=headers, json=payload, timeout=10, return_response=True
        )
        return self._extract_message_id(response)

    def _send_whatsapp_interactive_list(self, mobile, token, phone_number_id, body_text, list_payload):
        url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        rows = list_payload.get("rows") or []
        section_title = list_payload.get("section_title") or "Options"
        payload = {
            "messaging_product": "whatsapp",
            "to": mobile,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": body_text},
                "action": {
                    "button": list_payload.get("button") or "Choose",
                    "sections": [
                        {
                            "title": section_title,
                            "rows": rows,
                        }
                    ],
                },
            },
        }
        response = self._dispatch_whatsapp_request(
            url, headers=headers, json=payload, timeout=10, return_response=True
        )
        return self._extract_message_id(response)

    def _send_whatsapp_image(self, mobile, token, phone_number_id, media_url, caption=None):
        url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": mobile,
            "type": "image",
            "image": {
                "link": media_url,
                "caption": caption or "",
            },
        }
        response = self._dispatch_whatsapp_request(
            url, headers=headers, json=payload, timeout=15, return_response=True
        )
        return self._extract_message_id(response)

    def _upload_whatsapp_media(
        self, file_content, filename, token, phone_number_id, mimetype="application/pdf"
    ):
        url = f"https://graph.facebook.com/v20.0/{phone_number_id}/media"
        headers = {"Authorization": f"Bearer {token}"}
        files = {
            "file": (filename, file_content, mimetype),
        }
        data = {"messaging_product": "whatsapp"}
        response = self._dispatch_whatsapp_request(
            url, headers=headers, files=files, data=data, timeout=30, return_response=True
        )
        try:
            media_id = response.json().get("id")
        except ValueError:
            media_id = None
        if not media_id:
            raise UserError(_("Failed to upload media to WhatsApp."))
        return media_id

    def _send_whatsapp_document(self, mobile, token, phone_number_id, file_content, filename, caption=None):
        media_id = self._upload_whatsapp_media(file_content, filename, token, phone_number_id)
        url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": mobile,
            "type": "document",
            "document": {
                "id": media_id,
                "filename": filename,
                "caption": caption or "",
            },
        }
        response = self._dispatch_whatsapp_request(
            url, headers=headers, json=payload, timeout=15, return_response=True
        )
        return self._extract_message_id(response)

    def _dispatch_whatsapp_request(self, url, **kwargs):
        return_response = kwargs.pop("return_response", False)
        try:
            response = requests.post(url, **kwargs)
        except requests.RequestException as exc:
            _logger.exception("WhatsApp request failed for sale.order %s", getattr(self, "name", ""))
            raise UserError(_("Failed to reach WhatsApp API: %s") % exc)

        if not response.ok:
            try:
                detail = response.json()
                err_message = detail.get("error", {}).get("message") or response.text
            except ValueError:
                err_message = response.text
            _logger.warning(
                "WhatsApp API error for sale.order %s: status=%s, response=%s",
                getattr(self, "name", ""),
                response.status_code,
                err_message,
            )
            raise UserError(_("WhatsApp API error (%s): %s") % (response.status_code, err_message))
        return response if return_response else True

    def _extract_message_id(self, response: requests.Response) -> Optional[str]:
        try:
            payload = response.json()
        except ValueError:
            return None
        messages = payload.get("messages") or []
        if messages and isinstance(messages, list):
            return messages[0].get("id")
        return None

    def _render_sale_order_pdf(self):
        self.ensure_one()
        report = self.env.ref("sale.action_report_saleorder", raise_if_not_found=False)
        if not report:
            raise UserError(_("Sale order PDF report is missing."))
        pdf_content, _ = report._render_qweb_pdf(self.id)
        filename = f"{self.name or 'sale_order'}.pdf"
        return pdf_content, filename

    def _get_invoice_candidates(self):
        self.ensure_one()
        if not hasattr(self, "invoice_ids"):
            return self.env["account.move"]
        return self.invoice_ids.filtered(lambda mv: mv.state == "posted" and mv.move_type in ("out_invoice", "out_refund"))

    def _render_invoice_pdf(self, invoice):
        report = self.env.ref("account.account_invoices", raise_if_not_found=False) or self.env.ref(
            "account.report_invoice_document", raise_if_not_found=False
        )
        if not report:
            raise UserError(_("Invoice PDF report is missing."))
        pdf_content, _ = report._render_qweb_pdf(invoice.id)
        filename = f"{invoice.name or 'invoice'}.pdf"
        return pdf_content, filename

    def _send_whatsapp_payloads(
        self,
        message_body,
        message_mode="text",
        template=None,
        template_components=None,
        buttons=None,
        list_payload=None,
        include_sale_order_pdf=True,
        include_invoice_pdf=False,
    ):
        self.ensure_one()
        mobile = self._get_whatsapp_mobile()
        token, phone_number_id = self._get_whatsapp_credentials()

        buttons = buttons or []
        list_payload = list_payload or {}
        log_model = self.env["whatsapp.message.log"].sudo()

        # Send main message
        main_msg_id = None
        if message_mode == "template":
            if not template:
                raise UserError(_("Please select a template to send."))
            main_msg_id = self._send_whatsapp_template(
                mobile, token, phone_number_id, template, components=template_components
            )
        elif message_mode == "interactive_button":
            if not buttons:
                raise UserError(_("Please add at least one button."))
            main_msg_id = self._send_whatsapp_interactive_buttons(
                mobile, token, phone_number_id, message_body, buttons
            )
        elif message_mode == "interactive_list":
            if not list_payload.get("rows"):
                raise UserError(_("Please provide at least one list row."))
            main_msg_id = self._send_whatsapp_interactive_list(
                mobile, token, phone_number_id, message_body, list_payload
            )
        elif message_mode == "media_image":
            if not list_payload.get("media_url"):
                raise UserError(_("Please provide an image URL to send."))
            main_msg_id = self._send_whatsapp_image(mobile, token, phone_number_id, list_payload["media_url"], message_body)
        else:
            main_msg_id = self._send_whatsapp_text(mobile, token, phone_number_id, message_body)

        if main_msg_id:
            log_model.create(
                {
                    "message_id": main_msg_id,
                    "order_id": self.id,
                    "partner_id": self.partner_id.id,
                    "direction": "outbound",
                    "status": "sent",
                }
            )

        if include_sale_order_pdf:
            sale_pdf, sale_filename = self._render_sale_order_pdf()
            sale_msg_id = self._send_whatsapp_document(
                mobile,
                token,
                phone_number_id,
                sale_pdf,
                sale_filename,
                caption=_("Sales Order %(number)s") % {"number": self.name},
            )
            if sale_msg_id:
                log_model.create(
                    {
                        "message_id": sale_msg_id,
                        "order_id": self.id,
                        "partner_id": self.partner_id.id,
                        "direction": "outbound",
                        "status": "sent",
                    }
                )

        if include_invoice_pdf:
            invoices = self._get_invoice_candidates()
            if not invoices:
                raise UserError(_("No posted invoices are available for this order."))
            for invoice in invoices:
                invoice_pdf, invoice_filename = self._render_invoice_pdf(invoice)
                caption = _("Invoice %(number)s") % {"number": invoice.name or invoice.ref or ""}
                invoice_msg_id = self._send_whatsapp_document(
                    mobile,
                    token,
                    phone_number_id,
                    invoice_pdf,
                    invoice_filename,
                    caption=caption,
                )
                if invoice_msg_id:
                    log_model.create(
                        {
                            "message_id": invoice_msg_id,
                            "order_id": self.id,
                            "partner_id": self.partner_id.id,
                            "direction": "outbound",
                            "status": "sent",
                        }
                    )
