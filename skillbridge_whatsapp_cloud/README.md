# WhatsApp Cloud Messaging
WhatsApp Cloud API for Odoo sales orders, invoices, and campaigns with templates, PDFs, and delivery tracking.

A premium enterprise-grade integration for Odoo 19 using the official Meta Cloud API. Includes inbox, campaign engine, template sync, PDF sharing and delivery/read analytics. See the App Store-ready screenshots in `static/description/`.

## Compatibility
- Odoo 19.0 (this branch). Use matching branches for other versions when publishing to the Odoo App Store.

## Data & Privacy
- Sends partner mobile numbers, template/text content, and optional PDFs to the WhatsApp Business Cloud API to deliver messages.
- Enforces opt-in and E.164 validation before sending.
- STOP/START keywords automatically update opt-in status on inbound messages.
- No activation keys; data stays in your Odoo database unless you export it.

## Requirements
- WhatsApp Business Cloud API app.
- Permanent access token with `whatsapp_business_messaging` scope.
- `whatsapp_business_management` scope if you want to sync templates.
- Phone number ID from WhatsApp Manager (not the phone itself).
- Business Account ID (WABA ID) for template sync.
- Webhook verify token + app secret; customer mobiles in E.164 format with opt-in captured.

## Installation
1. Copy the `skillbridge_whatsapp_cloud` directory into your Odoo addons path (or install from Apps).
2. Update Apps List, search for **WhatsApp Cloud Messaging**, and install.

## Preview & Test (local)
1. Ensure the module folder is on your Odoo `addons_path` and restart the Odoo server.
```bash
# copy module to addons path (example)
cp -r . /path/to/odoo/addons/skillbridge_whatsapp_cloud
# restart your Odoo service (example)
systemctl restart odoo
```
2. In Odoo: Update the Apps list, search for **WhatsApp Cloud Messaging** and install the module.
3. Configure Settings → WhatsApp Business API with your WABA credentials and webhook settings to test end-to-end messaging in a sandbox or production WABA.

## Screenshots
- `static/description/cover-v2.png`
- `static/description/screenshots/dashboard-v2.png`
- `static/description/screen5.png`
- `static/description/screen4.png`
- `static/description/screen3.png`
- `static/description/screen7.png`
- `static/description/screen8.png`
- `static/description/screen9.png`

## Configuration
1. Settings → General Settings → WhatsApp Business API: set Access Token, Phone Number ID, Business Account ID (WABA ID), Webhook Verify Token, App Secret, and optional Default Media URL.
2. Sales → WhatsApp → Accounts: create a **default** account per company with token + phone number ID.
3. Templates: create Meta-approved templates in Odoo and set status to APPROVED.

## Usage
- Sales Order: click **Send WhatsApp** → choose text/template/image/interactive → optionally attach Sales Order PDF and posted invoices.
- Campaigns: create campaign → add drip steps → **Generate Queue** → **Start**; cron batches sends and logs statuses.
- Logs: review sent/delivered/read/failed with pivot KPIs, plus inbound message history.
- Inbox: open **WhatsApp → Inbox** to reply and view conversation history per customer.
- Templates: use **Sync from Meta** to pull approved templates and statuses.
- A daily cron keeps templates synced when WABA credentials are configured.

## Repository format for Odoo App Store
- Use `ssh://git@github.com/coldworld22/odoo-whatsapp-integration.git#19.0` when registering the addon after the `19.0` branch is pushed.

## Notes
- Ensure the Meta token is allowed to send from the configured phone_number_id.
- Phone numbers must include the country code (E.164 format) and be opted-in.
