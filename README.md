# Nappy’s Minimart — Odoo 19 Community Website

A red-and-gold community minimart storefront for La Romaine, Trinidad and Tobago, developed by Spxcorp Limited. Reuses the native Odoo commerce architecture from the La Rosa project, with original Nappy’s content, layout, assets and branding.

- **Addon:** `nappys_website`
- **Apps title:** Nappy’s Minimart — Website & Shop
- **Version:** `19.0.1.0.0`
- **Branch:** `main`
- **Required Odoo addon:** `website_sale` (Website/eCommerce and its standard dependencies)
- **Phone / WhatsApp:** +1 868 488-8332 / 18684888332

## Included

- Homepage, departments, community story and visit/contact pages.
- Approved Nappy’s red-and-gold logo, local Manrope font and bundled real stock photography.
- Native Odoo navigation, product search, account, cart and checkout. The mobile header places the menu button left, logo centre and cart right.
- Sticky header, responsive layouts, gentle scroll reveals with reduced-motion support, and a WhatsApp button on the right.
- Homepage product cards use published, active, saleable products for the current website. Pricing uses Odoo’s visitor/pricelist/tax logic; restricted catalogues are respected without `sudo()`.
- An optional **Feature on Nappy’s Minimart homepage** checkbox on products gives selected products priority.
- Eight editable website categories: Pantry Essentials; Drinks & Beverages; Snacks & Confectionery; Chilled & Dairy; Frozen Foods; Household & Cleaning; Personal Care; Baby Essentials.
- Website settings for contact number, WhatsApp, address, opening hours and storefront branding.
- Red Community backend navigation and primary buttons. Standard success/warning/error colours keep their normal meanings.
- Footer credit: Developed by Spxcorp Limited.

No sample inventory, prices, stock quantities, taxes, sales or payments are created. Empty product sections stay hidden; department links fall back to the native shop until their categories are visible. Website categories are separate from POS and internal inventory categories.

## CloudPepper installation

1. Connect `https://github.com/sheveioncallender-boop/nappysminimart-website` using branch `main` in the Odoo 19 Community environment.
2. Pull/deploy the source and restart the Odoo service as required by that environment. The repository root is the custom addons directory; it contains `nappys_website/` directly.
3. In Odoo, enable developer mode and run **Apps → Update Apps List**.
4. Search for **Nappy’s Minimart** and install **Nappy’s Minimart — Website & Shop**. Clear the Apps filter and search `nappys_website` if needed.
5. Open the Website application. The install hook brands the default website and sets `/nappys-home` as its homepage.
6. Check **Website → Configuration → Settings → Nappy’s Minimart**. Phone and WhatsApp are populated. Address is currently **La Romaine, Trinidad and Tobago**; confirm the full street address and opening hours before advertising precise directions.
7. Add and publish products through normal Odoo product management. Assign their eCommerce categories and images. Confirm company currency, pricelists, taxes, checkout, payment providers and delivery/pickup settings before taking orders.

Use the normal Odoo Website editor to edit page text and photos. The initial page/category records use `noupdate`; module upgrades preserve those records and contact settings. Future source changes to existing editable page records require an intentional migration or editor update.

For subsequent code changes, pull/redeploy, restart and **Upgrade** this addon. Odoo recompiles versioned assets; shoppers should not need to manually clear browser caches.

## Scope and behaviour

Installation changes the **default website** name, logo and homepage; it snapshots the previous values and reused menu entries. Uninstallation attempts to restore the original values where they still match the installed branding, preserving later user changes. Backend colours apply across this database while installed, including other companies/websites. The website branding toggle only controls storefront branding.

The map currently shows the La Romaine area. This is not a verified store pin. The contact page directs first-time visitors to call or message for exact directions.

This is the website module phase. POS, receipt branding/QR settings, inventory tracking, company/accounting settings and store setup are handled separately on the target Odoo instance. Installing this addon does not configure a payment gateway or turn on delivery services.

## Validation

See [VALIDATION.md](VALIDATION.md) for actual checks and their limits.

```sh
python scripts/validate_module.py
# Optional, with Odoo 19 Python dependencies installed:
python scripts/check_odoo19.py /path/to/odoo
```

Run the included HTTP tests on a disposable Odoo 19 database (not production):

```sh
./odoo-bin --addons-path=addons,/path/to/nappysminimart-website \
  -d nappys_test -i nappys_website --without-demo=all \
  --test-enable --test-tags nappys_website --stop-after-init
```

Tests cover page routes, native cart/checkout, product publication, restricted catalogues, archived/non-saleable products, cross-website isolation, and repeated setup preserving edits.

## Credits

Code: LGPL-3; see [LICENSE](LICENSE). Brand artwork belongs to the client and is not licensed as generic code. The code was adapted from Spxcorp Limited’s La Rosa website module. Photographs are subject to the Pexels licence and fonts to their included OFL licence; see [PHOTO_CREDITS.md](PHOTO_CREDITS.md).

## POS product names — 19.0.1.0.1

Product cards wrap to show the complete product name, including colour, size and pack details. This applies to image and image-free cards. The change uses the same Odoo 19 view inheritance as the La Rosa fix and is scoped to the product grid.

Pull this repository in CloudPepper, upgrade `nappys_website`, and reload the POS browser to receive the change. Point of Sale is now an explicit dependency.

## 58 mm receipts — 19.0.1.0.2

Nappy’s USB Xprinter XP-58IIL uses a 48 mm printable area on 58 mm paper (manufacturer: https://www.xprintertech.com/xprinter-58mm-xp-58iil). The POS receipt preview and browser print layout use this width, a centered company logo, wrapping product names, aligned amounts and compact contact details. Receipt QR blocks are hidden; also disable **Self-service invoicing** in POS settings. The company logo is the native receipt logo.

At the till, select the Xprinter driver, 58 mm roll paper, 100% scale, no browser margins, and headers/footers off. This does not install a driver or change Windows printer preferences remotely. Keep native browser printing for the USB model; no Epson network IP is required. A physical test print is required to confirm driver feed length and hardware margins.

### Receipt edge spacing — 19.0.1.0.3

The 48 mm receipt box includes 1.5 mm of inner padding on each side and 1 mm above/below, keeping quantities and totals away from the printable edge. Use Chrome custom scale 100%, margins None. A driver form such as 58(48) mm × 210 mm sets a fixed 210 mm sheet length; choose a suitable shorter/roll form in the driver if available to reduce blank feed.

### Receipt footer — 19.0.1.0.4

Hide the telephone line and Powered by Odoo on POS receipts only. Company contact data, the logo, location and approved 58 mm spacing remain unchanged.
