# chronofx.py 本体（途中で切れた草稿）に _p1〜_p10 を継ぎ直し、既知の粗を直す
import io, os, sys

D = r"C:\Users\omicron\Desktop\chrono_fx"
head = io.open(os.path.join(D, "chronofx.py"), encoding="utf-8").read()
mark = "必要銀行が既に倒れてい"
head = head[:head.index(mark)]

body = head + "るとイベントは見送られる（攻勢で既に実現済み）\n"
for i in range(1, 11):
    body += io.open(os.path.join(D, f"_p{i}.txt"), encoding="utf-8").read()

def rep(a, b, must=True):
    global body
    if a not in body:
        if must:
            sys.exit("見つからない置換: " + a[:60])
        return
    body = body.replace(a, b)

# --- 表記ゆれ・誤字 -----------------------------------------------------
rep("金本位放弃", "金本位を放弃")
rep("放弃", "放棄")
rep('"奥地利グールデン"', '"オーストリア・グールデン"')
rep('(2022, "rub2",', '(2022, "ruble2",')
rep('(1998, "ruble2", 0.3, "ロシア、デフォルト。GKO、紙屑"),',
    '(1998, "ruble2", 0.3, "ロシア、デフォルト。GKO、紙屑", "CBR98"),')
rep('(2008, "zdw", 1e-4, "ジンバブエ、100兆紙幣発行。100兆でバス1回分"),',
    '(2008, "zdw", 1e-4, "ジンバブエ、100兆紙幣発行。100兆でバス1回分", "RBZ08"),')

# --- do_buy / do_short のロールバックをスナップショット式に ----------------
rep('''    eq0 = equity()
    qty = g * (1 - FEE) / price(cid)
    S["silver"] -= g''',
    '''    snap = (S["silver"], S["debt"])
    qty = g * (1 - FEE) / price(cid)
    S["silver"] -= g''')
rep('''        S["hold"][cid] -= qty
        S["silver"] += g
        S["debt"] = max(S["debt"] - g, 0.0)
        _repay_debt()
''',
    '''        S["hold"][cid] -= qty
        S["silver"], S["debt"] = snap
''')
rep('''    g = n * price(cid)
    eq0 = equity()
    S["short"][cid] = S["short"].get(cid, 0.0) + n''',
    '''    g = n * price(cid)
    snap = (S["silver"], S["debt"])
    S["short"][cid] = S["short"].get(cid, 0.0) + n''')
rep('''        S["short"][cid] -= n
        S["silver"] -= g * (1 - FEE)
        _repay_debt()
''',
    '''        S["short"][cid] -= n
        S["silver"], S["debt"] = snap
''')

# --- b all = 手持ち銀を全部使う（売り持ち価値と混同していた） --------------
rep('''        amt = parse_amt(tokens[2])
        cid = tokens[1]
        if cid not in CURS:
            print("その通貨は無い（l で一覧）")
            return None
        g = S["silver"] if amt == "all" else amt
        if amt == "all" and S["hold"].get(cid, 0) > 0:
            g = S["hold"][cid] * price(cid)
        if amt == "all":
            g = max(g, 0)
        err = do_buy(cid, g if isinstance(g, float) else 0.0, quiet)''',
    '''        amt = parse_amt(tokens[2])
        cid = tokens[1]
        if cid not in CURS:
            print("その通貨は無い（l で一覧）")
            return None
        if amt is None:
            print("g数は数字か all で")
            return None
        g = S["silver"] if amt == "all" else amt
        err = do_buy(cid, g, quiet)''')

# --- 攻勢中の通貨は予定されている暴落イベントを発火させない ----------------
rep('''    if nb and BANKS[nb]["fallen"]:
        return [f"▶ {yname(y)} {head}''',
    '''    if nb and BANKS[nb]["attack"]:
        return []
    if nb and BANKS[nb]["fallen"]:
        return [f"▶ {yname(y)} {head}''')

# --- 大晦日に攻勢の決着も処理する -----------------------------------------
rep('''    for cid in [k for k, v in CURS.items() if v["y1"] == y]:''',
    '''    for bid in [k for k, b in BANKS.items() if b["attack"]]:
        settle_attack(bid, out)
    for cid in [k for k, v in CURS.items() if v["y1"] == y]:''')

# --- 通貨死亡は攻勢決着の後でも良いが、準備金枯渇→暴落の順が自然なので入れ替え不要 --
io.open(os.path.join(D, "chronofx.py"), "w", encoding="utf-8").write(body)
print("stitched:", len(body.splitlines()), "lines")
import py_compile
py_compile.compile(os.path.join(D, "chronofx.py"), doraise=True)
print("compile OK")
