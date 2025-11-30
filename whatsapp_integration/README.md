# WhatsApp Cloud Messaging
Send invoices, sales orders, and custom messages through the WhatsApp Business Cloud API from Odoo.

## Requirements
- Odoo 15.0+ (tested on 15/16/17)
- WhatsApp Business Cloud API credentials: permanent access token and phone number ID

## Installation
1. Copy the `whatsapp_integration` directory into your Odoo addons path.
2. In Odoo, go to Apps -> Update Apps List, then search for "WhatsApp Cloud Messaging" and install it.

## Configuration
1. Navigate to Settings -> General Settings -> WhatsApp Business API.
2. Enter your Access Token, Phone Number ID, Webhook Verify Token, and App Secret from Meta (the settings page includes short hints).
3. Save and reload the page to ensure parameters are stored.

## Usage
- Open a sales order with a partner that has a mobile number and click "Send WhatsApp" in the header.
- In the popup, edit the message if needed and choose whether to attach the Sales Order PDF and any posted invoices.
- The module will call the Meta Cloud endpoint using your configured token and phone number ID.

## Notes
- Ensure your Meta Cloud API token has permission to send messages from the configured phone number ID.
- Outgoing phone numbers must include the country code (E.164 format).
