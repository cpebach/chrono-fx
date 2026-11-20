import io, py_compile
p = r"C:/Users/omicron/Desktop/chrono_fx/chronofx.py"
s = io.open(p, encoding="utf-8").read()

def rep(a, b):
    global s
    assert a in s, "not found: " + a[:50]
    s = s.replace(a, b)

# 攻勢の決着が攻撃窓（1〜2年）に間に合うよう、必要売り建てを「準備金の半分以上」に。
# 準備金の減り 約1.6倍/年 × 半分 ≈ 1.3年で枯れる計算。
rep("売り持ちが準備金の2%以上", "売り建てが準備金の半分以上")
rep('0.02 * b["reserves"]', '0.5 * b["reserves"]')
rep('0.025 * b["reserves"]', '0.55 * b["reserves"]')

io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("threshold -> 50% OK")
