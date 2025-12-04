from odoo import fields, models


class WhatsAppTemplate(models.Model):
    _name = "whatsapp.template"
    _description = "WhatsApp Template"
    _order = "name"

    name = fields.Char(string="Label", required=True)
    template_name = fields.Char(string="Template Name (Meta)", required=True, help="Exact template name from Meta.")
    language_code = fields.Char(string="Language Code", default="en_US", help="Template language code (e.g., en_US).")
    category = fields.Selection(
        [
            ("MARKETING", "Marketing"),
            ("UTILITY", "Utility"),
            ("AUTHENTICATION", "Authentication"),
        ],
        string="Category",
        default="UTILITY",
    )
    status = fields.Selection(
        [
            ("DRAFT", "Draft"),
            ("SUBMITTED", "Submitted"),
            ("APPROVED", "Approved"),
            ("REJECTED", "Rejected"),
        ],
        string="Status",
        default="DRAFT",
    )
    body_preview = fields.Text(string="Body Preview")
    remark = fields.Text(string="Notes")
    placeholders = fields.Text(
        string="Variables",
        help="Document the variable slots used by this template (e.g., {{1}} = customer name).",
    )
    compliance_hint = fields.Text(
        string="Compliance Hint",
        help="Per-country compliance notes (e.g., opt-in wording or sender ID rules).",
    )
    expected_variables = fields.Integer(
        string="Expected Variables",
        help="Number of variable placeholders required by this template ({{1}}, {{2}}, ...).",
    )

    def action_submit(self):
        self.write({"status": "SUBMITTED"})

    def action_mark_approved(self):
        self.write({"status": "APPROVED"})

    def action_mark_rejected(self):
        self.write({"status": "REJECTED"})
