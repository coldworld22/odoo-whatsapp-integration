from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_token = fields.Char("WhatsApp Access Token", config_parameter="whatsapp_integration.token")
    whatsapp_phone_number_id = fields.Char("WhatsApp Phone Number ID", config_parameter="whatsapp_integration.phone_number_id")
