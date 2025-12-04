## FAQ

**Where do I get the token and phone number ID?**  
From Meta Business Manager: WhatsApp -> API Setup -> "Temporary/Primary Token" and "Phone number ID" fields.

**Why do I get an authentication error?**  
Tokens expire if temporary. Create a permanent token and ensure it matches the app that owns the phone number ID.

**Messages fail for some customers.**  
Make sure `partner_id.mobile` is set and formatted with country code (E.164). Opt-in may be required depending on your template usage.

**Invoice PDF is not sent.**  
Only posted customer invoices/credit notes linked to the sales order are sent. Ensure at least one invoice is posted.

**Can I use this in a sandbox?**  
Yes, but numbers that are not in the test phone list may be rate-limited or blocked by Meta.

**Where are credentials stored?**  
In Odoo system parameters: `skillbridge_whatsapp_cloud.token` and `skillbridge_whatsapp_cloud.phone_number_id`.
