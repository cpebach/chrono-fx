import io, py_compile
p = r"C:/Users/omicron/Desktop/chrono_fx/chronofx.py"
s = io.open(p, encoding="utf-8").read()

def rep(a, b):
    global s
    assert a in s, "not found: " + a[:50]
    s = s.replace(a, b)

rep("4000.0, 1e-6", "1000.0, 1e-6")      # RBZ08
rep("20000.0, 0.66", "6000.0, 0.66")     # BoE1931
rep("5000.0, 1e-8", "1500.0, 1e-8")      # NBY1992
rep("30000.0, 0.75", "8000.0, 0.75")     # BoE92
rep("15000.0, 0.45", "4000.0, 0.45")     # Banxico94
rep("12000.0, 0.5", "3000.0, 0.5")       # BOT97
rep("10000.0, 0.3", "2500.0, 0.3")       # CBR98
rep("12000.0, 0.6", "3000.0, 0.6")       # BCRA01
rep('売り持ちが準備金の5%以上', '売り持ちが準備金の2%以上')
rep('0.05 * b["reserves"]', '0.02 * b["reserves"]')
rep('0.06 * b["reserves"]', '0.025 * b["reserves"]')

io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("rebalanced OK")
