/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { loadJS } from "@web/core/assets";
import { browser } from "@web/core/browser/browser";
import { patch } from "@web/core/utils/patch";
import { Navbar } from "@point_of_sale/app/components/navbar/navbar";
import { makeAwaitable } from "@point_of_sale/app/utils/make_awaitable_dialog";
import { DrawerBridge, readDrawerSettings } from "./drawer_bridge";

let bridgePromise;
function getBridge() {
    if (!bridgePromise) {
        bridgePromise = (async () => {
            if (!window.qz) {
                await loadJS("/nappys_website/static/lib/qz-tray/qz-tray.js");
            }
            if (!window.qz?.websocket || !window.qz?.print) {
                throw new Error("The QZ printer client could not load. Refresh POS and try again.");
            }
            return new DrawerBridge(window.qz);
        })().catch((error) => {
            bridgePromise = null;
            throw error;
        });
    }
    return bridgePromise;
}
function message(error) {
    return error?.message || String(error || "The printer did not accept the request.");
}

export class DrawerSetup extends Component {
    static template = "nappys_website.DrawerSetup";
    static components = { Dialog };
    static props = { close: Function, getPayload: Function, storageKey: String };
    setup() {
        const saved = readDrawerSettings(browser.localStorage, this.props.storageKey);
        this.state = useState({
            printer: saved?.printer || "", pin: String(saved?.pin ?? 0),
            printers: [], busy: false, connected: false, error: "",
        });
    }
    async findPrinters() {
        if (this.state.busy) return;
        this.state.busy = true;
        this.state.error = "";
        this.state.connected = false;
        try {
            const bridge = await getBridge();
            this.state.printers = await bridge.printers();
            this.state.connected = true;
            if (!this.state.printers.includes(this.state.printer)) this.state.printer = "";
            if (!this.state.printers.length) {
                this.state.error = "Windows has no available printers. Install the Xprinter driver, then try again.";
            }
        } catch (error) {
            this.state.error = "Open QZ Tray on this till and approve its connection request. " + message(error);
        } finally {
            this.state.busy = false;
        }
    }
    save() {
        if (!this.state.connected || !this.state.printers.includes(this.state.printer)) return;
        const settings = { printer: this.state.printer, pin: Number(this.state.pin) };
        try {
            browser.localStorage.setItem(this.props.storageKey, JSON.stringify(settings));
        } catch {
            this.state.error = "Chrome could not save this till's printer. Allow site storage and try again.";
            return;
        }
        this.props.getPayload(settings);
        this.props.close();
    }
}

patch(Navbar.prototype, {
    setup() {
        super.setup(...arguments);
        this.nappysDrawer = useState({ busy: false });
    },
    get nappysDrawerStorageKey() {
        return `nappys.drawer.v1.${this.pos.config.id}`;
    },
    async nappysDrawerSetup() {
        if (this.nappysDrawer.busy || this.pos.cashier?._role === "minimal") return;
        this.nappysDrawer.busy = true;
        try {
            await makeAwaitable(this.dialog, DrawerSetup, { storageKey: this.nappysDrawerStorageKey });
        } finally {
            this.nappysDrawer.busy = false;
        }
    },
    async nappysOpenDrawer() {
        if (this.nappysDrawer.busy || this.pos.cashier?._role === "minimal") return;
        const settings = readDrawerSettings(browser.localStorage, this.nappysDrawerStorageKey);
        if (!settings) {
            await this.nappysDrawerSetup();
            return; // Saving the printer does not open the drawer; press Open Drawer afterwards.
        }
        this.nappysDrawer.busy = true;
        try {
            const bridge = await getBridge();
            await bridge.open(settings);
            this.notification.add("Drawer command sent.", { type: "success" });
            try {
                await this.pos.logEmployeeMessage("Open Drawer (QZ USB)", "CASH_DRAWER_ACTION");
            } catch {
                this.notification.add("The drawer command was sent, but its session log could not be saved.", { type: "warning" });
            }
        } catch (error) {
            this.dialog.add(AlertDialog, {
                title: "Drawer command not confirmed",
                body: "Check that QZ Tray is running and the Xprinter is switched on. Approve the QZ request if prompted. You can change the printer under the POS menu → Drawer setup.\n\n" + message(error),
            });
        } finally {
            this.nappysDrawer.busy = false;
        }
    },
});
