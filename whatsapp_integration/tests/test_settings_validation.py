from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestSettingsValidation(TransactionCase):
    def test_rejects_non_numeric_phone_number_id(self):
        settings = self.env["res.config.settings"].create(
            {
                "whatsapp_phone_number_id": "ABC123",
                "whatsapp_token": "test",
            }
        )
        with self.assertRaises(UserError):
            settings.set_values()

    def test_rejects_invalid_default_media_url(self):
        settings = self.env["res.config.settings"].create(
            {
                "whatsapp_phone_number_id": "1234567890",
                "whatsapp_token": "test",
                "whatsapp_default_media_url": "ftp://invalid",
            }
        )
        with self.assertRaises(UserError):
            settings.set_values()

