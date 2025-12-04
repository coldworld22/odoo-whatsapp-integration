## Setup Guide

### Prerequisites
- Odoo 15+ running and accessible (tested on 15/16/17).
- Meta WhatsApp Business Cloud API account with:
  - A phone number ID (from WhatsApp Manager -> Phone numbers).
  - A permanent access token with `whatsapp_business_messaging` scope.

### Install the module
1. Copy `skillbridge_whatsapp_cloud` into your Odoo addons path (or add the repo path to `addons_path` in `odoo.conf`).
2. Restart Odoo and update the Apps list.
3. Install "WhatsApp Cloud Messaging" from Apps.

### Configure credentials in Odoo
1. Go to Settings -> General Settings -> WhatsApp Business API.
2. Enter the Access Token, Phone Number ID, Webhook Verify Token, and App Secret you got from Meta.
3. Save. Odoo stores these values in system parameters:
   - `skillbridge_whatsapp_cloud.token`
   - `skillbridge_whatsapp_cloud.phone_number_id`
   - `skillbridge_whatsapp_cloud.webhook_verify_token`
   - `skillbridge_whatsapp_cloud.app_secret`

### Verify connectivity (optional)
- Create a sales order with a customer that has a valid mobile number in E.164 format (e.g., `+12025550123`).
- Click "Send WhatsApp" in the header, adjust the message, and choose whether to attach the Sales Order PDF and posted invoices. If credentials are correct, the API should respond with 200.

### Common pitfalls
- Using a temporary token that expires; switch to a permanent access token in Meta for production.
- Missing country code in the customer mobile number.
- Phone number ID and token taken from different Meta apps/projects.
