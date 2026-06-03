from odoo import SUPERUSER_ID, api
from odoo.api import Environment


def post_init_hook(*args, **kwargs):
    """Compatibility wrapper for module post-init hooks across Odoo versions.

    Supports the following signatures used across Odoo releases:
    - post_init_hook(env)            # Odoo 17+ passes an Environment
    - post_init_hook(cr, registry)   # Older Odoo versions
    - post_init_hook(registry)       # Some hooks receive only registry
    """
    env = None
    created_cursor = False

    if args:
        first = args[0]
        if isinstance(first, Environment):
            env = first
        elif hasattr(first, "cursor") and callable(first.cursor):
            cr = first.cursor()
            created_cursor = True
            env = api.Environment(cr, SUPERUSER_ID, {})
        else:
            cr = first
            env = api.Environment(cr, SUPERUSER_ID, {})

    if env is None:
        env = kwargs.get("env")

    if env is None:
        return

    try:
        logs = env["whatsapp.message.log"].sudo().search([("partner_id", "!=", False)])
        partner_ids = logs.mapped("partner_id").ids
        for partner_id in partner_ids:
            last_log = env["whatsapp.message.log"].sudo().search(
                [("partner_id", "=", partner_id)], order="create_date desc", limit=1
            )
            if last_log:
                last_log._update_conversations()
    finally:
        if created_cursor and "cr" in locals():
            try:
                cr.close()
            except Exception:
                pass
