import os, subprocess, sys

WEB = r"D:/dev/chrono_fx/web"
r = subprocess.run(["node", "--check", os.path.join(WEB, "game.js")],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", cwd=WEB)
print("syntax rc=", r.returncode, (r.stderr or "")[-400:])
r = subprocess.run(["node", os.path.join(WEB, "_htest.js")],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", cwd=WEB)
print("test rc=", r.returncode)
print((r.stdout or "")[-500:])
print((r.stderr or "")[-500:])
sys.exit(r.returncode)
