# WhatsApp Cloud Messaging
Official WhatsApp Business Cloud API integration for Odoo — send orders, invoices, and automated campaigns with compliance and observability.

Supported: Odoo 17 (this branch). Use corresponding branches for other Odoo versions.

Quick highlights
- Send Meta-approved templates, text, images and attach PDFs to Sales Orders and posted invoices.
- Campaigns with queues, throttling, drip steps, retries and KPI reporting.
- Inbox and threaded conversations with opt-in enforcement (E.164 validation) and keyword handling (STOP/START).

Requirements
- A WhatsApp Business Cloud app and a permanent access token with `whatsapp_business_messaging` scope.
- Phone Number ID and Business Account ID (WABA) for template sync.
- Webhook verify token and app secret configured in Odoo settings.

Installation
1. Place `skillbridge_whatsapp_cloud` into your Odoo addons path or install from Apps.
2. Update Apps List, search for "WhatsApp Cloud Messaging", and install.

Configuration
1. Go to Settings → WhatsApp Business API and set Access Token, Phone Number ID, WABA ID, Verify Token, and App Secret.
2. Create a WhatsApp Account per company under Sales → WhatsApp → Accounts.
3. Approve Meta templates and mark them APPROVED in Odoo for sending.

Usage
- Send from Sales Orders or run automated campaigns; review delivery/read statuses and logs in pivot views.
- Use the Inbox to reply to inbound messages and maintain conversation history per partner.

Repository for Odoo App Store
Use `ssh://git@github.com/coldworld22/odoo-whatsapp-integration.git#17.0` when registering the addon.

Notes
- Ensure the Meta token is permitted to send from the configured `phone_number_id` and that customer numbers are in E.164 format and opted-in.
