def post_init_hook(*args, **kwargs):
    """Compatibility wrapper for Odoo init hooks.

    Odoo 17+ calls `post_init_hook(env)`.
    Odoo 16 and earlier call `post_init_hook(cr, registry)`.
    """
    # Lazy import to avoid issues when module is inspected outside Odoo
    try:
        from odoo import SUPERUSER_ID, api
        from odoo.api import Environment
    except Exception:
        SUPERUSER_ID = None
        api = None
        Environment = None

    env = None
    if args:
        first = args[0]
        if Environment is not None and isinstance(first, Environment):
            env = first
        elif api is not None:
            # Odoo <= 16 typically passes (cr, registry); we only need `cr` to
            # build an env. Prefer SUPERUSER to avoid ACL issues during setup.
            cr = args[0]
            env = api.Environment(cr, SUPERUSER_ID, {})

    if env is None:
        env = kwargs.get("env")

    if env is None:
        return

    logs = env["whatsapp.message.log"].sudo().search([("partner_id", "!=", False)])
    partner_ids = logs.mapped("partner_id").ids
    for partner_id in partner_ids:
        last_log = env["whatsapp.message.log"].sudo().search(
            [("partner_id", "=", partner_id)], order="create_date desc", limit=1
        )
        if last_log:
            last_log._update_conversations()
