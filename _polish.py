import io, py_compile
p = r"C:/Users/omicron/Desktop/chrono_fx/chronofx.py"
s = io.open(p, encoding="utf-8").read()

def rep(a, b):
    global s
    assert a in s, "not found: " + a[:60]
    s = s.replace(a, b)

rep('''    if not (b["y0"] <= S["year"] <= b["y1"]):
        return f"まだ早い（攻撃可能は {yname(b['y0'])}〜{yname(b['y1'])}）"''',
    '''    if not (b["y0"] <= S["year"] <= b["y1"]):
        if S["year"] > b["y1"]:
            return f"その機会（きかい）は過ぎた（攻撃可能は {yname(b['y0'])}〜{yname(b['y1'])}）"
        return f"まだ早い（攻撃可能は {yname(b['y0'])}〜{yname(b['y1'])}）"''')

# Bot が手数料ですり減りすぎないよう、売買を控えめに
rep("    if random.random() < 0.30:\n        return",
    "    if random.random() < 0.55:\n        return")
rep("S[\"silver\"] * random.uniform(0.2, 0.6)",
    "S[\"silver\"] * random.uniform(0.1, 0.35)")

io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("polish OK")
