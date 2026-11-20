// CHRONO FX 〜エレクトロン・スタンダード〜 Web/APK版エンジン
// chronofx.py（CLI版）の忠実移植。データは data.js（生成物）から読む。
"use strict";
const FEE = 0.003, LEV = 10.0, INTR = 0.02, ATT_INTR = 0.06, DRIFT = 0.995;
const START_YEAR = -700, END_YEAR = 2026, START_SILVER = 50.0;
const CURS = {};
for (const c of DATA.cur) CURS[c[0]] = { name: c[1], y0: c[2], y1: c[3],
    succ: c[4], base: c[5], regime: c[6], factor: 1.0 };
const BANKS = {};
for (const b of DATA.bank) BANKS[b[0]] = { cur: b[1], y0: b[2], y1: b[3],
    reserves0: b[4], reserves: b[4], deval: b[5],
    fallen: false, missed: false, attack: false };
let S = null, LOG = [], OVER = false;
function emit(s) { LOG.push(String(s)); }
function yname(y) { return y < 0 ? ("紀元前" + (-y) + "年") : (y + "年"); }
function fmt_g(g) {
    g = Number(g);
    if (Number.isNaN(g)) return "NaN";
    if (g === Infinity) return "∞";
    const a = Math.abs(g);
    if (a >= 1e12 || (a > 0 && a < 1e-6)) return g.toExponential(2) + "g";
    if (a >= 1e4) return Math.round(g).toLocaleString("en-US") + "g";
    return g.toLocaleString("en-US", { minimumFractionDigits: 2,
        maximumFractionDigits: 2 }) + "g";
}
function fmtNum(x) {
    x = Number(x);
    if (!Number.isFinite(x)) return String(x);
    const a = Math.abs(x);
    if (a !== 0 && (a >= 1e4 || a < 1e-3)) return x.toExponential(3);
    const s = Number(x.toPrecision(4));
    return Number.isInteger(s) ? s.toLocaleString("en-US") : String(s);
}
function pad(s, n) { s = String(s); return s.length >= n ? s : s + " ".repeat(n - s.length); }

function reset() {
    S = { year: START_YEAR, silver: START_SILVER, debt: 0.0, hold: {}, short: {} };
    OVER = false;
    for (const c in CURS) CURS[c].factor = 1.0;
    for (const k in BANKS) { const b = BANKS[k];
        b.fallen = false; b.missed = false; b.attack = false;
        b.reserves = b.reserves0; }
}
function born(cid) { return CURS[cid].y0 <= S.year; }
function alive(cid) { return born(cid) && S.year <= CURS[cid].y1; }
function price(cid) { const c = CURS[cid]; return Math.max(c.base * c.factor, 1e-18); }
function long_val() { let t = 0; for (const c in S.hold) { const q = S.hold[c];
    if (q > 0 && born(c)) t += q * price(c); } return t; }
function short_val() { let t = 0; for (const c in S.short) { const q = S.short[c];
    if (q > 0 && born(c)) t += q * price(c); } return t; }
function equity() { return S.silver + long_val() - S.debt - short_val(); }
function exposure() { return long_val() + short_val() + S.debt; }
function hint(cid, year) {
    for (const e of DATA.events) {
        if (e[1] === cid && e[0] === year) {
            if (e[4] && BANKS[e[4]].fallen) continue;
            return e[2] > 1 ? "▲" : "▼"; } }
    for (const b of DATA.bank)
        if (b[1] === cid && b[2] <= year && year <= b[3] && !BANKS[b[0]].fallen)
            return "◆";
    return " ";
}
function net_line() {
    const eq = equity(), ex = exposure();
    const lev = eq > 0 ? ex / eq : Infinity;
    return "◆ " + yname(S.year) + " | 純資産 " + fmt_g(eq) +
        "（銀 " + fmt_g(S.silver) + " 借入 " + fmt_g(S.debt) + "）" +
        "| 建値 " + lev.toFixed(1) + "倍/上限" + LEV.toFixed(0) + "倍";
}

