import hashlib
import hmac
import json

from odoo.tests import TransactionCase

from ..controllers.whatsapp_webhook import WhatsAppWebhookController


class TestWebhookProcessing(TransactionCase):
    def setUp(self):
        super().setUp()
        self.controller = WhatsAppWebhookController()
        self.app_secret = "secret123"
        self.partner = self.env["res.partner"].create({"name": "Test Partner", "mobile": "+15551234567"})
        self.order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "partner_invoice_id": self.partner.id, "partner_shipping_id": self.partner.id}
        )

    def _signature(self, body_bytes):
        digest = hmac.new(self.app_secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
        return f"sha256={digest}"

    def test_inbound_message_logs_and_chatter(self):
        payload = {
            "entry": [
                {
                    "id": "entry1",
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "id": "wamid.inbound1",
                                        "from": "+15551234567",
                                        "type": "text",
                                        "text": {"body": "Hello"},
                                    }
                                ]
                            }
                        }
                    ],
                }
            ]
        }
        body_bytes = json.dumps(payload).encode("utf-8")
        sig = self._signature(body_bytes)

        # Inject configuration
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("skillbridge_whatsapp_cloud.app_secret", self.app_secret)
        params.set_param("skillbridge_whatsapp_cloud.webhook_verify_token", "token")

        # Patch request context: simulate headers/body
        class DummyRequest:
            def __init__(self, body, signature):
                self.method = "POST"
                self.headers = {"X-Hub-Signature-256": signature}
                self._body = body

            def get_data(self, cache=False, as_text=False):
                return self._body

        httpreq = DummyRequest(body_bytes, sig)
        self.env["ir.http"]._current_request = httpreq
        # Directly call the protected handler
        self.controller._handle_callback()

        # Validate log created
        log = self.env["whatsapp.message.log"].search([("message_id", "=", "wamid.inbound1")], limit=1)
        self.assertTrue(log, "Inbound message log should be created")
        self.assertEqual(log.partner_id, self.partner)
        self.assertEqual(log.order_id, self.order)
        self.assertEqual(log.direction, "inbound")

        # Validate chatter message on order
        messages = self.order.message_ids.filtered(lambda m: "WhatsApp" in (m.body or ""))
        self.assertTrue(messages, "Order should have a chatter message for inbound WhatsApp")

    def test_status_failure_updates_log_and_chatter(self):
        # Seed a sent log
        self.env["whatsapp.message.log"].create(
            {
                "message_id": "wamid.outbound1",
                "order_id": self.order.id,
                "partner_id": self.partner.id,
                "direction": "outbound",
                "status": "sent",
            }
        )

        payload = {
            "entry": [
                {
                    "id": "entry1",
                    "changes": [
                        {
                            "value": {
                                "statuses": [
                                    {
                                        "id": "wamid.outbound1",
                                        "status": "failed",
                                        "errors": [{"code": 470, "title": "Failed"}],
                                    }
                                ]
                            }
                        }
                    ],
                }
            ]
        }
        body_bytes = json.dumps(payload).encode("utf-8")
        sig = self._signature(body_bytes)

        params = self.env["ir.config_parameter"].sudo()
        params.set_param("skillbridge_whatsapp_cloud.app_secret", self.app_secret)
        params.set_param("skillbridge_whatsapp_cloud.webhook_verify_token", "token")

        class DummyRequest:
            def __init__(self, body, signature):
                self.method = "POST"
                self.headers = {"X-Hub-Signature-256": signature}
                self._body = body

            def get_data(self, cache=False, as_text=False):
                return self._body

        httpreq = DummyRequest(body_bytes, sig)
        self.env["ir.http"]._current_request = httpreq
        self.controller._handle_callback()

        log = self.env["whatsapp.message.log"].search([("message_id", "=", "wamid.outbound1")], limit=1)
        self.assertEqual(log.status, "failed")
        self.assertTrue(log.last_payload)

        messages = self.order.message_ids.filtered(lambda m: "failed" in (m.body or ""))
        self.assertTrue(messages, "Order should have a chatter message for failed WhatsApp delivery")
