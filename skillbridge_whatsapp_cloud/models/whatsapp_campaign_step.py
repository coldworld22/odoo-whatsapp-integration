from odoo import fields, models


class WhatsAppCampaignStep(models.Model):
    _name = "whatsapp.campaign.step"
    _description = "WhatsApp Campaign Step"
    _order = "sequence asc, id asc"

    campaign_id = fields.Many2one("whatsapp.campaign", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    delay_hours = fields.Float(string="Delay (hours)", default=24.0, help="Delay after previous step is sent.")
    message_mode = fields.Selection(
        [("text", "Plain Text"), ("template", "Template"), ("media_image", "Image")],
        default="text",
        required=True,
    )
    template_id = fields.Many2one("whatsapp.template")
    message_body = fields.Text(string="Message/Caption")
    media_url = fields.Char(string="Image URL")
