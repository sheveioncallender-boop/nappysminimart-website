# Validation — 26 November 2026

## Passed locally

- Python syntax for all addon and test files.
- XML parsing, manifest dependencies/data/assets and bundled asset references.
- SCSS compilation with libsass; JavaScript syntax with Node.
- The Odoo 19 inheritance engine applied all five inherited views successfully: main layout, desktop header, mobile header, website settings and product form.
- Template call targets and referenced commerce/cache methods checked against Odoo 19 source commit `c58c4773d7d8172a2fb8d103bd4ae54d832aaa3d`.
- Source review of public catalogue queries: no privilege escalation; native website/company rules and eCommerce access guard retained from the La Rosa implementation.
- Confirmed no La Rosa contact details, arts/crafts content or asset references remain in the addon.
- Inspected the approved red-and-gold logo and bundled real grocery photos.

## Not run here

A full installation and the included Odoo HTTP tests have **not** run. The workspace denied the local socket required to start PostgreSQL. Browser rendering, installation/upgrade/uninstallation, payment, checkout and target-instance behaviour still require validation on the intended Odoo 19 instance or a test copy. Static validation is not a substitute for those checks.

## Target-instance acceptance

- Install on a test copy; confirm homepage, Shop, Departments, Our Community, Visit Us and `/contactus`.
- Check desktop and mobile layouts, especially 360px/390px widths: menu left, logo centre, cart right, no horizontal overflow, menus and cart remain usable.
- Check phone `tel:+18684888332` and WhatsApp `https://wa.me/18684888332`.
- Confirm exact address and hours, company currency, taxes and order fulfilment settings.
- Publish a test product with an image, category, price and intended stock settings; verify homepage and shop visibility/pricing. Unpublish it and check removal. Verify a restricted catalogue does not expose products to anonymous visitors.
- Add/remove an item from the cart, change quantity and walk through checkout without making a real payment.
- Edit page content and contact settings, upgrade the addon, and verify edits persist.
- Test uninstall/restore on a disposable copy only.
- Run `nappys_website` HTTP tests on a disposable database using the README command.
