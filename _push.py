import os, subprocess, sys, zipfile

ROOT = r"C:/Users/omicron/Desktop/chrono_fx"
z = zipfile.ZipFile(os.path.join(ROOT, "dist", "chrono-fx.apk"))
names = z.namelist()
for need in ("classes.dex", "assets/index.html", "assets/ui.js",
             "assets/style.css", "assets/game.js", "assets/data.js"):
    assert need in names, "APK missing " + need
print("APK assets OK:", [n for n in names if n.startswith("assets/")])

def run(args):
    r = subprocess.run(args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=ROOT)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    print("$", " ".join(args[:2]), "rc=", r.returncode)
    if out:
        print(out[-700:])
    if r.returncode != 0:
        sys.exit("FAILED " + str(args))
    return r

run(["git", "add", "-A"])
msg = ("GUI版: 速報フィード付きニュース/相場のティッカー/中銀ダッシュボード\n\n"
       "- ニュースは新聞風カードでスライドイン、陥落は画面シェイク+拡大テキスト\n"
       "- 純資産スパークライン、通貨カードの価格履歴スパークライン\n"
       "- 相場ティッカー(マーキー)、レバレッジバー、売り攻勢ボタン\n"
       "- GAME OVER/CLEARオーバーレイ(クリア時は紙吹雪)\n"
       "UI追加は ui.js/style.css のみでゲームエンジンのRulesは無変更")
r = subprocess.run(["git", "commit", "-m",
                    msg + "\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>"],
                   capture_output=True, text=True,
                   encoding="utf-8", errors="replace", cwd=ROOT)
print("commit rc=", r.returncode)
print(((r.stdout or "") + (r.stderr or ""))[-500:])
run(["git", "push", "origin", "main"])
run(["git", "log", "--oneline", "-3"])
print("PUSHED")
