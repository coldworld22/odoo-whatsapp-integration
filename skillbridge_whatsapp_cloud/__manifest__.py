{
    "name": "WhatsApp Cloud Messaging — Skillbridge Studio",
    "summary": "Official WhatsApp Cloud API integration for Odoo — send orders, invoices, and campaigns.",
    "description": """
WhatsApp Cloud Messaging brings the official WhatsApp Business Cloud API to Odoo, enabling sales, accounting and marketing teams to send Meta-approved templates, attach PDFs, and run compliant campaigns with delivery/read tracking.

Key features:
- Send WhatsApp messages from Sales Orders and posted invoices (PDF attachments supported).
- Support for text, Meta templates, images, and interactive buttons/lists.
- Template sync with Meta (WABA) and template variable handling.
- Campaigns with queues, throttling, drip steps, and retry/backoff policies.
- Inbox and conversation history with opt-in handling and E.164 validation.
- Webhook verification, delivery/read/failure logs and pivot KPIs.

Setup highlights:
1) Configure WhatsApp Business API credentials in Settings (token, phone number ID, WABA ID, verify token, app secret).
2) Create a WhatsApp Account per company and approve templates in Meta.
3) Send manually from Sales Orders or automate with campaign queues and cron tasks.
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
        "static/description/cover.png",
        "static/description/cover.gif",
        "static/description/screenshots/dashboard.png",
        "static/description/screenshots/inbox.png",
        "static/description/screenshots/campaigns.png",
        "static/description/screenshots/templates.png",
        "static/description/screenshots/logs.png",
        "static/description/screenshots/analytics.png",
        "static/description/screen4.png",
        "static/description/screen6.png",
        "static/description/screen2.png",
        "static/description/screen5.png",
        "static/description/screen3.png",
        "static/description/contact.png",
        "static/description/screen1.png",
        "static/description/icon.png",
    ],
    "installable": True,
    "application": True,
    "post_init_hook": "post_init_hook",
}
