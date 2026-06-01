from odoo import fields, models


class WhatsAppInboxReply(models.TransientModel):
    _name = "whatsapp.inbox.reply"
    _description = "WhatsApp Inbox Reply"

    conversation_id = fields.Many2one("whatsapp.conversation", string="Conversation", required=True)
    partner_id = fields.Many2one(related="conversation_id.partner_id", string="Partner", readonly=True)
    message_body = fields.Text(string="Message", required=True)

    def action_send(self):
        self.ensure_one()
        self.conversation_id.send_text_message(self.message_body)
        return {"type": "ir.actions.act_window_close"}
