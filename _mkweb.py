import io, json, os, sys

ROOT = r"C:/Users/omicron/Desktop/chrono_fx"
WEB = os.path.join(ROOT, "web")
sys.path.insert(0, ROOT)
import chronofx as C

data = {"cur": [list(c) for c in C.CUR_DEFS],
        "bank": [list(b) for b in C.BANK_DEFS],
        "events": [list(e) + [None] * (5 - len(e)) for e in C.EVENTS]}
js = "globalThis.DATA = " + json.dumps(data, ensure_ascii=False) + ";\n"
io.open(os.path.join(WEB, "data.js"), "w", encoding="utf-8").write(js)
print("data.js", len(data["cur"]), "curs,", len(data["bank"]), "banks,",
      len(data["events"]), "events,", os.path.getsize(os.path.join(WEB, "data.js")), "bytes")

parts = []
for i in range(1, 11):
    p = os.path.join(WEB, f"_w{i}.js")
    parts.append(io.open(p, encoding="utf-8").read())
out = "\n".join(parts)
gp = os.path.join(WEB, "game.js")
io.open(gp, "w", encoding="utf-8").write(out)
print("game.js", os.path.getsize(gp), "bytes")
for i in range(1, 11):
    os.remove(os.path.join(WEB, f"_w{i}.js"))
print("chunks removed")
