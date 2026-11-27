import { readFile } from 'node:fs/promises';
import test from 'node:test';
import assert from 'node:assert/strict';
const source = await readFile(new URL('../nappys_website/static/src/pos/drawer_bridge.js', import.meta.url), 'utf8');
const { DrawerBridge, readDrawerSettings, drawerPulse } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`);
function mockQz() {
    const calls = [];
    let active = false;
    const qz = {
        websocket: { isActive: () => active, connect: async () => { calls.push('connect'); active = true; } },
        printers: { find: async () => ['Xprinter XP-58', 'Other Printer'] },
        configs: { create: (printer, options) => ({printer, ...options}) },
        print: async (config, data) => calls.push({config, data}),
    };
    return { qz, calls };
}
test('sends a pulse only to the exact saved printer, without printable or feed data', async () => {
    const {qz, calls} = mockQz();
    await new DrawerBridge(qz).open({printer: 'Xprinter XP-58', pin: 0});
    assert.equal(calls[1].config.printer, 'Xprinter XP-58');
    const bytes = Buffer.from(calls[1].data[0].data, 'hex');
    assert.deepEqual([...bytes], [27, 112, 0, 25, 250]);
    assert.equal(calls[1].data.length, 1);
});
test('failed or denied QZ connection never sends a pulse', async () => {
    const {qz, calls} = mockQz();
    qz.websocket.connect = async () => { throw Error('Denied'); };
    await assert.rejects(new DrawerBridge(qz).open({printer: 'Xprinter XP-58', pin: 0}), /Denied/);
    assert.deepEqual(calls, []);
});
test('does not retry a rejected print or fall back to the default printer', async () => {
    const {qz} = mockQz(); let sends = 0;
    qz.print = async () => { sends++; throw Error('Printer unavailable'); };
    await assert.rejects(new DrawerBridge(qz).open({printer: 'Xprinter XP-58', pin: 0}), /unavailable/);
    assert.equal(sends, 1);
});
test('blocks overlapping drawer requests and releases the lock after completion', async () => {
    const {qz} = mockQz(); let finish; let sends = 0;
    qz.print = () => { sends++; return new Promise(resolve => { finish = resolve; }); };
    const bridge = new DrawerBridge(qz);
    const first = bridge.open({printer: 'Xprinter XP-58', pin: 0});
    await assert.rejects(bridge.open({printer: 'Xprinter XP-58', pin: 0}), /in progress/);
    await new Promise(resolve => setImmediate(resolve));
    finish(); await first;
    assert.equal(sends, 1); assert.equal(bridge.sending, false);
});
test('corrupt terminal preferences require setup; invalid pin cannot send a command', async () => {
    for (const raw of ['{', '{}', '{"printer":"","pin":0}', '{"printer":"Xprinter","pin":5}']) {
        assert.equal(readDrawerSettings({getItem: () => raw}, 'key'), null);
    }
    const {qz, calls} = mockQz();
    await assert.rejects(new DrawerBridge(qz).open({printer: 'Xprinter', pin: 5}), /pin/);
    assert.deepEqual(calls, []);
    assert.equal(drawerPulse(1)[0].data, '1B700119FA');
});
