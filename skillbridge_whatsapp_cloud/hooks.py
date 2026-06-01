def post_init_hook(*args, **kwargs):
    """Compatibility wrapper for module post-init hooks across Odoo versions.

    Supports the following signatures used across Odoo releases:
    - post_init_hook(env)            # Odoo 17+ passes an Environment
    - post_init_hook(cr, registry)   # Older Odoo versions
    - post_init_hook(registry)       # Some hooks receive only registry
    """
    try:
        from odoo import SUPERUSER_ID, api
        from odoo.api import Environment
    except Exception:
        SUPERUSER_ID = None
        api = None
        Environment = None

    env = None
    created_cursor = False

    # Positional args handling
    if args:
        first = args[0]
        # If an Environment was passed directly (17+)
        if Environment is not None and isinstance(first, Environment):
            env = first
        elif api is not None:
            # If a registry was passed (has cursor method), open a cursor
            if hasattr(first, "cursor") and callable(first.cursor):
                cr = first.cursor()
                created_cursor = True
                env = api.Environment(cr, SUPERUSER_ID, {})
            else:
                # Assume a DB cursor was passed (older signature)
                cr = first
                env = api.Environment(cr, SUPERUSER_ID, {})

    # Keyword arg 'env' when called as post_init_hook(env=env)
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
