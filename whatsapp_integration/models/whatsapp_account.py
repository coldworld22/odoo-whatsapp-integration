from odoo import fields, models


class WhatsAppAccount(models.Model):
    _name = "whatsapp.account"
    _description = "WhatsApp Account"

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True)
    phone_number_id = fields.Char(
        required=True,
        string="Phone Number ID",
        help="Meta phone_number_id for this company (numeric ID from WhatsApp Manager).",
    )
    token = fields.Char(
        required=True,
        string="Access Token",
        help="Permanent access token with whatsapp_business_messaging scope.",
    )
    is_default = fields.Boolean(
        default=False,
        help="If enabled, this account is used by default for the company when sending messages.",
    )
