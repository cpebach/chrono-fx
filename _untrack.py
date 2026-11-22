import subprocess, os, sys

ROOT = r"D:\dev\chrono_fx"
WHITTLE = ["_env1.py", "_env2.py", "_env3.py", "_env4.py", "_env5.py", "_env6.py",
           "_try.py", "_probe.py", "_ggufinfo.py", "_relassets.py", "_hfget.py",
           "_port.py", "_lookd.py", "_lookdev.py"]
for f in WHITTLE:
    dup = os.path.exists(os.path.join(r"D:\whittle-next-27b\scripts", f))
    assert dup, "not saved elsewhere: " + f
r = subprocess.run(["git", "rm", "-q", "--cached", "--"] + WHITTLE,
                   capture_output=True, text=True, cwd=ROOT)
print("rm --cached rc=", r.returncode, r.stderr[-200:])
for f in WHITTLE:
    p = os.path.join(ROOT, f)
    if os.path.exists(p):
        os.remove(p)
print("removed from repo & local; whittle-side copies intact")
