from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    whatsapp_opt_in = fields.Boolean(string="WhatsApp Opt-In")
    whatsapp_opt_in_date = fields.Datetime(string="Opt-In Date")
    whatsapp_opt_in_source = fields.Char(string="Opt-In Source")
