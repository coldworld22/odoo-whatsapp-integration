import re

from odoo import fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    whatsapp_token = fields.Char(
        string="WhatsApp Access Token",
        config_parameter="whatsapp_integration.token",
        help="Permanent Meta access token with whatsapp_business_messaging scope.",
    )
    whatsapp_phone_number_id = fields.Char(
        string="WhatsApp Phone Number ID",
        config_parameter="whatsapp_integration.phone_number_id",
        help="The WhatsApp phone number ID from Meta Business Manager (not the phone number itself).",
    )
    whatsapp_webhook_verify_token = fields.Char(
        string="Webhook Verify Token",
        config_parameter="whatsapp_integration.webhook_verify_token",
        help="Arbitrary string you configure on the Meta webhook setup screen to validate GET challenges.",
    )
    whatsapp_app_secret = fields.Char(
        string="App Secret",
        config_parameter="whatsapp_integration.app_secret",
        help="App secret used to validate X-Hub-Signature-256 on webhook callbacks.",
    )
    whatsapp_auto_send_on_confirm = fields.Boolean(
        string="Auto-send on Sales Order Confirmation",
        config_parameter="whatsapp_integration.auto_send_on_confirm",
    )
    whatsapp_auto_send_on_invoice_post = fields.Boolean(
        string="Auto-send on Invoice Post",
        config_parameter="whatsapp_integration.auto_send_on_invoice_post",
    )
    whatsapp_default_media_url = fields.Char(
        string="Default Media URL",
        config_parameter="whatsapp_integration.default_media_url",
        help="Fallback image URL for media sends or QR codes.",
    )

    def _check_settings(self):
        for rec in self:
            if rec.whatsapp_phone_number_id:
                phone_id = rec.whatsapp_phone_number_id.strip()
                if not re.fullmatch(r"[0-9]+", phone_id):
                    raise UserError("WhatsApp Phone Number ID must be numeric (Meta phone_number_id, not the phone itself).")
            if rec.whatsapp_default_media_url:
                url = rec.whatsapp_default_media_url.strip()
                if not re.match(r"^https?://", url):
                    raise UserError("Default Media URL must start with http:// or https://")

    def set_values(self):
        self._check_settings()
        return super().set_values()