function pos_line() {
    const ps = [];
    for (const c in S.hold) { const q = S.hold[c];
        if (q > 1e-12) ps.push("買 " + CURS[c].name + "×" + fmtNum(q) +
            " (" + fmt_g(q * price(c)) + ")"); }
    for (const c in S.short) { const q = S.short[c];
        if (q > 1e-12) ps.push("売 " + CURS[c].name + "×" + fmtNum(q) +
            " (" + fmt_g(q * price(c)) + ")"); }
    return "持ち高: " + (ps.length ? ps.join(" / ") : "なし");
}
function year_end(y) {
    const out = [];
    S.debt *= (1 + INTR);
    for (const k in BANKS) { const b = BANKS[k];
        if (b.attack) { const cid = b.cur;
            if ((S.short[cid] || 0) > 0) { S.short[cid] *= (1 + ATT_INTR);
                out.push("　" + CURS[cid].name + "の中銀、利上げ。売り建てに年" +
                    (ATT_INTR * 100).toFixed(0) + "%の利子"); } } }
    if (y >= 1971)
        for (const k in CURS) if (CURS[k].regime === "f") CURS[k].factor *= DRIFT;
    for (const k in BANKS) if (BANKS[k].attack) settle_attack(k, out);
    const dying = [];
    for (const k in CURS) if (CURS[k].y1 === y) dying.push(k);
    for (const cid of dying) {
        const v = CURS[cid];
        const hl = S.hold[cid] || 0.0, sh = S.short[cid] || 0.0;
        delete S.hold[cid]; delete S.short[cid];
        if (hl > 1e-12 && v.succ && born(v.succ)) {
            const s2 = v.succ, got = hl * price(cid) / price(s2);
            S.hold[s2] = (S.hold[s2] || 0.0) + got;
            out.push("☠ " + v.name + "、この世を去る。持っていた " + fmtNum(hl) +
                " 枚は継承通貨 " + CURS[s2].name + " " + fmtNum(got) + " に生まれ変わった");
        } else if (hl > 1e-12)
            out.push("☠ " + v.name + "、国家ごと滅んだ。継承なし——持っていた " +
                fmtNum(hl) + " 枚は紙屑と化した（-" + fmt_g(hl * price(cid)) + "）");
        if (sh > 1e-12)
            out.push("⚖ " + v.name + "の売り建て " + fmtNum(sh) + "、債務ごと消滅。買い戻さなくて済んだ");
        v.factor = 0.0; }
    for (const bid in BANKS) { const b = BANKS[bid];
        if (!b.fallen && !b.missed && y > b.y1) { b.missed = true;
            out.push("◎ 「" + CURS[b.cur].name + "」の中央銀行 " + bid +
                "、為替防衛に成功。この機会は二度と来ない（取り逃し）"); } }
    return out;
}

function apply_event(ev) {
    const y = ev[0], cid = ev[1], m = ev[2], head = ev[3];
    const nb = ev.length > 4 ? ev[4] : null;
    if (nb && BANKS[nb].attack) return [];
    if (nb && BANKS[nb].fallen)
        return ["▶ " + yname(y) + " " + head + " —— だがその中銀は既にあなたに倒されていた"];
    CURS[cid].factor = Math.max(CURS[cid].factor * m, 1e-30);
    return ["▶ " + yname(y) + " " + head + "（" + CURS[cid].name + " " +
        (m > 1 ? "急騰" : "急落") + " ×" + fmtNum(m) + "）"];
}
function advance_to(ny) {
    const lines = [];
    while (S.year < ny) {
        const y = S.year;
        for (const e of DATA.events) if (e[0] === y) lines.push(...apply_event(e));
        lines.push(...year_end(y));
        S.year = y + 1;
        if (equity() <= 0) return lines;
    }
    return lines;
}
function step_to(ny, out) {
    ny = Math.min(ny, END_YEAR);
    out.push(...advance_to(ny));
    if (S.year >= END_YEAR)
        for (const e of DATA.events) if (e[0] === END_YEAR) out.push(...apply_event(e));
}
function next_news_year() {
    let best = END_YEAR;
    for (const e of DATA.events) if (e[0] > S.year && e[0] < best) best = e[0];
    return best;
}
function can_do() { const eq = equity(); return eq > 0 && exposure() <= LEV * eq + 1e-9; }
function _repay_debt() {
    if (S.debt > 0 && S.silver > 0) {
        const r = Math.min(S.debt, S.silver); S.debt -= r; S.silver -= r; }
}

