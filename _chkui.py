import os, subprocess, sys

W = r"C:/Users/omicron/Desktop/chrono_fx/web"
r = subprocess.run(["node", "--check", "ui.js"], cwd=W,
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print("node --check ui.js rc=", r.returncode, (r.stderr or "").strip()[:400])
sys.exit(r.returncode)
