# WhatsApp Cloud Messaging
Send invoices, sales orders, and campaign messages through the WhatsApp Business Cloud API from Odoo.

## Compatibility
- Odoo 17.0 (this branch). Use matching branches for other versions when publishing to the Odoo App Store.

## Data & Privacy
- Sends partner mobile numbers, template/text content, and optional PDFs to the WhatsApp Business Cloud API to deliver messages.
- Enforces opt-in and E.164 validation before sending.
- No activation keys; data stays in your Odoo database unless you export it.

## Requirements
- WhatsApp Business Cloud API app.
- Permanent access token with `whatsapp_business_messaging` scope.
- Phone number ID from WhatsApp Manager (not the phone itself).
- Webhook verify token + app secret; customer mobiles in E.164 format with opt-in captured.

## Installation
1. Copy the `skillbridge_whatsapp_cloud` directory into your Odoo addons path (or install from Apps).
2. Update Apps List, search for **WhatsApp Cloud Messaging**, and install.

## Configuration
1. Settings → General Settings → WhatsApp Business API: set Access Token, Phone Number ID, Webhook Verify Token, App Secret, and optional Default Media URL.
2. Sales → WhatsApp → Accounts: create a **default** account per company with token + phone number ID.
3. Templates: create Meta-approved templates in Odoo and set status to APPROVED.

## Usage
- Sales Order: click **Send WhatsApp** → choose text/template/image/interactive → optionally attach Sales Order PDF and posted invoices.
- Campaigns: create campaign → add drip steps → **Generate Queue** → **Start**; cron batches sends and logs statuses.
- Logs: review sent/delivered/read/failed with pivot KPIs.

## Repository format for Odoo App Store
- Use `ssh://git@github.com/coldworld22/odoo-whatsapp-integration.git#17.0` when registering the addon (branch `17.0` is already pushed).

## Notes
- Ensure the Meta token is allowed to send from the configured phone_number_id.
- Phone numbers must include the country code (E.164 format) and be opted-in.