function do_buy(cid, g, quiet) {
    if (!alive(cid)) return "その通貨はまだこの世に無い（か、既に死んでいる）";
    if (!(g > 0)) return "数量を正しく指定してね（例: b usd 10 / b usd all）";
    const snap = [S.silver, S.debt];
    const qty = g * (1 - FEE) / price(cid);
    S.silver -= g;
    if (S.silver < 0) { S.debt += -S.silver; S.silver = 0.0; }
    S.hold[cid] = (S.hold[cid] || 0.0) + qty;
    if (!can_do()) {
        S.hold[cid] -= qty; S.silver = snap[0]; S.debt = snap[1];
        return "却下: レバレッジ上限（純資産の" + LEV.toFixed(0) + "倍）を超える買いは許されない"; }
    if (!quiet) {
        const bor = S.debt <= 0 ? "" : "（うち借入 " + fmt_g(g) + "）";
        emit("　" + CURS[cid].name + " を " + fmt_g(g) + " ぶん購入（" +
            fmtNum(qty) + " 枚・手数料 0.3%）" + bor); }
    return null;
}
function do_sell(cid, g, quiet) {
    const have = (S.hold[cid] || 0.0) * price(cid);
    if (!(have > 0)) return "その通貨の現物を持っていない";
    g = Math.min(g, have);
    const qty = g / price(cid);
    S.hold[cid] -= qty;
    S.silver += g * (1 - FEE);
    _repay_debt();
    if (!quiet) emit("　" + CURS[cid].name + " を " + fmt_g(g) + " ぶん売却（受取 " +
        fmt_g(g * (1 - FEE)) + "）");
    return null;
}
function do_short(cid, n, quiet) {
    if (!alive(cid)) return "その通貨を売り建てることはできない";
    const g = n * price(cid), snap = [S.silver, S.debt];
    S.short[cid] = (S.short[cid] || 0.0) + n;
    S.silver += g * (1 - FEE);
    _repay_debt();
    if (!can_do()) {
        S.short[cid] -= n; S.silver = snap[0]; S.debt = snap[1];
        return "却下: レバレッジ上限（" + LEV.toFixed(0) + "倍）を超えてしまう"; }
    if (!quiet) emit("　" + CURS[cid].name + " を " + fmtNum(n) + " 枚 売り建て（受取 " +
        fmt_g(g * (1 - FEE)) + "・下落が儲け）");
    return null;
}
function do_cover(cid, n, quiet) {
    const have = S.short[cid] || 0.0;
    if (!(have > 1e-12)) return "売り建てが無い";
    if (n === "all" || n >= have) n = have;
    const g = n * price(cid);
    if (S.silver < g * (1 + FEE)) {
        const need = g * (1 + FEE) - S.silver;
        S.silver += need; S.debt += need; }
    S.short[cid] -= n;
    S.silver -= g * (1 + FEE);
    _repay_debt();
    if (!quiet) emit("　" + CURS[cid].name + " 売り建て " + fmtNum(n) +
        " 枚を買い戻し（支払 " + fmt_g(g * (1 + FEE)) + "）");
    return null;
}

