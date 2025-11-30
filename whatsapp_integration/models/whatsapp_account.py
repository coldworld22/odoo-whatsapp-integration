from odoo import fields, models


class WhatsAppAccount(models.Model):
    _name = "whatsapp.account"
    _description = "WhatsApp Account"

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True)
    phone_number_id = fields.Char(required=True, string="Phone Number ID")
    token = fields.Char(required=True, string="Access Token")
    is_default = fields.Boolean(default=False)
