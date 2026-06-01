from odoo import fields, models


class WhatsAppCampaignQueue(models.Model):
    _name = "whatsapp.campaign.queue"
    _description = "WhatsApp Campaign Queue"
    _order = "id asc"

    campaign_id = fields.Many2one("whatsapp.campaign", required=True, ondelete="cascade", index=True)
    partner_id = fields.Many2one("res.partner", required=True, index=True)
    status = fields.Selection(
        [("pending", "Pending"), ("sent", "Sent"), ("failed", "Failed")],
        default="pending",
        required=True,
        index=True,
    )
    attempts = fields.Integer(default=0)
    message_id = fields.Char()
    last_error = fields.Text()
    next_attempt_at = fields.Datetime(string="Next Attempt", default=fields.Datetime.now, index=True)
    step_id = fields.Many2one("whatsapp.campaign.step", string="Current Step")