function banks_line() {
    const lines = [];
    for (const bid in BANKS) { const b = BANKS[bid]; let st;
        if (b.fallen) st = "☠倒壊"; else if (b.missed) st = "…取り逃し";
        else if (b.y0 <= S.year && S.year <= b.y1) st = "●攻撃可";
        else if (b.y0 > S.year) st = "先 (" + b.y0 + "〜)"; else st = "閉幕";
        const need = 0.5 * b.reserves;
        lines.push(" " + pad(bid, 10) + " " + pad(CURS[b.cur].name, 14) + " " +
            yname(b.y0) + "〜" + yname(b.y1) + " 準備金 " + fmt_g(b.reserves) +
            "（売り建て " + fmt_g(need) + "〜）" + st); }
    return lines.join("\n");
}
function show_banks() {
    emit("売り攻勢の標的（条件: ウィンドウ内の年であること、対象の売り建てが準備金の半分以上）:");
    emit(banks_line());
    emit(" a <ID> で攻勢開始 / x <ID> で中止。準備金が尽きると通貨を撃墜、" +
        "売り建ては安値で自動決済され戦利品が入る");
}
function do_attack(bid, quiet) {
    if (!(bid in BANKS)) return "そんな銀行は無い（a で一覧）";
    const b = BANKS[bid];
    if (b.fallen) return "もう倒した銀行だ。二度殺すのはやめよう";
    if (b.missed) return "そのウィンドウは過ぎた。歴史は待ってくれない";
    if (!(b.y0 <= S.year && S.year <= b.y1)) {
        if (S.year > b.y1) return "その機会（きかい）は過ぎた（攻撃可能は " +
            yname(b.y0) + "〜" + yname(b.y1) + "）";
        return "まだ早い（攻撃可能は " + yname(b.y0) + "〜" + yname(b.y1) + "）"; }
    if (b.attack) return "既に攻勢中だ。耐えてくれ";
    const cid = b.cur, sv = (S.short[cid] || 0.0) * price(cid);
    if (sv < 0.5 * b.reserves) return "売り建てが足りない: " + CURS[cid].name +
        "の売り建てが " + fmt_g(0.5 * b.reserves) + "以上必要（現在 " + fmt_g(sv) + "）";
    b.attack = true;
    if (!quiet) emit("⚔ 宣言: " + CURS[cid].name + "の中央銀行 " + bid +
        " へ売り攻勢を開始！準備金 " + fmt_g(b.reserves) + " を枯らすまで殴り続ける");
    return null;
}
function do_stop(bid) {
    const b = BANKS[bid];
    if (!b || !b.attack) return "攻勢中の銀行が無い";
    b.attack = false;
    return bid + " への攻勢を中止した";
}

function settle_attack(bid, out) {
    const b = BANKS[bid], cid = b.cur;
    const sv = (S.short[cid] || 0.0) * price(cid);
    if (sv <= 0) { b.attack = false;
        out.push("　" + bid + "、売り持ちが居なくなって肩透かし。攻勢自然消滅"); return; }
    b.reserves -= sv * (0.8 + Math.random() * 0.8);
    CURS[cid].factor *= 1.08;
    if (b.reserves > 0) { out.push("　" + bid + "、利上げと介入で反撃（準備金残 " +
        fmt_g(b.reserves) + "。" + CURS[cid].name + "を1.08倍買い支えた）"); return; }
    b.attack = false; b.fallen = true;
    const old = price(cid);
    CURS[cid].factor = Math.max(CURS[cid].factor * b.deval, 1e-30);
    out.push("★★☆ " + bid + " 陥落！！ " + CURS[cid].name + "が ×" + fmtNum(b.deval) +
        " に暴落（" + fmt_g(old) + "→" + fmt_g(price(cid)) + "）");
    const sh = S.short[cid] || 0.0; delete S.short[cid];
    if (sh > 1e-12) { const gain = sh * (old - price(cid)); S.silver += gain;
        out.push("　売り建て " + fmtNum(sh) + " 枚を安値で自動決済。+" + fmt_g(gain)); }
    const bounty = 0.03 * b.reserves0;
    S.silver += bounty;
    out.push("　戦利品 +" + fmt_g(bounty) + "（中銀の金庫から）");
}
function show_prices() {
    const rows = ["  " + pad("ID", 11) + " " + pad("通貨", 16) + " 現在値(銀g) 体制 終末 見通し"];
    for (const cid in CURS) { const c = CURS[cid];
        if (!alive(cid)) continue;
        let d = "";
        if (c.y1 <= S.year + 10) d = c.succ ? "⌛継承あり" : "⚰滅亡へ";
        const p = Number(price(cid)).toPrecision(4);
        rows.push("  " + pad(cid, 11) + " " + pad(c.name, 16) + " " +
            ("            " + p).slice(-12) + "  " + (c.regime === "g" ? "金" : "紙") +
            "   " + d + "  " + hint(cid, S.year)); }
    emit(rows.join("\n"));
}
const HELP = "コマンド: b<通貨> <g数|all>=買 / s<通貨> <g数|all>=売 / " +
    "sh<通貨> <枚数>=売り建て / cv<通貨> <枚数|all>=買戻し / a <銀行>=売り攻勢 / " +
    "x <銀行>=攻勢中止 / n[年数]=進む / l=一覧 p=相場 w=資産 bank=標的 h=ここ q=中断 new=続行";
