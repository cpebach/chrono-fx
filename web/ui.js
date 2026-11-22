"use strict";
const C = window.CHRONO;
const $ = (s) => document.querySelector(s);
const el = (tag, cls, txt) => {
    const d = document.createElement(tag);
    if (cls) d.className = cls;
    if (txt != null) d.textContent = txt;
    return d;
};
function spark(arr, w = 96, h = 26) {
    if (!arr || arr.length < 2) return "";
    let lo = Math.min(...arr), hi = Math.max(...arr);
    const l2 = Math.max(lo, 1e-18), h2 = Math.max(hi, l2 * 1.02);
    const lr = Math.log(l2), hr = Math.log(h2);
    const pts = arr.map((v, i) => {
        const x = (i / (arr.length - 1)) * w;
        const y = h - ((Math.log(Math.max(v, l2)) - lr) / Math.max(hr - lr, 1e-9)) * h;
        return x.toFixed(1) + "," + y.toFixed(1);
    }).join(" ");
    const up = arr[arr.length - 1] >= arr[0];
    return '<svg viewBox="0 0 ' + w + " " + h + '" preserveAspectRatio="none">' +
        '<polyline points="' + pts + '" fill="none" stroke="' +
        (up ? "#ff6b6b" : "#3ecf8e") + '" stroke-width="1.6"/></svg>';
}
let snap = {};
function flashCard(cid, card) {
    const p = C.price(cid), prev = snap[cid];
    if (prev && Math.abs(p - prev) / Math.max(prev, 1e-18) > 0.005)
        card.classList.add(p > prev ? "fl-up" : "fl-dn");
    snap[cid] = p;
}
function renderWallet() {
    const s = C.getState(), eq = C.equity();
    $("#net").textContent = C.fmt_g(eq);
    $("#silver").textContent = C.fmt_g(s.silver);
    $("#debt").textContent = C.fmt_g(s.debt);
    const lev = eq > 0 ? C.exposure() / eq : Infinity;
    $("#lev").textContent = lev.toFixed(1) + "倍";
    $("#levbar").style.width = Math.min(100, (lev / 10) * 100) + "%";
    $("#eqspark").innerHTML = spark(C.EQSER, 150, 30);
    $("#fallen").textContent =
        Object.keys(C.BANKS).filter((k) => C.BANKS[k].fallen).length + "/8";
}
function holdRow(cid, q, kind) {
    const c = C.CURS[cid], p = C.price(cid);
    const card = el("div", "hcard");
    card.innerHTML =
        '<div class="hh"><b></b><span class="p"></span></div>' +
        '<div class="hs"><span></span><span class="spk">' + spark(C.HIST[cid]) + "</span></div>" +
        '<div class="hb"></div>';
    card.querySelector(".hh b").textContent = c.name;
    card.querySelector(".hh .p").textContent = C.fmt_g(p) + "/枚";
    card.querySelector(".hs span").textContent = kind + " ×" + C.fmtNum(q) +
        " = " + C.fmt_g(q * p);
    const bar = card.querySelector(".hb");
    const mk = (t, cmd) => {
        const b = el("button", "mini", t);
        b.addEventListener("click", () => run(cmd));
        bar.appendChild(b); };
    if (kind === "買") {
        mk("25%売", "s " + cid + " " + (q * p * 0.25).toFixed(8));
        mk("全売", "s " + cid + " all");
        mk("売り建", "sh " + cid + " " + Math.max(1, (q * p) / p).toFixed(4)); }
    else mk("買戻", "cv " + cid + " all");
    flashCard(cid, card);
    return card;
}
function renderHoldings() {
    const s = C.getState(), box = $("#holdings");
    box.innerHTML = "";
    let n = 0;
    for (const cid in s.hold) if (s.hold[cid] > 1e-9)
        { box.appendChild(holdRow(cid, s.hold[cid], "買")); n++; }
    for (const cid in s.short) if (s.short[cid] > 1e-9)
        { box.appendChild(holdRow(cid, s.short[cid], "売")); n++; }
    if (!n) box.appendChild(el("div", "dim", "ポジションなし。下の売買パネルから"));
}
function renderBanks() {
    const s = C.getState(), box = $("#banks");
    box.innerHTML = "";
    for (const bid in C.BANKS) {
        const b = C.BANKS[bid];
        const inW = b.y0 <= s.year && s.year <= b.y1;
        const pct = Math.max(0, Math.min(100, (100 * b.reserves) / b.reserves0));
        const sv = (s.short[b.cur] || 0) * C.price(b.cur);
        const row = el("div", "brow" + (b.fallen ? " dead" : "") + (b.attack ? " atk" : ""));
        row.innerHTML = '<div class="bt"><b></b> <span class="bc"></span>' +
            '<span class="wy"></span></div>' +
            '<div class="bbar"><i style="width:' + pct + '%"></i></div>' +
            '<div class="bs"></div>';
        row.querySelector("b").textContent = bid;
        row.querySelector(".bc").textContent = C.CURS[b.cur].name;
        row.querySelector(".wy").textContent = C.yname(b.y0) + "〜" + C.yname(b.y1);
        row.querySelector(".bs").textContent = "準備金 " + C.fmt_g(b.reserves) +
            "・売り建て " + C.fmt_g(sv) + "（要 " + C.fmt_g(0.5 * b.reserves) + "〜）" +
            (b.fallen ? " ☠倒壊" : b.missed ? " 取り逃し" : b.attack ? " ⚔攻勢中" :
                inW ? " ●攻撃可" : "");
        if (inW && !b.fallen && !b.missed && !b.attack) {
            const bt = el("button", "atk", "⚔ 売り攻勢");
            bt.addEventListener("click", () => run("a " + bid));
            row.appendChild(bt); }
        if (b.attack) {
            const st = el("button", "mini", "攻勢中止");
            st.addEventListener("click", () => run("x " + bid));
            row.appendChild(st); }
        box.appendChild(row); }
}
function newsCard(line) {
    let body = line.slice(2), yr = "", cur = "", dir = "", mult = "", head = body;
    const sp = body.indexOf(" ");
    if (sp > 0) { yr = body.slice(0, sp); head = body.slice(sp + 1); }
    const par = body.lastIndexOf("（");
    if (par > 0 && body.endsWith("）")) {
        const m2 = body.slice(par + 1, -1).match(/^(.+?) (急騰|急落) ×(.+)$/);
        if (m2) { cur = m2[1]; dir = m2[2]; mult = m2[3];
            head = body.slice(0, par).slice(yr.length + 1); } }
    const art = el("article", "news" + (dir ? (dir === "急騰" ? " up" : " dn") : ""));
    if (dir) art.innerHTML =
        '<div class="nh"><span class="media">⚡ CHRONO WIRE</span><time></time>' +
        '<span class="tag"></span></div><h2></h2>' +
        '<div class="nf"><span class="chip"></span><span class="src"></span></div>';
    else { art.className = "news lite"; art.innerHTML = "<h2></h2>"; }
    art.querySelector("h2").textContent = head;
    if (dir) {
        art.querySelector("time").textContent = yr;
        art.querySelector(".tag").textContent = dir === "急騰" ? "◎ 急騰" : "▼ 急落";
        art.querySelector(".chip").textContent = cur + " ×" + mult;
        art.querySelector(".src").textContent =
            "chronofx.wire/" + (yr.indexOf("前") >= 0 ? "ancient" : "modern"); }
    return art;
}
function addBanner(cls, txt) {
    const d = el("div", "banner " + cls);
    d.textContent = txt;
    $("#feed").prepend(d);
}
function fallFX() {
    document.body.classList.add("shake");
    setTimeout(() => document.body.classList.remove("shake"), 800);
    const b = el("div", "bigfall", "★ 陥 落 ★");
    document.body.appendChild(b);
    setTimeout(() => b.remove(), 1600);
}
function logLine(l) {
    const lg = $("#log");
    lg.appendChild(el("div", null, l));
    while (lg.children.length > 120) lg.removeChild(lg.firstChild);
    lg.scrollTop = lg.scrollHeight;
}
function handleLines(lines) {
    for (const l of lines) {
        if (l.startsWith("▶ ")) $("#feed").prepend(newsCard(l));
        else if (l.startsWith("★★☆")) { addBanner("fall", l); fallFX(); }
        else if (l.startsWith("⚔")) addBanner("atk", l);
        else if (l.startsWith("☠") || l.startsWith("⚖") || l.startsWith("◎"))
            addBanner("memento", l);
        else if (l.trim() && !l.startsWith("[")) logLine(l);
    }
}
function renderTicker() {
    const items = [];
    for (const cid in C.CURS) if (C.alive(cid)) {
        const h = C.HIST[cid], p = C.price(cid);
        const prev = h && h.length > 1 ? h[h.length - 2] : p;
        const d = prev > 0 ? (p - prev) / prev : 0;
        items.push('<span class="ti"><b>' + C.CURS[cid].name + "</b> " +
            C.fmt_g(p) + ' <i class="' + (d > 0.001 ? "up" :
                d < -0.001 ? "dn" : "fl") + '">' + (d >= 0 ? "▲" : "▼") +
            Math.abs(d * 100).toFixed(1) + "%</i></span>"); }
    $("#ticker").innerHTML = '<div class="tick">' +
        items.join("") + items.join("") + "</div>";
}
function renderSheet() {
    const sel = $("#cur"), keep = sel.value;
    sel.innerHTML = "";
    for (const cid in C.CURS) if (C.alive(cid)) {
        const o = el("option", null, C.CURS[cid].name + " " +
            C.fmt_g(C.price(cid)));
        o.value = cid;
        if (cid === keep) o.selected = true;
        sel.appendChild(o); }
    if (sel.value) $("#pxnow").textContent = C.fmt_g(C.price(sel.value)) + "/枚";
}
function trade(cmd) {
    const cid = $("#cur").value, amt = parseFloat($("#amt").value) || 0;
    if (!cid) return;
    if (cmd === "b") run("b " + cid + " " + amt);
    else if (cmd === "ball") run("b " + cid + " all");
    else if (cmd === "s") run("s " + cid + " " + amt);
    else if (cmd === "sall") run("s " + cid + " all");
    else if (cmd === "sh") { const p = C.price(cid);
        run("sh " + cid + " " + (amt > 0 && p > 0 ? (amt / p).toFixed(6) : "1")); }
    else if (cmd === "cv") run("cv " + cid + " all");
}
function run(cmd) {
    if (!cmd) return;
    const pre = C.getState();
    const y0 = pre ? pre.year : null, eq0 = pre ? C.equity() : 0;
    const oldP = {};
    if (pre) for (const cid in C.CURS) if (C.alive(cid)) oldP[cid] = C.price(cid);
    const out = C.submit(cmd);
    if (cmd === "new") { CLK.from = {}; CLK.fromEq = C.equity(); }
    else if (y0 !== null && C.getState().year > y0) {  // 年が進んだら旧価格から滑らかに動かし始める
        const f = {};
        for (const cid in C.CURS)
            if (C.alive(cid)) f[cid] = (cid in oldP) ? oldP[cid] : C.price(cid);
        CLK.from = f; CLK.fromEq = eq0;
    }
    CLK.left = CLK.yearMs;  // 手動送してもカウントダウンは振り出しへ
    handleLines(out);
    renderAll();
    updBar();
    const inp = $("#cmd");
    if (inp) inp.value = "";
    if (C.done()) endOverlay();
}
function renderAll() {
    $("#year").textContent = C.yname(C.getState().year);
    renderWallet(); renderHoldings(); renderBanks();
    renderSheet(); renderTicker(); renderChart();
    $("#hintline").textContent = C.net_line();
}
/* ===== リアルタイム時計（既定 1年=30秒）とライブチャート ===== */
const CLK = { yearMs: 30000, left: 30000, on: true, from: {}, prevT: 0 };
let CH = null;
const SPEEDS = [["s60", 60000], ["s30", 30000], ["s10", 10000], ["s3", 3000]];
function syncClockUI() {
    for (const sp of SPEEDS) $("#" + sp[0]).classList.toggle("on", CLK.yearMs === sp[1]);
    $("#pp").textContent = CLK.on ? "⏸ 一時停止" : "▶ 再開";
    $("#pp").classList.toggle("on", !CLK.on);
}
function updBar() {
    const f = (CLK.on && !C.done()) ? 1 - CLK.left / CLK.yearMs : 0;
    $("#tickbar").style.width = (f * 100).toFixed(1) + "%";
    $("#nexty").textContent = C.done() ? "歴史終了" :
        !CLK.on ? "⏸ 一時停止中" : "次の年まで " + Math.ceil(CLK.left / 1000) + "秒";
}
function liveVal(cid, ts) {
    const to = C.price(cid);
    const from = (cid in CLK.from) ? CLK.from[cid] : to;
    const t = 1 - Math.max(0, Math.min(1, CLK.left / CLK.yearMs));
    const e = t * t * (3 - 2 * t);  // smoothstep
    let v = from + (to - from) * e;
    if (CLK.on && !C.done()) v *= 1 + 0.006 * Math.sin(ts / 850 + cid.charCodeAt(0)) +
        0.004 * Math.sin(ts / 310 + cid.length * 7);
    return Math.max(v, 1e-18);
}
function renderChart() {
    const box = $("#chart"), cid = $("#cur").value, nm = $("#chname");
    CH = null;
    if (!cid || !C.alive(cid)) {
        nm.textContent = ""; $("#chlab").textContent = "";
        box.innerHTML = '<div class="dim">通貨を選ぶとライブレートが出る</div>';
        return; }
    const h = (C.HIST[cid] || []).slice();
    const cur = C.price(cid);
    if (!h.length || h[h.length - 1] !== cur) h.push(cur);
    if (h.length < 2) {
        nm.textContent = C.CURS[cid].name; $("#chlab").textContent = "";
        box.innerHTML = '<div class="dim">まだ歴史が浅い。1年進むごとに線が伸びる</div>';
        return; }
    const W = 600, H = 175, P = 10;
    const from = (cid in CLK.from) ? CLK.from[cid] : cur;
    const all = h.concat([from]);
    const lo = Math.min.apply(null, all), hi = Math.max.apply(null, all);
    const l2 = Math.log(Math.max(lo * 0.99, 1e-18));
    const h2 = Math.log(Math.max(hi * 1.01, lo * 1.05, 1e-9));
    const Y = (v) => H - P - ((Math.log(Math.max(v, 1e-18)) - l2) /
        Math.max(h2 - l2, 1e-9)) * (H - 2 * P);
    const X = (i) => P + (i / (h.length - 1)) * (W - 2 * P);
    const pts = h.map((v, i) => [X(i), Y(v)]);
    const up = h[h.length - 1] >= h[0];
    const col = up ? "#ff6b6b" : "#3ecf8e";
    box.innerHTML = '<svg viewBox="0 0 ' + W + " " + H +
        '" preserveAspectRatio="none">' +
        '<polygon id="chfill" points="" fill="' +
        (up ? "rgba(255,107,107,.13)" : "rgba(62,207,142,.13)") + '"/>' +
        '<polyline id="chline" points="" fill="none" stroke="' + col +
        '" stroke-width="2" stroke-linejoin="round"/>' +
        '<circle id="chdot" r="4" fill="' + col + '"/></svg>';
    $("#chlab").textContent = C.yname(C.getState().year - (h.length - 1)) + " 〜 " +
        C.yname(C.getState().year) + "　安 " + C.fmt_g(lo) + " ／ 高 " + C.fmt_g(hi) +
        "/枚　・チャートは決算価格へ滑らか移動中（約定は決算価格）";
    CH = { cid: cid, pts: pts, W: W, H: H, P: P, Y: Y,
        line: box.querySelector("#chline"), fill: box.querySelector("#chfill"),
        dot: box.querySelector("#chdot") };
}
function paintChart(ts) {
    if (!CH) return;
    if (CH.cid !== $("#cur").value) { renderChart(); if (!CH) return; }
    const lv = liveVal(CH.cid, ts);
    const y = Math.max(CH.P, Math.min(CH.H - CH.P, CH.Y(lv)));
    const last = CH.pts.length - 1;
    const pts = CH.pts.map((q, i) => q[0].toFixed(1) + "," +
        (i === last ? y.toFixed(1) : q[1].toFixed(1))).join(" ");
    CH.line.setAttribute("points", pts);
    CH.fill.setAttribute("points", CH.P + "," + (CH.H - CH.P) + " " + pts +
        " " + (CH.W - CH.P) + "," + (CH.H - CH.P));
    CH.dot.setAttribute("cx", CH.pts[last][0].toFixed(1));
    CH.dot.setAttribute("cy", y.toFixed(1));
    $("#chname").textContent = C.CURS[CH.cid].name + "  " + C.fmt_g(lv) + "/枚";
}
function loop(ts) {  // 実時間の心拍。タブ非表示時はほぼ止まる（=自動セーブ的に安全）
    const dt = CLK.prevT ? Math.min(1500, ts - CLK.prevT) : 0;
    CLK.prevT = ts;
    if (C.done() && CLK.on) { CLK.on = false; syncClockUI(); updBar(); }
    if (CLK.on && !C.done()) {
        CLK.left -= dt;
        if (CLK.left <= 0) { CLK.left = CLK.yearMs; run("n 1"); }
        updBar();
    }
    paintChart(ts);
    requestAnimationFrame(loop);
}
function confetti() {
    const ov = $("#overlay");
    for (let i = 0; i < 46; i++) {
        const c = el("i", "cf");
        c.style.left = (Math.random() * 100) + "vw";
        c.style.animationDelay = (Math.random() * 1.4) + "s";
        c.style.background =
            ["#ffd166", "#ef476f", "#06d6a0", "#118ab2", "#ffffff"][i % 5];
        ov.appendChild(c);
        setTimeout(() => c.remove(), 4200); }
}
function endOverlay() {
    const eq = C.equity();
    const allDown = Object.keys(C.BANKS).every((k) => C.BANKS[k].fallen);
    let t, sub, cls;
    if (eq <= 0) { t = "☠ GAME OVER"; sub = "資産が消し飛んだ。歴為替の波に呑まれた"; cls = "over"; }
    else if (allDown) { t = "★★ ALL BANKS DOWN"; sub = "8中央銀行、すべて撃破。あなたは歴史そのものになった"; cls = "clear"; }
    else if (C.getState().year >= 2026) { t = "★ GAME CLEAR";
        sub = "2026年まで生き残った。最終純資産 " + C.fmt_g(eq); cls = "clear"; }
    else { t = "🏳 降参"; sub = "歴史の途中で降りた。最終純資産 " + C.fmt_g(eq); cls = "over"; }
    $("#ovt").textContent = t;
    $("#ovs").textContent = sub;
    $("#overlay").className = "show " + cls;
    if (cls === "clear") confetti();
}
function init() {
    const btn = (id, fn) => $(id).addEventListener("click", fn);
    btn("#n1", () => run("n 1"));
    btn("#nn", () => {  // 翌年送りでニュースが発火するので1年足して見せる
        const n0 = $("#feed").querySelectorAll(".news").length;
        run("n");
        if (!C.done() &&
            $("#feed").querySelectorAll(".news").length === n0) run("n 1"); });
    btn("#n10", () => run("n 10"));
    btn("#n100", () => run("n 100"));
    btn("#qbtn", () => run("q"));
    for (const c of ["b", "ball", "s", "sall", "sh", "cv"])
        btn("#t" + c, () => trade(c));
    for (const sp of SPEEDS) btn("#" + sp[0], () => {
        CLK.yearMs = sp[1]; CLK.left = sp[1]; syncClockUI(); updBar(); });
    btn("#pp", () => {
        if (!C.done()) CLK.on = !CLK.on; syncClockUI(); updBar(); });
    $("#cur").addEventListener("change", () => { renderSheet(); renderChart(); });
    $("#cmd").addEventListener("keydown", (e) => {
        if (e.key === "Enter") run(e.target.value); });
    $("#again").addEventListener("click", () => {
        $("#overlay").className = "";
        $("#feed").innerHTML = ""; $("#log").innerHTML = ""; snap = {};
        CLK.on = true; CLK.left = CLK.yearMs; syncClockUI();
        run("new"); });
    run("new");
    syncClockUI(); updBar();
    requestAnimationFrame(loop);
}
init();
