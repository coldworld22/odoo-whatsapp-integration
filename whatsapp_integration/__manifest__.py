{
    "name": "WhatsApp Business Integration",
    "summary": "Send invoices, sales orders, and custom messages via WhatsApp Business Cloud API",
    "version": "17.0.1.0.0",
    "author": "Your Company",
    "license": "LGPL-3",
    "website": "https://yourcompany.com",
    "depends": ["base", "mail", "sale"],
    "data": [
        "views/res_config_settings_view.xml",
        "views/whatsapp_buttons.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True,
    "application": True,
}
