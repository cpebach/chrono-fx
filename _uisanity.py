import re

W = r"C:/Users/omicron/Desktop/chrono_fx/web"
html = open(W + "/index.html", encoding="utf-8").read()
ui = open(W + "/ui.js", encoding="utf-8").read()
css = open(W + "/style.css", encoding="utf-8").read()
ids = set(re.findall(r'id="([^"]+)"', html))
used = set(re.findall(r'\$\("#([\w-]+)"\)', ui)) | set(
    re.findall(r'btn\("#([\w-]+)"', ui))
missing = used - ids
if '"#t" + c' in ui:
    missing.discard("t")  # 実行時に tb/tball/ts/tsall/tsh/tcv へ展開される
print("html ids:", len(ids), "ui refs:", len(used), "missing:", sorted(missing) or "-")
assert not missing, missing
cls = set(re.findall(r'class="([\w \-]+)"', ui))
for c in "news banner bigfall cf tick ti hcard brow atk mini show over clear shake fl-up fl-dn".split():
    assert c in css, "css missing class " + c
# index.html must load all three scripts
for s in ("data.js", "game.js", "ui.js"):
    assert s in html, "script missing " + s
assert "style.css" in html
print("UI SANITY OK")
