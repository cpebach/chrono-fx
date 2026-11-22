import subprocess, sys

r = subprocess.run(["node", r"D:\dev\chrono_fx\_rt.js"],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", cwd=r"D:\dev\chrono_fx\web")
print((r.stdout or "").strip())
if r.returncode != 0:
    print((r.stderr or "")[-1500:])
print("rc=", r.returncode)
sys.exit(r.returncode)
