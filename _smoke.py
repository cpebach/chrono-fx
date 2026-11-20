import os, subprocess, sys

PY = sys.executable
GAME = r"C:/Users/omicron/Desktop/chrono_fx/chronofx.py"
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
script = "\n".join([
    "p",                # -700年の相場
    "b electrum 30",    # エレクトロン貨を買う
    "n",                # 前594年のソロン不安へ
    "w",                # 資産
    "s electrum all",   # 全部売って銀へ
    "n 400",            # -194年あたりまで一気に
    "l",                # 一覧
    "sh owl 5",         # 死んだ通貨の売り建ては弾かれる
    "bank",             # 標的一覧
    "a BoE1931",        # まだ早いはず
    "b denarius 99999", # レバレッジ上限に弾かれるはず
    "b denarius 20",    # 正常な買い
    "h",
    "q",
])
r = subprocess.run([PY, GAME], input=script, capture_output=True,
                   text=True, timeout=120, encoding="utf-8",
                   errors="replace", env=ENV)
print(r.stdout[-4200:])
if r.returncode != 0 or r.stderr.strip():
    print("STDERR:", r.stderr[-600:])
    print("rc=", r.returncode)
