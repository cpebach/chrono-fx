import subprocess, sys

ROOT = r"D:\dev\chrono_fx"

def run(args):
    r = subprocess.run(args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=ROOT)
    print("$", " ".join(args[:3]), "rc=", r.returncode)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    if out:
        print(out[-400:])
    if r.returncode != 0:
        sys.exit("FAILED")
    return r

run(["git", "add", "-A"])
r = subprocess.run(["git", "commit", "-m",
                    "chore: Whittle環境用スクリプトの混入を解消・READMEにリアルタイム進行を追記\n\n"
                    "Co-Authored-By: Claude Code <noreply@anthropic.com>"],
                   capture_output=True, text=True,
                   encoding="utf-8", errors="replace", cwd=ROOT)
print("commit rc=", r.returncode, ((r.stdout or "") + (r.stderr or ""))[-300:])
run(["git", "push", "origin", "main"])
print("OK")
