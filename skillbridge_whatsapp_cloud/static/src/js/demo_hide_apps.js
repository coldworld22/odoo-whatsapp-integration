/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";
import { session } from "@web/session";

const visibleMenuXmlids = new Set([
    "sale.sale_menu_root",
    "skillbridge_whatsapp_cloud.menu_whatsapp_template_root",
]);

function applyDemoNavigation() {
    document.querySelectorAll(".o_menu_sections [data-menu-xmlid]").forEach((element) => {
        const xmlid = element.getAttribute("data-menu-xmlid");
        if (!visibleMenuXmlids.has(xmlid)) {
            element.style.display = "none";
        }
    });
    document.documentElement.classList.add("o_whatsapp_demo");
}

jsonrpc("/web/dataset/call_kw/res.users/has_group", {
    model: "res.users",
    method: "has_group",
    args: ["skillbridge_whatsapp_cloud.group_whatsapp_demo_user"],
    kwargs: { context: session.user_context || {} },
})
    .then((hasGroup) => {
        if (!hasGroup || !session.uid) {
            return;
        }
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", applyDemoNavigation, { once: true });
        } else {
            applyDemoNavigation();
        }
    })
    .catch(() => {});
