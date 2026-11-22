"use strict";
// ヘッドレススモーク: リアルタイム時計が1年=30秒で進み、チャートが毎フレーム動くか
const fs = require("fs");
globalThis.window = globalThis;
const CAP = [];
function mkEl(tag) {
    return {
        tag: tag || "div", _sel: {}, style: {}, children: { length: 0 },
        classList: { toggle() {}, add() {}, remove() {}, contains() { return false; } },
        _inner: "", textContent: "", value: "", id: "",
        set innerHTML(v) { this._inner = v; }, get innerHTML() { return this._inner; },
        appendChild(c) { return c; }, prepend(c) { return c; }, remove() {},
        addEventListener() {}, setAttribute(k, v) { CAP.push([this.id || "?", k, String(v)]); },
        querySelector(s) { return this._sel[s] || (this._sel[s] = mkEl()); },
        querySelectorAll() { return []; }, scrollTop: 0, scrollHeight: 0,
    };
}
const els = {};
globalThis.document = {
    querySelector(s) { return els[s] || (els[s] = mkEl()); },
    createElement(t) { return mkEl(t); },
    body: mkEl("body"),
};
let rafCb = null;
globalThis.requestAnimationFrame = (fn) => { rafCb = fn; };
const W = "D:/dev/chrono_fx/web/";
require(W + "data.js");
const api = require(W + "game.js");
globalThis.CHRONO = api;
(0, eval)(fs.readFileSync(W + "ui.js", "utf8"));
els["#cur"].value = "electrum";
const y0 = api.getState().year;
let ts = 0;
for (let i = 0; i < 65; i++) {  // 65秒ぶんの実時間
    ts += 1000;
    const cb = rafCb; rafCb = null; cb(ts);
}
const y1 = api.getState().year;
const lineVals = CAP.filter((c) => c[1] === "points").map((c) => c[2]);
const uniq = new Set(lineVals).size;
const lastY = (s) => s.split(" ").pop().split(",")[1];
let ok = true;
const ck = (name, cond) => { if (!cond) ok = false; console.log((cond ? "PASS" : "FAIL") + " " + name); };
ck("65秒で2年進む(既定30秒/年): " + y0 + "->" + y1, y1 - y0 === 2);
ck("チャートのpoints更新が発生 " + lineVals.length + "回", lineVals.length > 6);
ck("毎フレーム座標が変わる(動くチャート) 重複除外" + uniq,
   uniq > lineVals.length * 0.7);
ck("先端のyが実際に移動", new Set(lineVals.map(lastY)).size > 1);
ck("まだ終了していない", !api.done());
console.log(ok ? "RT SMOKE OK" : "RT SMOKE NG");
process.exit(ok ? 0 : 1);
