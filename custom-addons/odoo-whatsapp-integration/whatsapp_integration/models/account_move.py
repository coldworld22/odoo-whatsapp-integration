import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super().action_post()
        auto_send = (
            self.env["ir.config_parameter"].sudo().get_param("whatsapp_integration.auto_send_on_invoice_post")
            == "True"
        )
        if auto_send:
            outbound_moves = self.filtered(lambda m: m.move_type in ("out_invoice", "out_refund"))
            for move in outbound_moves:
                orders = move.line_ids.mapped("sale_line_ids.order_id")
                for order in orders:
                    try:
                        order._send_whatsapp_payloads(
                            message_body=order._get_default_whatsapp_message(),
                            message_mode="text",
                            include_sale_order_pdf=True,
                            include_invoice_pdf=True,
                        )
                    except Exception as exc:
                        _logger.warning("Auto WhatsApp send on invoice post failed for %s: %s", move.name, exc)
        return res
