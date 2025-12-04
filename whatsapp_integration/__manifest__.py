{
    "name": "WhatsApp Cloud Messaging",
    "summary": "Send invoices, sales orders, and custom messages via WhatsApp Business Cloud API",
    "description": """
WhatsApp Business Cloud integration for Odoo Sales and Accounting.

Key features:
- Send WhatsApp messages from Sales Orders and posted invoices (PDF attachments supported).
- Message modes: text, Meta templates, images; template variables with compliance hints.
- Bulk campaigns with queues, throttling, drip steps, retries/backoff, and KPI dashboards.
- Partner opt-in flags with E.164 validation; per-company WhatsApp accounts (no hard-coded tokens).
- Webhook verification with verify token + app secret and delivery/read/failure logs.

Setup:
1) Settings › WhatsApp Business API: token, phone number ID, webhook verify token, app secret, default media URL.
2) Create a default WhatsApp Account record per company with token + phone number ID.
3) Approve templates in Meta and mark them APPROVED in Odoo; then send from Sales Orders or run campaigns.
""",
    "version": "17.0.1.0.1",
    "author": "Skillbridge Studio",
    "maintainer": "Skillbridge Studio",
    "support": "support@eduskillbridge.net",
    "license": "OPL-1",
    # Public project page for details and docs (17.0 branch)
    "website": "https://github.com/coldworld22/odoo-whatsapp-integration/tree/17.0",
    "category": "Sales",
    "price": 400.0,
    "currency": "USD",
    "external_dependencies": {"python": ["requests"]},
    "depends": ["base", "mail", "sale", "account"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_view.xml",
        "views/whatsapp_wizard_views.xml",
        "views/whatsapp_buttons.xml",
        "views/whatsapp_template_views.xml",
        "views/whatsapp_log_views.xml",
        "views/whatsapp_log_views_pivot.xml",
        "views/whatsapp_campaign_views.xml",
        "views/whatsapp_account_views.xml",
        "views/res_partner_views.xml",
        "data/cron.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "whatsapp_integration/static/src/scss/demo_brand.scss",
            "whatsapp_integration/static/src/scss/demo_hide_apps.scss",
            "whatsapp_integration/static/src/js/demo_hide_apps.js",
        ],
    },
    "demo": ["data/demo.xml"],
    "images": [
        "static/description/icon.png",
        "static/description/cover.png",
        "static/description/contact.png",
        "static/description/sale.png",
        "static/description/whatsapp.png",
    ],
    "installable": True,
    "application": True,
}
