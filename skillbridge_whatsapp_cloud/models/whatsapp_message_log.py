from odoo import _, api, fields, models


class WhatsAppMessageLog(models.Model):
    _name = "whatsapp.message.log"
    _description = "WhatsApp Message Log"
    _order = "create_date desc"

    message_id = fields.Char(string="Message ID", required=True, index=True)
    order_id = fields.Many2one("sale.order", string="Sales Order", index=True, ondelete="cascade")
    partner_id = fields.Many2one("res.partner", string="Partner", index=True)
    campaign_id = fields.Many2one("whatsapp.campaign", string="Campaign", index=True)
    message_body = fields.Text(string="Message Body")
    message_type = fields.Char(string="Message Type")
    template_name = fields.Char(string="Template Name")
    direction = fields.Selection(
        [("outbound", "Outbound"), ("inbound", "Inbound")],
        string="Direction",
        required=True,
        default="outbound",
    )
    status = fields.Char(string="Status", index=True)
    error_code = fields.Char(string="Error Code")
    last_payload = fields.Text(string="Last Payload")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._update_conversations()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "status" in vals:
            self._update_conversation_status()
        return res

    def _conversation_summary(self):
        self.ensure_one()
        if self.message_body:
            return self.message_body
        if self.template_name:
            return _("Template: %s") % self.template_name
        if self.message_type:
            return f"[{self.message_type}]"
        return _("Message")

    def _update_conversations(self):
        Conversation = self.env["whatsapp.conversation"].sudo()
        for rec in self:
            if not rec.partner_id:
                continue
            conversation = Conversation.search([("partner_id", "=", rec.partner_id.id)], limit=1)
            if not conversation:
                conversation = Conversation.create({"partner_id": rec.partner_id.id})
            conversation.write(
                {
                    "last_message": rec._conversation_summary(),
                    "last_message_date": rec.create_date or fields.Datetime.now(),
                    "last_direction": rec.direction,
                    "last_status": rec.status,
                    "last_message_id": rec.id,
                }
            )

    def _update_conversation_status(self):
        Conversation = self.env["whatsapp.conversation"].sudo()
        for rec in self:
            if not rec.partner_id:
                continue
            conversation = Conversation.search([("partner_id", "=", rec.partner_id.id)], limit=1)
            if conversation and conversation.last_message_id.id == rec.id:
                conversation.write({"last_status": rec.status})
