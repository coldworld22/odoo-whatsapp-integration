from odoo import fields, models


class WhatsAppMessageLog(models.Model):
    _name = "whatsapp.message.log"
    _description = "WhatsApp Message Log"
    _order = "create_date desc"

    message_id = fields.Char(string="Message ID", required=True, index=True)
    order_id = fields.Many2one("sale.order", string="Sales Order", index=True, ondelete="cascade")
    partner_id = fields.Many2one("res.partner", string="Partner", index=True)
    campaign_id = fields.Many2one("whatsapp.campaign", string="Campaign", index=True)
    direction = fields.Selection(
        [("outbound", "Outbound"), ("inbound", "Inbound")],
        string="Direction",
        required=True,
        default="outbound",
    )
    status = fields.Char(string="Status")
    error_code = fields.Char(string="Error Code")
    last_payload = fields.Text(string="Last Payload")
