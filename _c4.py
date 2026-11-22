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
                    "feat: リアルタイム進行(既定1年=30秒)とライブチャート\n\n"
                    "- 年時計: rAFループで自動1年経過。速度60/30/10/3秒と一時停止\n"
                    "- 決算価格へ滑らか補間+微揺動で先端が毎フレーム動く\n"
                    "- 終了時自動停止、手動送りでカウントダウン再調整\n"
                    "- _rt.js/_rt.py: ヘッドレス時計スモーク追加\n\n"
                    "Co-Authored-By: Claude Code <noreply@anthropic.com>"],
                   capture_output=True, text=True,
                   encoding="utf-8", errors="replace", cwd=ROOT)
print("commit rc=", r.returncode, ((r.stdout or "") + (r.stderr or ""))[-300:])
run(["git", "push", "origin", "main"])
print("OK")
