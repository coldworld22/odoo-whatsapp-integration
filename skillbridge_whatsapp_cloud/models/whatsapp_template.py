import logging
import re

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WhatsAppTemplate(models.Model):
    _name = "whatsapp.template"
    _description = "WhatsApp Template"
    _order = "name"

    name = fields.Char(string="Label", required=True)
    template_name = fields.Char(string="Template Name (Meta)", required=True, help="Exact template name from Meta.")
    language_code = fields.Char(string="Language Code", default="en_US", help="Template language code (e.g., en_US).")
    meta_template_id = fields.Char(string="Meta Template ID")
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
    last_synced_at = fields.Datetime(string="Last Synced At", readonly=True)

    def action_sync_from_meta(self):
        total_created, total_updated = self._sync_from_meta()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Template sync complete"),
                "message": _("Created: %(created)s, Updated: %(updated)s")
                % {"created": total_created, "updated": total_updated},
                "sticky": False,
            },
        }

    def _cron_sync_from_meta(self):
        try:
            self.sudo()._sync_from_meta()
        except Exception as exc:
            _logger.warning("WhatsApp template cron sync failed: %s", exc)
        return True

    def _sync_from_meta(self):
        token, business_account_id = self._get_sync_credentials()
        url = f"https://graph.facebook.com/v20.0/{business_account_id}/message_templates"
        params = {
            "fields": "id,name,language,category,status,components,quality_score",
            "limit": 200,
        }
        total_created = 0
        total_updated = 0
        headers = {"Authorization": f"Bearer {token}"}
        while url:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            if not response.ok:
                raise UserError(_("Template sync failed (%s): %s") % (response.status_code, response.text))
            payload = response.json()
            for item in payload.get("data", []):
                template_name = item.get("name")
                if not template_name:
                    continue
                language_code = item.get("language") or "en_US"
                status = (item.get("status") or "").upper()
                category = (item.get("category") or "").upper()
                meta_template_id = item.get("id") or ""
                body_preview, expected_vars, placeholders = self._parse_components(item.get("components") or [])
                mapped_status = self._map_status(status)
                vals = {
                    "template_name": template_name,
                    "language_code": language_code,
                    "status": mapped_status,
                    "meta_template_id": meta_template_id,
                    "last_synced_at": fields.Datetime.now(),
                }
                if category in dict(self._fields["category"].selection):
                    vals["category"] = category
                if body_preview:
                    vals["body_preview"] = body_preview
                if expected_vars:
                    vals["expected_variables"] = expected_vars
                if placeholders:
                    vals["placeholders"] = placeholders

                existing = self.search(
                    [("template_name", "=", template_name), ("language_code", "=", language_code)], limit=1
                )
                if existing:
                    if existing.placeholders:
                        vals.pop("placeholders", None)
                    if existing.name:
                        vals["name"] = existing.name
                    else:
                        vals["name"] = template_name
                    existing.write(vals)
                    total_updated += 1
                else:
                    vals["name"] = template_name
                    self.create(vals)
                    total_created += 1
            url = (payload.get("paging") or {}).get("next")
            params = None
        return total_created, total_updated

    def _get_sync_credentials(self):
        company = self.env.company
        account = (
            self.env["whatsapp.account"]
            .sudo()
            .search([("company_id", "=", company.id), ("is_default", "=", True)], limit=1)
        )
        token = account.token if account else False
        business_account_id = account.business_account_id if account else False
        params = self.env["ir.config_parameter"].sudo()
        token = token or params.get_param("skillbridge_whatsapp_cloud.token")
        business_account_id = business_account_id or params.get_param("skillbridge_whatsapp_cloud.business_account_id")
        if not token or not business_account_id:
            raise UserError(
                _(
                    "Missing WhatsApp credentials. Set Access Token and Business Account ID (WABA ID) in Settings "
                    "or on the default WhatsApp Account."
                )
            )
        return token, business_account_id

    @staticmethod
    def _map_status(status):
        if status in ("APPROVED", "REJECTED"):
            return status
        if status in ("PENDING", "SUBMITTED", "IN_APPEAL"):
            return "SUBMITTED"
        return "DRAFT"

    @staticmethod
    def _parse_components(components):
        body_preview = ""
        expected_vars = 0
        placeholders = ""
        for comp in components or []:
            if comp.get("type") == "BODY":
                body_preview = comp.get("text") or ""
                numbers = [int(n) for n in re.findall(r"{{\s*(\d+)\s*}}", body_preview)]
                if numbers:
                    expected_vars = max(numbers)
                    placeholders = ", ".join([f"{{{{{n}}}}}" for n in sorted(set(numbers))])
                break
        return body_preview, expected_vars, placeholders

    def action_submit(self):
        self.write({"status": "SUBMITTED"})

    def action_mark_approved(self):
        self.write({"status": "APPROVED"})

    def action_mark_rejected(self):
        self.write({"status": "REJECTED"})
