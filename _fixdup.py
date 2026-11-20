import io, py_compile, sys
p = r"C:/Users/omicron/Desktop/chrono_fx/chronofx.py"
s = io.open(p, encoding="utf-8").read()
dup = "攻勢で既に実現済み）\nるとイベントは見送られる（攻勢で既に実現済み）\nEVENTS"
if dup not in s:
    sys.exit("想定外の状態: " + repr(s[s.index("実現済み") - 20:s.index("実現済み") + 60]))
s = s.replace(dup, "攻勢で既に実現済み）\nEVENTS")
io.open(p, "w", encoding="utf-8").write(s)
py_compile.compile(p, doraise=True)
print("dup removed, compile OK,", len(s.splitlines()), "lines")
