from odoo import models
import requests

class WhatsAppAPI(models.Model):
    _inherit = "sale.order"

    def action_send_whatsapp(self):
        """Send WhatsApp message using Meta Cloud API"""
        token = self.env["ir.config_parameter"].sudo().get_param("whatsapp_integration.token")
        phone_number_id = self.env["ir.config_parameter"].sudo().get_param("whatsapp_integration.phone_number_id")

        if not token or not phone_number_id:
            raise ValueError("WhatsApp API credentials not configured in Odoo Settings")

        url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": self.partner_id.mobile,
            "type": "text",
            "text": {"body": f"Hello {self.partner_id.name}, here is your order {self.name}"}
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise ValueError(f"WhatsApp API error: {response.text}")
        return True
