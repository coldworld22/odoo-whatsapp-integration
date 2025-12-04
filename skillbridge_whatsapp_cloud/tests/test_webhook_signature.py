import hashlib
import hmac

from odoo.tests import TransactionCase

from ..controllers.whatsapp_webhook import WhatsAppWebhookController


class TestWebhookSignature(TransactionCase):
    def setUp(self):
        super().setUp()
        self.controller = WhatsAppWebhookController()
        self.app_secret = "secret123"
        self.body = b'{"test": true}'

    def test_valid_signature(self):
        expected = hmac.new(self.app_secret.encode("utf-8"), self.body, hashlib.sha256).hexdigest()
        header = f"sha256={expected}"
        self.assertTrue(self.controller._is_valid_signature(self.app_secret, header, self.body))

    def test_invalid_signature(self):
        header = "sha256=badsignature"
        self.assertFalse(self.controller._is_valid_signature(self.app_secret, header, self.body))

    def test_missing_header(self):
        self.assertFalse(self.controller._is_valid_signature(self.app_secret, None, self.body))
