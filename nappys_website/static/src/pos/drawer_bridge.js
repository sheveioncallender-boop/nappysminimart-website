/** @odoo-module **/

// No sale, receipt, paper-feed or cutter commands are sent by this adapter.
export function drawerPulse(pin = 0) {
    if (pin !== 0 && pin !== 1) {
        throw new Error("Choose drawer pin 2 or pin 5.");
    }
    // ESC p m t1 t2: 50 ms on, 500 ms off. Hex avoids character encoding changes.
    return [{ type: "raw", format: "command", flavor: "hex", data: pin === 0 ? "1B700019FA" : "1B700119FA" }];
}

export function readDrawerSettings(storage, key) {
    try {
        const value = JSON.parse(storage.getItem(key));
        if (typeof value?.printer === "string" && value.printer.trim() && [0, 1].includes(value.pin)) {
            return { printer: value.printer, pin: value.pin };
        }
    } catch { /* Missing, blocked or old local settings mean setup is needed. */ }
    return null;
}

export class DrawerBridge {
    constructor(qz) {
        this.qz = qz;
        this.connecting = null;
        this.sending = false;
    }
    async connect() {
        if (this.qz.websocket.isActive()) {
            return;
        }
        if (!this.connecting) {
            // Use QZ's normal local, secure websocket and permission prompts.
            // Never change trust settings or use a remote print host.
            this.connecting = this.qz.websocket.connect({ retries: 0 }).finally(() => {
                this.connecting = null;
            });
        }
        await this.connecting;
    }
    async printers() {
        await this.connect();
        const names = await this.qz.printers.find();
        return [...new Set(names)].sort();
    }
    async open(settings) {
        if (this.sending) {
            throw new Error("A drawer command is already in progress.");
        }
        if (!settings || typeof settings.printer !== "string" || !settings.printer.trim()) {
            throw new Error("Select this till's receipt printer in Drawer setup first.");
        }
        const data = drawerPulse(settings.pin);
        this.sending = true;
        try {
            await this.connect();
            const config = this.qz.configs.create(settings.printer, { jobName: "Nappy's — Open drawer" });
            // An exact printer name is required. Never fall back to the default printer.
            await this.qz.print(config, data);
        } finally {
            this.sending = false;
        }
    }
}