function parseAmt(tok) {
    if (tok == null) return 1.0;
    if (tok === "all") return "all";
    if (!/^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$/.test(tok)) return null;
    const v = parseFloat(tok);
    return Number.isFinite(v) ? v : null;
}

function do_command(ts) {
    if (!ts.length) return;
    const op = ts[0].toLowerCase();
    if (op === "h" || op === "help" || op === "?") emit(HELP);
    else if (op === "l" || op === "list" || op === "p" || op === "price") show_prices();
    else if (op === "w" || op === "net") { emit(net_line()); emit(pos_line()); }
    else if (op === "bank") show_banks();
    else if (op === "b") {
        if (ts.length < 3) { emit("b <通貨> <g数|all>"); return; }
        const amt = parseAmt(ts[2]), cid = ts[1];
        if (!(cid in CURS)) { emit("その通貨は無い（l で一覧）"); return; }
        if (amt === null) { emit("g数は数字か all で"); return; }
        const g = amt === "all" ? S.silver : amt;
        const err = do_buy(cid, g, false); if (err) emit("　" + err); }
    else if (op === "s") {
        const cid = ts.length > 1 ? ts[1] : "";
        if (!(cid in CURS)) { emit("s <通貨> <g数|all>"); return; }
        const amt = ts.length > 2 ? parseAmt(ts[2]) : "all";
        const g = amt === "all" ? Infinity : (amt || 0);
        const err = do_sell(cid, g, false); if (err) emit("　" + err); }
    else if (op === "sh") {
        if (ts.length < 3) { emit("sh <通貨> <枚数>"); return; }
        const cid = ts[1], n = parseAmt(ts[2]);
        if (!(cid in CURS) || n === null || n === "all") { emit("枚数は数値で（sh usd 100）"); return; }
        const err = do_short(cid, n, false); if (err) emit("　" + err); }
    else if (op === "cv") {
        const cid = ts.length > 1 ? ts[1] : "";
        if (!(cid in CURS)) { emit("cv <通貨> <枚数|all>"); return; }
        let n = ts.length > 2 ? parseAmt(ts[2]) : "all";
        if (n === null) n = "all";
        const err = do_cover(cid, n, false); if (err) emit("　" + err); }
    else if (op === "a") {
        if (ts.length < 2) { show_banks(); return; }
        const err = do_attack(ts[1], false); if (err) emit("　" + err); }
    else if (op === "x") { if (ts.length > 1) emit("　" + (do_stop(ts[1]) || "")); }
}
function allFallen() { for (const k in BANKS) if (!BANKS[k].fallen) return false; return true; }
function gameOn() { return S.year < END_YEAR && equity() > 0 && !allFallen(); }
function wrap() {
    emit(""); emit("=".repeat(66));
    if (equity() <= 0)
        emit("▓▓ GAME OVER ▓▓ 資産が消し飛んだ。歴為替の波に呑まれた数は数知れず");
    else if (allFallen())
        emit("★★ GAME CLEAR ★★ 8中央銀行、すべて撃破。あなたは歴史そのものになった");
    else if (S.year >= END_YEAR)
        emit("★ GAME CLEAR ★ 2026年まで生き残った。最終資産で歴史の勝ち組みを測る");
    emit(net_line()); emit(pos_line());
    const f = []; for (const k in BANKS) if (BANKS[k].fallen) f.push(k);
    emit("倒した銀行 " + f.length + "/" + Object.keys(BANKS).length + ": " +
        (f.length ? f.join(", ") : "無し"));
    emit("経過 " + (S.year - START_YEAR) + "年 / 全 " + (END_YEAR - START_YEAR) + "年");
}

