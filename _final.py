import os, shutil, subprocess, sys

PY = sys.executable
GAME = r"C:/Users/omicron/Desktop/chrono_fx/chronofx.py"
r = subprocess.run([PY, "-m", "py_compile", GAME], capture_output=True, text=True)
print("compile rc=", r.returncode)
r = subprocess.run([PY, GAME, "--bot", "3000", "--seed", "7"],
                   capture_output=True, text=True, timeout=180,
                   encoding="utf-8", errors="replace")
lines = (r.stdout or "").splitlines()
print("bot rc=", r.returncode)
for l in lines:
    if any(k in l for k in ("GAME", "倒した銀行", "経過")):
        print(l.strip())
dst = r"C:/Users/omicron/discord-claude-bridge/media/chronofx.py"
shutil.copyfile(GAME, dst)
print("copied ->", dst, os.path.getsize(dst), "bytes")
