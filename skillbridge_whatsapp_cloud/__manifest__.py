{
    "name": "WhatsApp Cloud Messaging - Skillbridge Studio",
    "summary": "WhatsApp Cloud API for Odoo: send orders, invoices, inbox replies, and campaigns.",
    "description": """
WhatsApp Business Cloud API integration for Odoo Sales and Accounting.

Key features:
- Send WhatsApp messages from Sales Orders and posted invoices (PDF attachments supported).
- Message modes: text, Meta templates, images, and interactive buttons/lists from Sales Orders.
- Template variables with compliance hints and keyword opt-in/out (STOP/START).
- Inbox: reply to inbound messages and view conversation history per customer.
- Sync templates from Meta (WABA) to keep names, statuses, and languages aligned.
- Bulk campaigns with queues, throttling, drip steps, retries/backoff, and KPI dashboards.
- Partner opt-in flags with E.164 validation and per-company WhatsApp accounts (no hard-coded tokens).
- Webhook verification with verify token + app secret and delivery/read/failure logs.

Setup:
1) Settings › WhatsApp Business API: token, phone number ID, Business Account ID (WABA ID), webhook verify token, app secret, default media URL.
2) Create a default WhatsApp Account record per company with token + phone number ID.
3) Approve templates in Meta and mark them APPROVED in Odoo; then send from Sales Orders or run campaigns.
""",
    "version": "17.0.1.1.6",
    "author": "Skillbridge Studio",
    "maintainer": "Skillbridge Studio",
    "support": "support@eduskillbridge.net",
    "license": "OPL-1",
    # Public project page for details and docs (17.0 branch)
    "website": "https://github.com/coldworld22/odoo-whatsapp-integration/tree/17.0",
    "category": "Sales",
    "price": 249.0,
    "currency": "USD",
    "external_dependencies": {"python": ["requests"]},
    "depends": ["base", "mail", "sale", "account"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        # Define the WhatsApp root menu before child menus reference it.
        "views/whatsapp_template_views.xml",
        "views/whatsapp_account_views.xml",
        "views/whatsapp_inbox_views.xml",
        "views/whatsapp_inbox_reply_views.xml",
        "views/whatsapp_wizard_views.xml",
        "views/whatsapp_buttons.xml",
        "views/whatsapp_log_views.xml",
        "views/whatsapp_log_views_pivot.xml",
        "views/whatsapp_campaign_views.xml",
        "views/res_partner_views.xml",
        "views/res_config_settings_view.xml",
        "data/cron.xml",
    ],
    "demo": ["data/demo.xml"],
    "images": [
        "static/description/cover-v2.png",
        "static/description/cover.gif",
        "static/description/screenshots/dashboard-v3.png",
        "static/description/screenshots/inbox-v3.png",
        "static/description/screenshots/campaigns.png",
        "static/description/screenshots/templates.png",
        "static/description/screenshots/logs.png",
        "static/description/screenshots/analytics.png",
        "static/description/screen4.png",
        "static/description/screen6.png",
        "static/description/screen2.png",
        "static/description/screen5.png",
        "static/description/screen4.png",
        "static/description/screen3.png",
        "static/description/screen7.png",
        "static/description/screen8.png",
        "static/description/screen9.png",
        "static/description/contact.png",
        "static/description/screen1.png",
        "static/description/icon.png",
    ],
    "installable": True,
    "application": True,
    "post_init_hook": "post_init_hook",
}
