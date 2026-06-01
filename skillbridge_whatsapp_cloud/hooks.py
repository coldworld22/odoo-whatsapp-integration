from odoo import SUPERUSER_ID, api


def post_init_hook(*args):
    """Support both legacy `post_init_hook(cr, registry)` and newer
    `post_init_hook(registry)` signatures across Odoo versions.
    """
    # Determine provided arguments
    if len(args) == 2:
        cr, registry = args[0], args[1]
        created_cursor = False
    elif len(args) == 1:
        registry = args[0]
        # registry.cursor() returns a cursor we must close afterwards
        cr = registry.cursor()
        created_cursor = True
    else:
        raise TypeError("post_init_hook expects (cr, registry) or (registry)")

    try:
        env = api.Environment(cr, SUPERUSER_ID, {})
        logs = env["whatsapp.message.log"].sudo().search([("partner_id", "!=", False)])
        partner_ids = logs.mapped("partner_id").ids
        for partner_id in partner_ids:
            last_log = env["whatsapp.message.log"].sudo().search(
                [("partner_id", "=", partner_id)], order="create_date desc", limit=1
            )
            if last_log:
                last_log._update_conversations()
    finally:
        if created_cursor:
            cr.close()
