import os, subprocess, sys

W = r"C:/Users/omicron/Desktop/chrono_fx/web"
parts = {
    "ui.js": ["_u1.js", "_u2.js", "_u3.js", "_u4.js", "_u5.js"],
    "style.css": ["_c1.css", "_c2.css", "_c3.css", "_c4.css"],
}
for out, chunks in parts.items():
    buf = ""
    for c in chunks:
        p = os.path.join(W, c)
        with open(p, encoding="utf-8") as f:
            buf += f.read().rstrip("\n") + "\n"
    with open(os.path.join(W, out), "w", encoding="utf-8") as f:
        f.write(buf)
    print(out, len(buf), "bytes from", len(chunks), "chunks")
r = subprocess.run(["node", "--check", "ui.js"], cwd=W,
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print("node --check ui.js rc=", r.returncode)
if r.returncode:
    sys.exit((r.stdout or "") + (r.stderr or ""))
for cl in sum(parts.values(), []):
    os.remove(os.path.join(W, cl))
print("chunks removed. UI build OK")
