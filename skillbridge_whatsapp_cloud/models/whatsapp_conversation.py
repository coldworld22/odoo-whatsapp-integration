import re

from odoo import _, fields, models
from odoo.exceptions import UserError

MOBILE_PATTERN = re.compile(r"^\+?[1-9]\d{6,14}$")


class WhatsAppConversation(models.Model):
    _name = "whatsapp.conversation"
    _description = "WhatsApp Conversation"
    _order = "last_message_date desc, id desc"

    partner_id = fields.Many2one("res.partner", string="Partner", required=True, index=True, ondelete="cascade")
    last_message = fields.Text(string="Last Message", readonly=True)
    last_message_date = fields.Datetime(string="Last Message Date", readonly=True)
    last_direction = fields.Selection(
        [("outbound", "Outbound"), ("inbound", "Inbound")], string="Last Direction", readonly=True
    )
    last_status = fields.Char(string="Last Status", readonly=True)
    last_message_id = fields.Many2one("whatsapp.message.log", string="Last Message Log", readonly=True)
    message_ids = fields.One2many("whatsapp.message.log", "conversation_id", string="Messages", readonly=True)

    def action_reply(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Reply via WhatsApp"),
            "res_model": "whatsapp.inbox.reply",
            "view_mode": "form",
            "target": "new",
            "context": {"default_conversation_id": self.id, "default_partner_id": self.partner_id.id},
        }

    def send_text_message(self, message_body):
        self.ensure_one()
        message = (message_body or "").strip()
        if not message:
            raise UserError(_("Please enter a message."))
        mobile = self._get_partner_mobile(self.partner_id)
        token, phone_number_id = self.env["sale.order"]._get_whatsapp_credentials()
        message_id = self.env["sale.order"]._send_whatsapp_text(mobile, token, phone_number_id, message)
        self.env["whatsapp.message.log"].sudo().create(
            {
                "message_id": message_id or "",
                "partner_id": self.partner_id.id,
                "direction": "outbound",
                "status": "sent",
                "message_body": message,
                "message_type": "text",
            }
        )
        return message_id

    @staticmethod
    def _get_partner_mobile(partner):
        mobile = (partner.mobile or partner.phone or "").strip()
        if not mobile:
            raise UserError(_("The customer mobile number is missing."))
        if not MOBILE_PATTERN.match(mobile):
            raise UserError(_("The customer mobile number must be in international format (E.164)."))
        if hasattr(partner, "whatsapp_opt_in") and not partner.whatsapp_opt_in:
            raise UserError(_("Customer has not opted in for WhatsApp messaging."))
        return mobile
