{
    "name": "WhatsApp Cloud Messaging",
    "summary": "Send invoices, sales orders, and custom messages via WhatsApp Business Cloud API",
    "description": """
WhatsApp Business integration for Odoo:
- Send WhatsApp messages from Sales Orders.
- Attach Sales Order PDFs and posted invoices.
- Configure token and phone number ID in settings with validation.
""",
    "version": "17.0.1.0.0",
    "author": "Your Company",
    "maintainer": "Your Company",
    "support": "support@yourcompany.com",
    "license": "LGPL-3",
    "website": "https://yourcompany.com",
    "category": "Sales",
    "depends": ["base", "mail", "sale", "account"],
    "data": [
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
    "demo": ["data/demo.xml"],
    "images": [
        "static/description/icon.png",
        "static/description/cover.png",
        "static/description/screenshots.png",
    ],
    "installable": True,
    "application": True,
}
