## 17.0.1.1.6

- Rebuilt the Odoo Apps Store description as a complete professional landing page with valid scoped styling, premium hero, feature cards, screenshot gallery, workflow, comparison, FAQ, and support CTA.
- Aligned store metadata and documentation links with the Odoo 17 store branch.

## 17.0.1.0.1

- Switched to OPL-1 license for paid distribution; added support and troubleshooting docs.
- Added validation tests for settings (numeric phone_number_id, http(s) media URL).
- Added status decorations on queues/logs, action help, and click-to-chat/contact links.
- Added indexes on queues/logs/campaign state for better performance at scale.
- Masked tokens in settings/account views and enriched landing page content.

## 17.0.1.1.2

- Added WhatsApp Inbox with conversation list and reply wizard.
- Added Meta template sync (WABA) with sync button, daily cron, and sync metadata fields.
- Added WABA ID configuration for Settings/Accounts and updated docs.
- Stored message body/type/template on logs for better inbox context.

## 17.0.1.1.3

- Refreshed Odoo Apps store assets (cover.png + cover.gif) and description layout with scoped styles to prevent Odoo CSS collisions.
- Updated public listing text for clearer positioning, features, and compliance messaging.

## 18.0.1.1.5

- Fixed `post_init_hook` signature compatibility across Odoo 16 (cr, registry) and Odoo 17+ (env) to prevent installation crash.

## 17.0.1.1.5

- Revised Odoo Apps Store description page: premium hero, screenshot showcase, integrations, comparison, workflow and FAQ updates.
- Added high-quality screenshots and inline SVG badges/icons for a polished App Store listing.
- Accessibility improvements: ARIA attributes, descriptive captions and keyboard-friendly CTAs.
- Updated `__manifest__.py` images list and bumped module version for App Store readiness.
