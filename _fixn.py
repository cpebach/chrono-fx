import io, py_compile
p = r"C:/Users/omicron/Desktop/chrono_fx/chronofx.py"
s = io.open(p, encoding="utf-8").read()
a = '''        if raw.lower().startswith("n"):
            ny = END_YEAR
            if len(raw) > 1:'''
b = '''        if raw.lower().startswith("n"):
            ny = next_news_year()
            if len(raw) > 1:'''
assert a in s
io.open(p, "w", encoding="utf-8").write(s.replace(a, b))
py_compile.compile(p, doraise=True)
print("bare-n fix OK")
