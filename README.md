# WhatsApp Cloud Messaging for Odoo 17 and 18

This repository hosts the `skillbridge_whatsapp_cloud` addon for Odoo 17 and 18, enabling WhatsApp Business Cloud messaging from Sales Orders and campaigns with opt-in compliance, delivery/read tracking, and webhook validation.

## Branches
- `17.0` (default for the store): contains only the `skillbridge_whatsapp_cloud` module.
- `main`: kept for history; use `17.0` for installs and submissions.

## Quick links
- Module path: [`skillbridge_whatsapp_cloud/`](./skillbridge_whatsapp_cloud)
- Store-ready branch: https://github.com/coldworld22/odoo-whatsapp-integration/tree/17.0
- Odoo Apps listings checked and available:
  - Odoo 18: https://apps.odoo.com/apps/modules/18.0/skillbridge_whatsapp_cloud
  - Odoo 17: https://apps.odoo.com/apps/modules/17.0/skillbridge_whatsapp_cloud
- Requirements: WhatsApp Business Cloud API app, permanent token (whatsapp_business_messaging), phone_number_id, webhook verify token, app secret.

## Install
Copy `skillbridge_whatsapp_cloud` into your addons path (or install from Odoo Apps after publishing), update Apps list, and configure tokens/phone_number_id under Settings → WhatsApp Business API.
