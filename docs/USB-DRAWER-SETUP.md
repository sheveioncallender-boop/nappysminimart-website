# Nappy’s USB cash drawer

Module version: **19.0.1.1.0**. Printer: **Xprinter XP-58IIL**, attached to Windows by USB; cash drawer attached to the printer.

## Install on the till

1. Download and install the Windows QZ Tray application from https://qz.io/download.
2. Start QZ Tray and leave it running in the Windows notification area. Enable its normal automatic startup option if desired.
3. Leave the working Xprinter Windows driver and Chrome receipt settings in place.

## Deploy the Odoo update

1. Pull the latest `main` branch of `sheveioncallender-boop/nappysminimart-website` in CloudPepper.
2. Upgrade the existing **Nappy’s Minimart — Website & Shop** module (`nappys_website`) to **19.0.1.1.0**. This is an update to the existing module, not a separate application.
3. Finish any in-progress payment and refresh the POS browser with Ctrl+Shift+R. Do not close the register session just to update the browser.
4. Check that **Open Drawer** appears in the top bar. On narrow screens it shows a drawer icon. The menu also includes **Drawer setup**.

## Connect this computer

1. Open **POS menu → Drawer setup → Connect and find printers**.
2. Approve QZ’s connection/printer-list prompt for the Nappy’s Odoo site.
3. Select the exact Windows printer, expected to be **Xprinter XP-58** from the till screenshot. The list comes from QZ on that computer; no default printer is selected automatically.
4. Keep **Pin 2 — standard**, then press **Save printer**. Saving does not activate the drawer.
5. Press **Open Drawer** and approve QZ’s request. Check the drawer physically. No sale is posted, no receipt is generated, and the command contains no text, paper-feed or cutter instruction.
6. If the printer accepts the command but the drawer stays shut, check the cable/lock and try **Pin 5 — alternate** in Drawer setup.

Printer selection is stored only in that browser for that POS configuration. Repeat setup on each till or after clearing browser storage.

## Permission prompts

This release uses QZ’s normal unsigned permission prompts. It does not disable QZ protections, install a trust certificate, or promise silent one-click operation. Prompt-free use is a separate QZ certificate and server-side signing setup; private signing keys must never be placed in browser assets or the Git repository.

## Troubleshooting

- **Cannot connect:** start QZ Tray; check its permission dialog. Use HTTPS on the Odoo site and approve the normal Windows QZ installation certificate prompt when installing the official application.
- **Wrong/unavailable printer:** return to Drawer setup and select the exact current Windows queue. The button never silently chooses another printer.
- **Command accepted but drawer closed:** the success notice only confirms submission to QZ. Check printer power, cable and drawer lock; try the alternate pin if appropriate.
- **Raw printing not supported by the driver:** use QZ’s official Windows raw-printer setup guide to add a separate Generic/Text queue on the same USB port for drawer commands. Keep normal receipts on the existing Xprinter queue. https://qz.io/docs/setting-up-a-raw-printer-in-windows
- **No button after deploy:** confirm the module upgrade, refresh POS assets, and check that the cashier is not assigned Odoo’s minimal role.

## Implementation and validation

The native Odoo 19 POS navbar is extended through the POS asset bundle. The QZ JavaScript client 2.2.5 is vendored unmodified with its LGPL license. The drawer adapter sends exactly one ESC/POS pulse (`1B 70 00 19 FA`, or pin-5 `1B 70 01 19 FA`), with a lock against overlapping requests and no automatic retry. Submission is recorded using Odoo’s normal session message method; a failed log does not resend the hardware command.

Validation: module structure, Odoo 19 navbar XPath inheritance, native JavaScript transpilation, and five adapter tests. A physical USB drawer test requires the till and has not been performed remotely.

Sources: https://qz.io/docs/getting-started · https://qz.io/docs/raw · https://qz.io/docs/signing
