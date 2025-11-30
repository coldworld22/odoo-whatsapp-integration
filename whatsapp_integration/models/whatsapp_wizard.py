from odoo import _, fields, models
from odoo.exceptions import UserError


class WhatsAppSendWizard(models.TransientModel):
    _name = "whatsapp.send.wizard"
    _description = "Send WhatsApp Message"

    order_id = fields.Many2one("sale.order", string="Sales Order", required=True, readonly=True)
    message_mode = fields.Selection(
        [
            ("text", "Plain Text"),
            ("template", "Template"),
            ("interactive_button", "Interactive Buttons"),
            ("interactive_list", "Interactive List"),
            ("media_image", "Image"),
        ],
        string="Message Type",
        default="text",
        required=True,
    )
    template_id = fields.Many2one("whatsapp.template", string="Template")
    template_body_preview = fields.Text(related="template_id.body_preview", readonly=True)
    template_compliance_hint = fields.Text(related="template_id.compliance_hint", readonly=True)
    template_var_1 = fields.Char(string="Variable 1")
    template_var_2 = fields.Char(string="Variable 2")
    template_var_3 = fields.Char(string="Variable 3")
    template_var_4 = fields.Char(string="Variable 4")
    template_var_5 = fields.Char(string="Variable 5")
    message_body = fields.Text(string="Message")
    include_sale_order_pdf = fields.Boolean(string="Attach Sales Order PDF", default=True)
    include_invoice_pdf = fields.Boolean(string="Attach Posted Invoices", default=False)
    button_1 = fields.Char(string="Button 1 Title")
    button_2 = fields.Char(string="Button 2 Title")
    button_3 = fields.Char(string="Button 3 Title")
    list_title = fields.Char(string="List Title")
    list_button_label = fields.Char(string="List Button Label")
    list_section_title = fields.Char(string="List Section Title")
    list_row_1_title = fields.Char(string="Row 1 Title")
    list_row_1_description = fields.Char(string="Row 1 Description")
    list_row_2_title = fields.Char(string="Row 2 Title")
    list_row_2_description = fields.Char(string="Row 2 Description")
    list_row_3_title = fields.Char(string="Row 3 Title")
    list_row_3_description = fields.Char(string="Row 3 Description")
    media_url = fields.Char(string="Image URL")

    def action_send(self):
        self.ensure_one()
        order = self.order_id
        if not order:
            raise UserError(_("No sales order selected."))

        message = (self.message_body or "").strip() or order._get_default_whatsapp_message()
        self._validate_interactive_constraints()
        order._send_whatsapp_payloads(
            message_body=message,
            message_mode=self.message_mode,
            template=self.template_id,
            template_components=self._collect_template_components(),
            buttons=self._collect_buttons(),
            list_payload=self._collect_list_payload(),
            include_sale_order_pdf=self.include_sale_order_pdf,
            include_invoice_pdf=self.include_invoice_pdf,
        )
        return {"type": "ir.actions.act_window_close"}

    def _collect_buttons(self):
        return [b for b in [self.button_1, self.button_2, self.button_3] if b]

    def _collect_list_payload(self):
        rows = []
        for idx, (title, desc) in enumerate(
            [
                (self.list_row_1_title, self.list_row_1_description),
                (self.list_row_2_title, self.list_row_2_description),
                (self.list_row_3_title, self.list_row_3_description),
            ],
            start=1,
        ):
            if title:
                rows.append(
                    {
                        "id": f"row_{idx}",
                        "title": title,
                        "description": desc or "",
                    }
                )
        if not rows:
            return {}
        return {
            "title": self.list_title or _("Options"),
            "button": self.list_button_label or _("Choose"),
            "section_title": self.list_section_title or _("Select an option"),
            "rows": rows,
            "media_url": self.media_url or "",
        }

    def _collect_template_components(self):
        if self.message_mode != "template":
            return []
        values = [v for v in [self.template_var_1, self.template_var_2, self.template_var_3, self.template_var_4, self.template_var_5] if v]
        expected = self.template_id.expected_variables
        if expected and len(values) < expected:
            raise UserError(_("Template expects %s variables; please fill them.") % expected)
        if values:
            return [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": val} for val in values],
                }
            ]
        return []

    def _validate_interactive_constraints(self):
        """Enforce simple WhatsApp limits: button titles <=20 chars, list row titles <=24."""
        if self.message_mode == "interactive_button":
            buttons = self._collect_buttons()
            if not buttons:
                raise UserError(_("Please add at least one button."))
            if len(buttons) > 3:
                raise UserError(_("You can add up to 3 buttons."))
            for title in buttons:
                if len(title) > 20:
                    raise UserError(_("Button titles must be 20 characters or fewer."))
        elif self.message_mode == "interactive_list":
            rows = self._collect_list_payload().get("rows", [])
            if not rows:
                raise UserError(_("Please provide at least one list row."))
            if len(rows) > 3:
                raise UserError(_("You can add up to 3 list rows in this dialog."))
            for row in rows:
                if len(row["title"]) > 24:
                    raise UserError(_("List row titles must be 24 characters or fewer."))
                if len(row.get("description", "")) > 72:
                    raise UserError(_("List row descriptions must be 72 characters or fewer."))
        elif self.message_mode == "media_image":
            if not self.media_url:
                raise UserError(_("Please provide an image URL to send."))