function intro() {
    emit("=".repeat(66)); emit("  CHRONO FX 〜エレクトロン・スタンダード〜");
    emit("  紀元前700年・リディアのエレクトロン貨から2026年まで、1年1コマ");
    emit("  ニュースを読んで Currency を売買し、資産を守り抜け。");
    emit("  ・手数料 0.3% / レバレッジ上限 純資産の10倍 / 銀借入に年2%");
    emit("  ・国家と運命を共にした通貨の現物は消滅、売り建ては債務ごと消滅");
    emit("  ・貴金属本位・固定相場の時代、準備金を持つ中央銀行を売り攻勢で倒せる");
    emit("  ・目標: 2026年まで破産せず生存、または " +
        Object.keys(BANKS).length + " 中銀すべて撃破");
    emit("  見通し記号 ▲=上げニュース ▼=下げニュース ◆=中銀攻撃可 ⌛=継承あり ⚰=滅亡へ");
    emit("=".repeat(66));
    emit(net_line());
    const names = []; for (const c in CURS) if (alive(c)) names.push(CURS[c].name);
    emit("当初からある通貨: " + names.join(", "));
    emit("(h でヘルプ / p で相場 / n で次のニュースまで)");
}
function newGame() { reset(); LOG = []; OVER = false; intro(); }
function submit(raw) {
    raw = String(raw).trim();
    if (raw.toLowerCase() === "new") { newGame(); return LOG.splice(0); }
    if (!gameOn()) {
        if (!OVER) { OVER = true; wrap(); }
        emit("（ゲームは終わっている。new で続行）"); return LOG.splice(0); }
    if (!raw) return LOG.splice(0);
    LOG.push("[" + yname(S.year) + "]> " + raw);
    const r = raw.toLowerCase();
    if (r === "q") { emit("（そこで観念して幕を下ろした）"); OVER = true; wrap();
        return LOG.splice(0); }
    if (r[0] === "n" && (r.length === 1 || r[1] === " " || /\d/.test(r[1]))) {
        let ny = next_news_year();
        if (r.length > 1) { const k = parseInt(raw.slice(1), 10);
            if (Number.isNaN(k)) { emit("n 後ろは年数（数字）"); return LOG.splice(0); }
            ny = Math.min(S.year + k, END_YEAR); }
        const out = []; step_to(ny, out);
        if (out.length) emit(out.join("\n"));
        emit(net_line()); emit(pos_line());
        if (!gameOn()) { OVER = true; wrap(); }
        return LOG.splice(0); }
    do_command(raw.split(/\s+/));
    if (!gameOn()) { OVER = true; wrap(); }
    return LOG.splice(0);
}

function initUI() {
    const log = document.getElementById("log"), inp = document.getElementById("cmd");
    function render(lines) {
        for (const l of lines) {
            const d = document.createElement("div");
            if (/^(★★|▓▓|⚔|☠|★ GAME)/.test(l.trim())) d.className = "big";
            d.textContent = l; log.appendChild(d); }
        log.scrollTop = log.scrollHeight; }
    function go(v) { v = v.trim(); if (!v) return; render(submit(v)); inp.value = ""; }
    document.getElementById("go").addEventListener("click", () => go(inp.value));
    inp.addEventListener("keydown", e => { if (e.key === "Enter") go(inp.value); });
    for (const b of document.querySelectorAll(".q"))
        b.addEventListener("click", () => {
            if (b.dataset.c === "q") go("q"); else render(submit(b.dataset.c)); });
    render(submit("new"));
}
if (typeof module !== "undefined" && module.exports)
    module.exports = { newGame, submit, getState: () => S, BANKS, CURS,
        equity, price, exposure, yname, done: () => !gameOn() };
else if (typeof document !== "undefined") initUI();
