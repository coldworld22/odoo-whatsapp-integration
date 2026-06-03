WhatsApp Cloud Messaging
========================

Overview
--------

SkillBridge WhatsApp Cloud Messaging connects Odoo 19 with the official Meta WhatsApp Cloud API for sales, invoicing, inbox replies, templates, campaign queues, and message tracking.

Prerequisites
-------------

- A Meta Business account with WhatsApp Business Cloud API enabled.
- A permanent access token with ``whatsapp_business_messaging`` scope.
- ``whatsapp_business_management`` scope when syncing approved templates from Meta.
- Phone Number ID and WhatsApp Business Account ID from WhatsApp Manager.
- Webhook verify token, app secret, and customer phone numbers in E.164 format.

Configuration
-------------

1. Install the module from Apps.
2. Open Settings and configure the WhatsApp Business API credentials.
3. Create a default WhatsApp Account per company under Sales > WhatsApp > Accounts.
4. Approve templates in Meta, then sync or create matching templates in Odoo.
5. Capture partner opt-in before sending messages.

Usage
-----

- Sales Orders: use the Send WhatsApp button to send text, templates, images, buttons, lists, and optional PDFs.
- Invoices: send posted invoice PDFs through the linked Sales Order flow.
- Inbox: review customer conversations and reply from Odoo.
- Campaigns: generate queues, throttle batches, process drip steps, and review delivery results.
- Logs: audit outbound and inbound messages with delivery, read, and failure statuses.

Security Notes
--------------

- Tokens are stored in Odoo configuration parameters and account records.
- Webhook requests can be validated with the configured app secret.
- The module enforces opt-in and E.164 validation before outbound sends.
- Meta conversation and messaging fees are billed separately by Meta.

Support
-------

For setup help, contact ``support@eduskillbridge.net``.
