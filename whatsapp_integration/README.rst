WhatsApp Cloud Messaging
========================

Send WhatsApp Business Cloud API messages from Odoo for sales, invoices, and campaigns with delivery tracking and opt-in compliance.

Compatibility
-------------

- Odoo 17.0 (this branch). Use a matching branch for other versions when publishing to the Odoo App Store.

Key Features
------------

- Message types: text, Meta-approved templates, images, interactive buttons/lists, and PDFs from Sales Orders/posted invoices.
- Campaigns: queues with throttling, drip steps, send windows, retries/backoff, and KPI dashboards.
- Compliance: E.164 phone validation, partner opt-in flags, per-company accounts, and webhook signature verification.
- Observability: message logs (sent/delivered/read/failed) with pivot, plus inbound payload trace.

Data & Privacy
--------------

- Sends partner mobile, template/text content, and optional PDFs to the WhatsApp Business Cloud API to deliver messages.
- Enforces opt-in (boolean flag) and E.164 validation before sending.
- No activation keys; data stays in your Odoo database unless you export it.

Requirements
------------

- WhatsApp Business Cloud API app.
- Permanent access token with ``whatsapp_business_messaging`` scope.
- Phone number ID from WhatsApp Manager (not the phone itself).
- Webhook verify token + app secret; partner mobiles in E.164 format with opt-in captured.

Installation & Configuration
----------------------------

1) Install the module from Apps (or copy to addons path and update list).  
2) Settings → WhatsApp Business API: set token, phone number ID, webhook verify token, app secret, and optional default media URL.  
3) Sales → WhatsApp → Accounts: create a **default** account per company (token + phone number ID).  
4) Approve templates in Meta; create the same templates in Odoo and set status to APPROVED.  
5) Demo data includes safe placeholder templates, partner, campaign, and non-default demo account under ``noupdate``.

Quickstart
----------

1) Create a partner with E.164 mobile (e.g., ``+12025550123``) and opt-in enabled.  
2) Open a Sales Order → click **Send WhatsApp** → pick text/template/image/interactive → Send.  
3) Campaigns: create campaign → add drip steps → **Generate Queue** → **Start**; cron batches sends and logs statuses.  
4) Review Logs and Pivot for sent/delivered/read/failed KPIs.

Repository for Odoo App Store
-----------------------------

When registering the addon, use the store format: ``ssh://git@github.com/<org>/<repo>.git#17.0`` (replace with your repo/branch).

Troubleshooting
---------------

- 401/403 from Meta: verify token scope ``whatsapp_business_messaging`` and that phone_number_id matches the WA Business number ID.  
- Invalid number: ensure E.164 formatting and partner opt-in checked.  
- Template rejected: status must be APPROVED and name/language must match Meta exactly.  
- Media send fails: Default Media URL must be https/http and publicly reachable.

Support
-------

- Email: support@eduskillbridge.net (responses within 1 business day).  
- WhatsApp: https://wa.me/966531505513  
- Onboarding and custom flows available from Skillbridge Studio.

License
-------

OPL-1
