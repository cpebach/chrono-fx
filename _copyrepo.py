import os, shutil, subprocess, sys

SRC = r"D:\dev\chrono_fx"
DST = r"D:\dev\chrono_fx"
if os.path.exists(DST):
    sys.exit("DST exists already: " + DST)

def ignore(dirpath, names):
    return {n for n in names if n in ("__pycache__", "build") or n.endswith(".pyc")}

shutil.copytree(SRC, DST, ignore=ignore)
print("copied ->", DST)

n = 0
for root, _, files in os.walk(DST):
    if ".git" in root:
        continue
    for f in files:
        if not f.endswith((".py", ".md", ".bat")):
            continue
        p = os.path.join(root, f)
        t = open(p, encoding="utf-8", errors="replace").read()
        t2 = (t.replace(r"D:/dev/chrono_fx", "D:/dev/chrono_fx")
               .replace(r"D:\dev\chrono_fx", r"D:\dev\chrono_fx"))
        if t2 != t:
            open(p, "w", encoding="utf-8").write(t2)
            n += 1
print("path-updated files:", n)

def run(args):
    r = subprocess.run(args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=DST)
    print("$", " ".join(args[:3]), "rc=", r.returncode)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    if out:
        print(out[-500:])
    if r.returncode != 0:
        sys.exit("FAILED " + str(args))
    return r

run(["git", "log", "--oneline", "-2"])
run(["git", "status", "--short"])
