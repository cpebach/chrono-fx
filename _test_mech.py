import sys
sys.path.insert(0, r"D:/dev/chrono_fx")
import random
random.seed(1)
import chronofx as cf

def fresh(year, silver=50.0):
    cf.S = {"year": year, "silver": silver, "debt": 0.0, "hold": {}, "short": {}}
    for c in cf.CURS.values():
        c["factor"] = 1.0
    for b in cf.BANKS.values():
        b.update(fallen=False, missed=False, attack=False, reserves=b["reserves0"])

# 1) 継承: 両→円
fresh(1871)
cf.S["hold"]["ryo"] = 10.0
cf.year_end(1871)
assert "ryo" not in cf.S["hold"] and cf.S["hold"].get("yen", 0) > 0, "継承失敗"
print("1 継承 両→円 OK 円枚数", round(cf.S["hold"]["yen"], 3))

# 2) 滅亡で現物消滅・売り建て債務もチャラ
fresh(1991)
cf.S["hold"]["srruble"] = 5.0
cf.S["short"]["srruble"] = 3.0
cf.year_end(1991)
assert cf.S["hold"].get("srruble", 0) == 0 and cf.S["short"].get("srruble", 0) == 0
print("2 滅亡処理 OK")

# 3) 継承なし滅亡 = 現物没収
fresh(1865)
cf.S["hold"]["confed"] = 2.0
cf.year_end(1865)
assert cf.S["hold"].get("confed", 0) == 0
print("3 南軍ドル没収 OK")

# 4) 売り攻勢: BoE92 を倒す（1992年・銀3500gの大金持ち）
fresh(1992, 3500.0)
n = 0.6 * cf.BANKS["BoE92"]["reserves0"] / cf.price("pound")
cf.do_short("pound", n, quiet=True)
cf.do_attack("BoE92", quiet=True)
assert cf.BANKS["BoE92"]["attack"]
for y in (1992, 1993):
    cf.advance_to(y + 1)
    print(" ", y, "年末: 準備金", round(cf.BANKS["BoE92"]["reserves"]),
          "純資産", round(cf.equity()), "g")
assert cf.BANKS["BoE92"]["fallen"], "銀行が倒れない"
assert cf.S["short"].get("pound", 0) == 0, "自動決済されていない"
assert cf.equity() > 3500, "攻勢で儲かっていない"
print("4 売り攻勢 BoE92 陥落 OK 最終純資産", round(cf.equity()), "g")

# 5) ウィンドウ外では攻撃できない
fresh(1995, 3500.0)
msg = cf.do_attack("BoE92")
assert msg and not cf.BANKS["BoE92"]["attack"], "窓外の攻撃を許した"
print("5 ウィンドウ外ブロック OK:", msg)

# 6) レバレッジ上限で弾かれる（完全に巻き戻る）
fresh(1990, 10.0)
r = cf.do_buy("usd", 500.0)
assert r and "却下" in r, "上限が効いていない"
assert cf.equity() > 9.9 and cf.S["silver"] == 10.0, "ロールバック不正"
print("6 レバレッジ上限 OK")

# 7) 倒産判定
fresh(2000, 1.0)
cf.S["debt"] = 100.0
assert cf.equity() <= 0
print("7 倒産判定 OK")

print("ALL MECH TESTS PASS")
