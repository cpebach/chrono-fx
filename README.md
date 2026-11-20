# CHRONO FX 〜エレクトロン・スタンダード〜

紀元前700年（リディアのエレクトロン貨）から2026年まで、**1年1コマ**で歴史の
為替を殴り合う終末FXゲーム。ニュース（実在イベント下敷き・約147本）を
読んで通貨を売買し、資産を増やし、中央銀行を倒す。

## あそびかた

### CLI（Python のみで動く）
```
python chronofx.py              # 対話プレイ（紀元前700年から）
python chronofx.py --bot 3000   # 自動売買Botに3000手ぶん任せて観戦
python chronofx.py --seed 7     # 乱数しぼり出し（--bot と併用可）
```

### Web / Android
- `web/` をブラウザで開くだけ（`web/index.html`、外部依存ゼロ）
- `dist/chrono-fx.apk` を Android にインストール（minSdk 21）

### コマンド
| cmd | 内容 | cmd | 内容 |
|---|---|---|---|
| `b <通貨> <g数\|all>` | 買う（銀が足りれば自動借入） | `s <通貨> [g数\|all]` | 売る |
| `sh <通貨> <枚数>` | 売り建て | `cv <通貨> <枚数\|all>` | 買い戻し |
| `a <銀行ID>` | 売り攻勢開始 | `x <銀行ID>` | 攻勢中止 |
| `n [年数]` | 次のニュースまで（または n 年） | `p / l / w / bank` | 相場/一覧/資産/標的 |

## ゲームルール
- 単位は銀グラム。**手数料0.3%**、総エクスポジール≤**純資産の10倍**、銀借入に年2%
- 通貨64種。登場・滅亡あり。**継承通貨があれば時価のまま自動交換**、
  継承なく滅んだ国家の通貨の現物は没収、売り建ては債務ごと消滅
- **中央銀行売り攻勢**: 攻撃ウィンドウ内で売り建てが準備金の半分以上だと `a` 可能。
  防衛（年+8%買い支え・売り建てに年6%利子）と準備金枯渇の綱引き。
  落城で通貨は暴落し、売り建ては安値で自動決済＋戦利品（準備金の3%）
- **GAME OVER**: 純資産≤0 / **CLEAR**: 2026年生存 または 8中銀すべて撃破

## ビルド
- `python _mkweb.py` … `chronofx.py` から `web/data.js` を生成し `web/game.js` を合成
- `python _buildapk.py` … aapt2/javac/d8/zipalign/apksigner で APK 署名ビルド
  （JDK17 と Android SDK build-tools 34 が必要。`_android_setup.py` で一括導入可）

## テスト
- `python _test_mech.py` … CLI版メカニクス7検証
- `python _runbots.py` … Bot 5シード×2726年フルタイムライン通し
- `python _testweb.py` … Web/APKエンジン移植版の node 検証（継承・BoE92撃破・破産）

ライセンス: MIT
