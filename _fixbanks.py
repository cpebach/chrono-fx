import io, py_compile
p = r"C:/Users/omicron/Desktop/chrono_fx/chronofx.py"
s = io.open(p, encoding="utf-8").read()
a = '''def do_attack(bid, quiet=False):'''
b = '''def show_banks():
    print("売り攻勢の標的（条件: ウィンドウ内の年であること、"
          "対象の売り建てが準備金の半分以上）:")
    print(banks_line())
    print(" a <ID> で攻勢開始 / x <ID> で中止。準備金が尽きると通貨を撃墜、"
          "売り建ては安値で自動決済され戦利品が入る")

def do_attack(bid, quiet=False):'''
assert a in s and "def show_banks" not in s
io.open(p, "w", encoding="utf-8").write(s.replace(a, b, 1))
py_compile.compile(p, doraise=True)
print("show_banks added")
