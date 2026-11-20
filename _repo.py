import glob, os, subprocess, sys, zipfile

ROOT = r"C:/Users/omicron/Desktop/chrono_fx"
z = zipfile.ZipFile(os.path.join(ROOT, "dist", "chrono-fx.apk"))
names = z.namelist()
print("APK entries:", names)
assert "classes.dex" in names and "assets/game.js" in names

def run(args, check=True):
    r = subprocess.run(args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=ROOT)
    print("$", args[0].split(os.sep)[-1], args[1:4], "rc=", r.returncode)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    if out:
        print(out[-800:])
    if check and r.returncode != 0:
        sys.exit("FAILED " + str(args))
    return r

for f in glob.glob(os.path.join(ROOT, "_p*.txt")) + glob.glob(os.path.join(ROOT, "_w*.js")):
    os.remove(f)
    print("removed", os.path.basename(f))

auth = run(["gh", "auth", "status"], check=False)
login = run(["gh", "api", "user", "--jq", ".login"], check=False).stdout.strip()
print("gh login:", login or "-")
if not os.path.isdir(os.path.join(ROOT, ".git")):
    run(["git", "init", "-b", "main"])
if login:
    run(["git", "config", "user.name", login])
    run(["git", "config", "user.email", f"{login}@users.noreply.github.com"])
else:
    run(["git", "config", "user.name", "chrono-fx"])
    run(["git", "config", "user.email", "chrono-fx@localhost"])
run(["git", "add", "-A"])
run(["git", "commit", "-m",
     "CHRONO FX: CLI/Web/APK 一式（通貨64種・中銀8行・ニュース147本）"])
run(["git", "log", "--oneline"])
if login:
    r = subprocess.run(["gh", "repo", "create", "chrono-fx", "--public",
                        "--source", ".", "--push"], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", cwd=ROOT)
    print("create rc=", r.returncode)
    print(((r.stdout or "") + (r.stderr or ""))[-600:])
    if r.returncode == 0:
        v = run(["gh", "repo", "view", "chrono-fx", "--json", "url", "-q", ".url"])
        print("REPO_URL:", v.stdout.strip())
