const assert = (c, m) => {
    if (!c) { console.error("FAIL " + m); process.exit(1); } };
require("./data.js");
const G = require("./game.js");
let out = G.submit("new");
assert(out.join("\n").includes("エレクトロン貨"), "intro");
out = G.submit("b electrum 30");
assert(out.join("\n").includes("購入"), "buy");
out = G.submit("n");
assert(G.getState().year === -594, "stop at -594, got " + G.getState().year);
out = G.submit("n");
assert(out.join("\n").includes("ソロン"), "event -594 applied on 2nd n");
out = G.submit("s electrum all");
assert(out.join("\n").includes("売却"), "sell");
G.submit("n 400");
out = G.submit("b denarius 99999");
assert(out.join("\n").includes("却下"), "leverage reject");
G.submit("new"); G.submit("b electrum 30");
out = G.submit("n 200");
assert(out.join("\n").includes("☠") && out.join("\n").includes("ダレイコス"), "succession");
G.submit("new"); G.getState().silver = 4000;
G.submit("n 2692");
assert(G.getState().year === 1992, "to 1992");
out = G.submit("sh pound 800");
assert(out.join("\n").includes("売り建て"), "short pound");
out = G.submit("a BoE92");
assert(out.join("\n").includes("⚔"), "attack start");
let fell = false;
for (let i = 0; i < 3; i++) {
    out = G.submit("n 1");
    if (out.join("\n").includes("陥落")) fell = true; }
assert(fell && G.BANKS["BoE92"].fallen, "BoE92 falls");
G.submit("new"); G.submit("n 2476");
assert(G.getState().year === 1776, "to 1776");
G.submit("b continental all");
out = G.submit("n 20");
assert(out.join("\n").includes("GAME OVER"), "bankruptcy on fiat death");
console.log("ALL WEB ENGINE TESTS PASS");
