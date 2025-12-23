from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    logs = env["whatsapp.message.log"].sudo().search([("partner_id", "!=", False)])
    partner_ids = logs.mapped("partner_id").ids
    for partner_id in partner_ids:
        last_log = env["whatsapp.message.log"].sudo().search(
            [("partner_id", "=", partner_id)], order="create_date desc", limit=1
        )
        if last_log:
            last_log._update_conversations()
