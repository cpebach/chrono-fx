# -*- coding: utf-8 -*-
"""CHRONO FX 〜エレクトロン・スタンダード〜

紀元前700年（エレクトロン貨）から2026年まで、1年1コマで為替を殴り合う終末FX端末。

使い方:
    python chronofx.py              ... 対話プレイ（紀元前700年から）
    python chronofx.py --bot 3000   ... 自動売買Botに3000手ぶん任せて観戦
    python chronofx.py --seed 7     ... 乱数しぼり出し（--bot と併用可）

コマンド（ゲーム中）:
    b <通貨> <g数|all>   銀gと交換に買う（手持ち銀が足りなければ借金＝レバレッジ）
    s <通貨> <g数|all>   売る
    sh <通貨> <本数>     売り建て（先に売って後に買い戻す）
    cv <通貨> <本数|all> 売り建てを買い戻す
    a <銀行ID>           その中央銀行へ売り攻勢（条件: ウィンドウ内・売り建てが準備金の半分以上）
    x <銀行ID>           攻勢を中止する
    l / p / w            通貨一覧 / 相場 / 資産明細
    n [年数]             次のニュースまで（または n 年）進める
    h                    ヘルプ    q 中断
勝つには: 2026年まで破産せず生き残るか、8つの中央銀行をすべて倒す。
国家ととも滅んだ通貨の現物持ちは消え、売り建ては債務ごとチャラになる。
"""
import random
import sys

FEE = 0.003          # 片道手数料 0.3%
LEV = 10.0           # 総エクスポジールの上限（純資産の10倍）
INTR = 0.02          # 銀借金の利子（年2%）
ATT_INTR = 0.06      # 攻勢中の売り建てに中銀が課す利子（年6%）
DRIFT = 0.995        # 1971年以降の紙幣の年間経年劣化
START_YEAR, END_YEAR = -700, 2026
START_SILVER = 50.0
START_SHORT = 1.0    # 攻勢判定に使う「攻勢開始前の売り残」の種火

# ---- 通貨 ------------------------------------------------------------------
# (ID, 和名, 開始年, 終了年, 継承先, 1枚=銀g(額面), 体制 g=貴金属本位 f=紙幣)
CUR_DEFS = [
    ("electrum",  "エレクトロン貨",       -700,  -546, "daric",     4.5, "g"),
    ("daric",     "ダレイコス",           -546,  -330, None,        5.4, "g"),
    ("owl",       "ふくろう銀貨",         -510,  -330, None,        4.3, "g"),
    ("carthage",  "カルタゴ銀貨",         -500,  -146, None,        7.2, "g"),
    ("denarius",  "デナリウス",           -268,   312, None,        4.5, "g"),
    ("aureus",    "アウレウス",            -27,   312, "solidus",   7.8, "g"),
    ("solidus",   "ソリドゥス",            309,  1092, "hyperpyron", 4.4, "g"),
    ("hyperpyron","ヒュペルピュロン",     1092,  1453, None,        3.2, "g"),
    ("dinar",     "ウマイヤ・ディナール",  693,  1258, None,        4.25,"g"),
    ("dirham",    "アッバース朝ディルハム", 700,  1258, None,        2.97,"g"),
    ("wuzhu",     "五銖銭",               -118,   621, "kaiyuan",   3.0, "g"),
    ("kaiyuan",   "開元通宝",              621,   907, None,        3.85,"g"),
    ("baochao",   "至元宝鈔",             1260,  1367, None,        3.0, "f"),
    ("mingnotes", "洪武宝鈔",             1375,  1425, None,        3.0, "f"),
    ("florin",    "フィオリーノ",         1252,  1533, None,        3.5, "g"),
    ("genovino",  "ゲノビーノ",           1139,  1797, None,        3.5, "g"),
    ("thaler",    "ターラー銀貨",         1520,  1900, None,       29.2, "g"),
    ("escudo",    "スペイン・エスクード", 1537,  1868, "peseta",    3.4, "g"),
    ("real8",     "8レアル銀貨",          1497,  1898, "usd",      25.6, "g"),
    ("assignat",  "アッシニュ",           1789,  1796, None,        5.0, "f"),
    ("continental","大陸紙幣",            1776,  1788, None,       25.0, "f"),
    ("ryo",       "両",                   1603,  1871, "yen",      17.0, "g"),
    ("pound",     "ポンド・スターリング", 1694,  2026, None,       24.4, "g"),
    ("usd",       "アメリカドル",         1792,  2026, None,       24.0, "g"),
    ("greenback", "緑背紙幣",             1862,  1879, "usd",      21.0, "f"),
    ("confed",    "南軍ドル",             1861,  1865, None,       21.0, "f"),
    ("franc",     "ジェルミナル・フラン", 1803,  1959, "newfranc",  5.0, "g"),
    ("newfranc",  "新フラン",             1960,  2001, "euro",      5.0, "f"),
    ("yen",       "日本円",               1871,  2026, None,       24.3, "g"),
    ("mark",      "ドイツマルク(金)",     1871,  1924, "rentenmark", 10.0,"g"),
    ("rentenmark","レンテンマルク",       1924,  1948, "dmark",     10.0, "g"),
    ("dmark",     "ドイツマルク",         1948,  2001, "euro",      10.0, "f"),
    ("gulden",    "オーストリア・グールデン",     1753,  1892, "crown",      9.0, "g"),
    ("crown",     "クローネ",             1892,  1924, "schilling", 10.0, "g"),
    ("schilling", "オーストリア・シリング",1925, 2001, "euro",      10.0, "f"),
    ("ruble",     "ロシア・ルーブル",     1714,  1922, "srruble",   18.0, "g"),
    ("srruble",   "ソ連ルーブル",         1923,  1991, None,        18.0, "f"),
    ("ruble2",    "ロシア・ルーブル(新)", 1992,  2026, None,         5.0, "f"),
    ("ottoman",   "オスマン・リラ",       1844,  1922, "tlira",      7.0, "g"),
    ("tlira",     "トルコ・リラ",         1923,  2026, None,         5.0, "f"),
    ("drachma",   "ギリシャ・ドラクマ",   1832,  2001, "euro",       0.35,"g"),
    ("lira",      "イタリア・リレラ",     1862,  2001, "euro",       0.22,"g"),
    ("peseta",    "スペイン・ペセタ",     1868,  2001, "euro",       1.0, "g"),
    ("pescudo",   "ポルトガル・エスクード",1911, 2001, "euro",       4.0, "g"),
    ("guilder",   "オランダ・グルデン",   1816,  2001, "euro",      10.0, "g"),
    ("bfranc",    "ベルギー・フラン",     1832,  2001, "euro",       5.0, "g"),
    ("krona",     "クローナ",             1873,  2026, None,         2.0, "f"),
    ("chf",       "スイス・フラン",       1850,  2026, None,         5.0, "f"),
    ("rupee",     "インド・ルピー",       1862,  2026, None,        10.0, "g"),
    ("tael",      "銀両",                 1000,  1933, None,        37.0, "g"),
    ("fabi",      "法幣",                 1935,  1948, None,        10.0, "f"),
    ("goldyuan",  "金円券",               1948,  1949, None,        10.0, "f"),
    ("cny",       "人民元",               1949,  2026, None,        10.0, "f"),
    ("pengo",     "ハンガリー・ペンゲ",   1927,  1946, "forint",     4.0, "g"),
    ("forint",    "ハンガリー・フォリント",1946, 2026, None,         2.0, "f"),
    ("yudinar",   "ユーゴスラヴィア・ディナール",1918,2003,None,     5.0, "f"),
    ("pesomx",    "メキシコ・ペソ",       1863,  2026, None,        25.0, "g"),
    ("apeso",     "アルゼンチン・ペソ",   1881,  2026, None,         5.0, "f"),
    ("baht",      "タイ・バーツ",         1902,  2026, None,        15.0, "g"),
    ("rupiah",    "インドネシア・ルピア", 1946,  2026, None,         1.0, "f"),
    ("won",       "韓国ウォン",           1953,  2026, None,         1.0, "f"),
    ("hryvnia",   "ウクライナ・フリヴニャ",1996,  2026, None,         1.0, "f"),
    ("zdw",       "ジンバブエ・ドル",     1980,  2009, None,         1.0, "f"),
    ("euro",      "ユーロ",               1999,  2026, None,        12.0, "f"),
]
CURS = {c[0]: {"name": c[1], "y0": c[2], "y1": c[3], "succ": c[4],
               "base": c[5], "regime": c[6], "factor": 1.0} for c in CUR_DEFS}

# ---- 中央銀行（売り攻勢の標的） ---------------------------------------------
# (ID, 対象通貨, ウィンドウ開始, 終了, 準備金(銀g), 成功時の暴落係数)
BANK_DEFS = [
    ("BoE1931",    "pound",   1929, 1931, 6000.0, 0.66),  # 金本位制復帰ポンドの大暴落
    ("NBY1992",    "yudinar", 1992, 1993,  1500.0, 1e-8),  # 社会主義最期の固定相場
    ("BoE92",      "pound",   1992, 1993, 8000.0, 0.75),  # 暗黒水曜日（ERM）
    ("Banxico94",  "pesomx",  1994, 1995, 4000.0, 0.45),  # テキーラ・クライシス
    ("BOT97",      "baht",    1997, 1998, 3000.0, 0.5),   # アジア通貨危機
    ("CBR98",      "ruble2",  1998, 1999, 2500.0, 0.3),   # ロシア債務不履行
    ("BCRA01",     "apeso",   2001, 2002, 3000.0, 0.6),   # コラルィート（ペソ交換禁止）
    ("RBZ08",      "zdw",     2008, 2009,  1000.0, 1e-6),  # ハイパーインフレ最終形
]
BANKS = {b[0]: {"cur": b[1], "y0": b[2], "y1": b[3], "reserves0": b[4],
                "reserves": b[4], "deval": b[5], "fallen": False,
                "missed": False, "attack": False} for b in BANK_DEFS}

# ---- ニュース ---------------------------------------------------------------
# ニュースなしでも世の中はちゃんと動く: (年, 通貨, 係数, 見出し=None, 必要銀行=None)
# 係数>1 は上昇(▲)。るとイベントは見送られる（攻勢で既に実現済み）
EVENTS = [
(-594, "electrum", 0.90, "ソロン、アテナイで債務解除「負債は土の下に眠れ」"),
(-550, "electrum", 1.25, "クロイソス王の鋳造所が開通「金、幾らでも」"),
(-546, "daric", 1.2, "リュディアを呑んだペルシア、黄金のダレイコスを量産"),
(-432, "owl", 1.15, "パルテノン神殿、デロス同盟の銀で飾り立てられる"),
(-413, "owl", 0.6, "シチリア遠征、アテナイ艦隊が消える。銀も消える"),
(-396, "owl", 0.5, "スパルタ、ケケリアの銀山を占領。ふくろう、飢える"),
(-330, "daric", 0.3, "ペルセポリス焼ける。ダレイコス、征服者に拾われず"),
(-330, "owl", 0.4, "アテナイ降伏。ふくろう銀貨、ただの銀になる"),
(-268, "denarius", 1.3, "ローマ、デナリウス発行開始。1デナリウス=10アス"),
(-218, "carthage", 0.6, "ハンニバル、イタリアへ。カルタゴの銀も一緒に"),
(-146, "carthage", 0.01, "カルタゴ滅びる。塩を蒔かれた更地に硬貨は無い"),
(-146, "denarius", 1.3, "コリントス炎上。地中海の銀はローマへ"),
(-84, "denarius", 0.8, "スラ、アテネを略奪。銀はローマへ"),
(-64, "denarius", 0.85, "ネロ、デナリウスの品位を下げる。哲学より鋳造"),
(64, "denarius", 0.7, "ローマ大火。ネロ、再建工事費を銀の目減りで調達"),
(193, "denarius", 0.7, "ディディウス、帝国を競売で落とす。当然値引き"),
(270, "denarius", 0.15, "3世紀の危機。デナリウス、銀メッキの銅板になる"),
(312, "denarius", 0.05, "デナリウス廃止。市民、物々交換へ後退"),
(312, "aureus", 0.6, "コンスタンティヌス、金貨アウレウスを刷新"),
(309, "solidus", 1.3, "ソリドゥス登場「千年、信用を保った硬貨」"),
(700, "dinar", 1.2, "イスラム世界、独自金币ディナールを整備"),
(1055, "solidus", 0.8, "セルジューク台頭。ビザンツ金貨、少し痩せる"),
(1092, "hyperpyron", 1.2, "細りきったソリドゥス、ヒュペルピュロンと交替"),
(1204, "hyperpyron", 0.4, "第四回十字軍、首都を略奪。金貨、悲鳴"),
(1258, "dinar", 0.2, "モンゴル、バグダッドを落とす。金銀、川へ"),
(1258, "dirham", 0.2, "ディルハム、モンゴルの馬蹄の下"),
(1350, "baochao", 0.01, "元、紙幣を刷りまくる。宝鈔、紙としての価値に"),
(1400, "mingnotes", 0.05, "大明宝鈔、強制使用もインフレには勝てず"),
(1425, "mingnotes", 0.2, "明、宝鈔の事実上の廃止を認める"),
(1453, "hyperpyron", 0.05, "首都陥落。千年のビザンツ、帳簿を閉じる"),
(1492, "escudo", 1.4, "コロンブス上陸。世界がスペインの金貨を買いに来る"),
(1520, "thaler", 1.3, "ヨアヒンスタール、大量の銀鉱脈を開く"),
(1545, "escudo", 0.92, "ポトシ銀山発見。銀が溢れ、銀自体の値が下がる"),
(1557, "escudo", 0.8, "スペイン王室、初のデフォルトを宣言"),
(1600, "escudo", 0.9, "エスクード、また少し削られる。王室の贅沢は高い"),
(1637, "guilder", 3.0, "チューリップ狂乱! 球根1個=家1軒"),
(1638, "guilder", 0.35, "チューリップ暴落。球根、ただの根っこ"),
(1650, "escudo", 0.9, "銀の流入は続く。カスティーリャ、また破産"),
(1717, "pound", 1.1, "ニュートン、金とポンドの交換率に釘を打つ"),
(1720, "pound", 0.75, "南海バブル崩壊。ニュートンも株で損をする"),
(1720, "franc", 0.3, "ロー氏のミシシッピ会社、株と紙幣で国民を紙切れに"),
(1776, "continental", 1.5, "独立宣言。大陸会議、刷ることで戦争を買う"),
(1781, "continental", 0.1, "戦況悪化。大陸紙幣、紙くず呼ばわり"),
(1788, "continental", 0.01, "大陸紙幣、憲法に置き換えられ退場"),
(1789, "assignat", 1.5, "仏、教会財産を担保にアッシニュを発行"),
(1793, "assignat", 0.3, "革命政府、ギロチンと印刷機をフル稼働"),
(1795, "assignat", 0.02, "アッシニュ暴落「紙幣の価値は紙以下」"),
(1796, "assignat", 0.01, "アッシニュ廃止。フランス、金で買い直す"),
(1803, "franc", 1.3, "ナポレオン、ジェルミナル・フランを整備"),
(1849, "usd", 1.05, "ゴールドラッシュ。カリフォルニアの砂金が船で到着"),
(1861, "confed", 1.2, "南軍、綿花を信じて紙幣を発行"),
(1864, "usd", 0.85, "緑背紙幣、金兑换を停止。戦費は印刷で"),
(1865, "confed", 0.01, "アポマトックス。南軍ドル、戦費とともに蒸発"),
(1871, "mark", 1.4, "ドイツ統一。賠償金と金準備で金本位マルク"),
(1871, "yen", 1.2, "明治政府、円を発行。四貨からメートル法へ"),
(1873, "krona", 1.2, "スカンディナヴィア通貨同盟。クローナ、銀で団結"),
(1875, "ottoman", 0.3, "オスマン帝国、対外債務の支払いを停止"),
(1879, "greenback", 1.3, "回復法。緑背紙幣、ついに金と引き換え可能に"),
(1896, "usd", 0.9, "ブライアン「金十字架に人類を釘付けにするな」"),
(1897, "yen", 0.8, "戦後恐慌。円、金兑换復帰へ値を削る"),
(1898, "real8", 0.05, "パリ条約。スペイン、8レアルの帝国を手放す"),
(1914, "pound", 0.8, "大戦勃発。ポンド、金本位を一時棚上げ"),
(1914, "mark", 0.6, "ドイツ、金本位停止。印刷機が愛国者になる"),
(1914, "franc", 0.8, "仏、「通貨は戦時下にあり」と印刷を開始"),
(1914, "ruble", 0.7, "帝政ロシア、紙幣増刷で戦争に突入"),
(1914, "lira", 0.8, "イタリア、紙幣を増刷。リレラ痩せる"),
(1914, "krona", 0.7, "大戦、スカンディナヴィアにも"),
(1917, "ruble", 0.1, "革命。ルーブル、ツァーリとともに崩れる"),
(1918, "yudinar", 1.2, "セルブ人・クロアチア人・スロベニア人王国、通貨統一"),
(1918, "ottoman", 0.4, "オスマン帝国降伏。リラ、戦勝国の机で分割される"),
(1919, "crown", 0.3, "ハプスブルク解体。クローネ、後継国家なく浮遊"),
(1922, "ottoman", 0.05, "スルタン制廃止。オスマン・リラ、退場"),
(1922, "ruble", 0.05, "ソヴィエト連邦結成。帝政ルーブル、用済み"),
(1923, "mark", 1e-8, "ハイパーインフレ。朝食に1兆マルク"),
(1923, "lira", 0.5, "戦後混乱のリレラ。ムソリーニ、台頭の足場"),
(1924, "mark", 0.01, "レンテンマルク登場。土地を担保に奇跡の安定"),
(1924, "crown", 0.01, "クローネ崩壊。オーストリア、シリングへ"),
(1927, "pengo", 1.2, "ペンゲ改革。ハンガリー、金本位に復帰"),
(1931, "yen", 0.8, "浜口蔵相、金兑换停止。円、下落"),
(1931, "pound", 0.66, "ポンド、金本位離脱", "BoE1931"),
(1931, "krona", 0.8, "スカンディナヴィア、金本位から相次いで崩壊"),
(1931, "pesomx", 0.7, "メキシコ、金本位を放棄"),
(1933, "usd", 0.75, "ルーズヴェルト、金私有禁止。ドル、金に対して7割へ"),
(1936, "peseta", 0.5, "スペイン内戦。ペセタ、二つに割れる"),
(1936, "lira", 0.8, "エチオピア戦。リレラ、国際的に孤立"),
(1938, "schilling", 0.6, "オーストリア併合。シリング、マルクに吸収"),
(1940, "guilder", 0.5, "ロッテルダム炎上。グルデン、占領下"),
(1940, "bfranc", 0.5, "ベルギー降伏。フラン、独軍の手管"),
(1941, "drachma", 0.2, "占領下のギリシャ。ドラクマ、歴史的暴落"),
(1941, "fabi", 0.5, "戦時中国。法幣、じわり溶ける"),
(1941, "yen", 0.6, "円、ブロック圏の中心で細る"),
(1943, "lira", 0.1, "敗北したイタリア。リレラ、連合国軍票に押される"),
(1945, "pengo", 1e-10, "世界最悪のハイパーインフレ。ペンゲ、1兆兆ペング"),
(1946, "pengo", 0.01, "ペンゲ廃止。フォリント、灰烬から"),
(1946, "rupiah", 1.3, "独立宣言。ルピア、革命の証"),
(1947, "fabi", 0.001, "内戦下の中国。法幣、紙より軽い"),
(1947, "srruble", 0.1, "戦後ソ連、通貨改革。旧紙幣を十割回収"),
(1948, "fabi", 0.001, "金円券へ移行。法幣、完全退役"),
(1948, "goldyuan", 0.01, "金円券も数週でもげた。国民党、台北へ"),
(1948, "dmark", 1.5, "紙幣改革。ドイツマルク、経済奇跡の種"),
(1949, "yen", 0.4, "ドッジライン1ドル360円。円、戦後レートを刻まれる"),
(1949, "cny", 1.5, "中华人民共和国、人民元"),
(1953, "won", 1.2, "戦後再建。韓国ウォン"),
(1961, "srruble", 0.1, "フルシチョフ、通貨改革。ルーブル、また十割回収"),
(1966, "rupee", 0.6, "インド、ルピー切り下げ。IMFとの約束"),
(1971, "usd", 0.88, "ニクソン・ショック。金兑换停止、ドル単独の時代"),
(1971, "yen", 0.85, "ドルと一緒に円も変換停止。「変動相場制へ」"),
(1973, "pound", 0.85, "ポンド、変動相場制へ。帝国の残響"),
(1976, "pound", 0.75, "IMF救済。ポンド、「英国の破産」の語が紙面を飾る"),
(1976, "pesomx", 0.6, "ペソ切り下げ。「このペソは本物です」は空振りに"),
(1982, "pesomx", 0.3, "メキシコ、支払停止。ラテンアメリカ債務危機"),
(1985, "yen", 1.4, "プラザ合意。円、急速に切り上がる"),
(1988, "cny", 0.8, "価格改命。人民元、買い占めの波"),
(1989, "forint", 0.8, "ハンガリー、社会主義からの転換。通貨、試行"),
(1989, "apeso", 0.2, "インフレ年率4900%。アルゼンチン、夏の大混乱"),
(1991, "srruble", 0.5, "パブロフ改革。ソ連ルーブル、最後の改革"),
(1991, "apeso", 0.3, "兌換ペソ導入。1ペソ=1ドルの約束"),
(1992, "pound", 0.75, "暗黒水曜日。ポンドERM離脱", "BoE92"),
(1992, "yudinar", 1e-4, "内戦下のユーゴ。ディナール、史上二位の暴落"),
(1993, "yudinar", 1e-4, "ユーゴ・ハイパーインフレ。4か月で31300兆%"),
(1994, "pesomx", 0.4, "メキシコ・ペソ危機。テキーラ・ショック", "Banxico94"),
(1995, "yen", 1.3, "円高1ドル80円。米国、怒る"),
(1997, "baht", 0.5, "バーツ変動制移行。アジア通貨危機、点火", "BOT97"),
(1997, "won", 0.45, "IMF管理下へ。ウォン、急落"),
(1997, "rupiah", 0.4, "ルピア危機。スハルト体制の終わりと共に"),
(1998, "ruble2", 0.3, "ロシア、デフォルト。GKO、紙屑", "CBR98"),
(2001, "apeso", 0.6, "コラルィート。銀行預金凍結、ペソ交換禁止", "BCRA01"),
(2001, "tlira", 0.7, "トルコ危機。リラ、2日で半値"),
(2002, "apeso", 0.35, "兑换終了。1ドル=3ペソ超"),
(2008, "forint", 0.5, "東欧通貨危機。フォリント、IMFを呼ぶ"),
(2008, "zdw", 1e-4, "ジンバブエ、100兆紙幣発行。100兆でバス1回分", "RBZ08"),
(2008, "usd", 0.9, "リーマン・ブラザース崩壊。安全資産へ、とは行かず"),
(2010, "euro", 0.85, "ギリシャ危機。ユーロ、「解体するのか?」"),
(2010, "drachma", 0.8, "ギリシャ、IMF管理下。ドラクマ再導入の噂"),
(2013, "yen", 0.8, "異次元緩和。円、二年で三割安"),
(2014, "hryvnia", 0.6, "クリミア併合。フリヴニャ、半値道"),
(2014, "ruble2", 0.7, "原油急落と制裁。ルーブル、沈む"),
(2015, "chf", 1.15, "SNB、ユーロ下限を突如撤廃。フラン、天井へ"),
(2015, "cny", 0.9, "人民元、切り下げ。世界、再び中国を疑う"),
(2016, "pound", 0.85, "ブレグジット国民投票。ポンド、一晩で消える"),
(2018, "tlira", 0.7, "トルコ、異端金融学。リラ、蒸発"),
(2020, "usd", 0.93, "コロナ。FRB刷る。金は跳ね、ドルは溶ける"),
(2022, "ruble2", 0.6, "侵攻。ルーブル、一時「プーチン・ペーパー」"),
(2022, "hryvnia", 0.7, "開戦。フリヴニャ、防衛戦"),
(2022, "yen", 0.75, "ウルトラ緩和管理。円、30年ぶりの安値圏"),
(2022, "cny", 0.95, "不動産不況とゼロコロナ。元、上値重い"),
(2026, "euro", 0.95, "電子ユーロ実験開始。紙幣の終焉、再び"),
]

def yname(y):
    return f"紀元前{-y}年" if y < 0 else f"{y}年"

def fmt_g(g):
    g = float(g)
    if g != g:
        return "NaN"
    if g == float("inf"):
        return "∞"
    a = abs(g)
    if a >= 1e12 or (0 < a < 1e-6):
        return f"{g:.2e}g"
    if a >= 1e4:
        return f"{g:,.0f}g"
    return f"{g:,.2f}g"

def born(cid):
    return CURS[cid]["y0"] <= S["year"]

def alive(cid):
    return born(cid) and S["year"] <= CURS[cid]["y1"]

def price(cid):
    c = CURS[cid]
    return max(c["base"] * c["factor"], 1e-18)

def long_val():
    return sum(q * price(c) for c, q in S["hold"].items() if q > 0 and born(c))

def short_val():
    return sum(q * price(c) for c, q in S["short"].items() if q > 0 and born(c))

def equity():
    return S["silver"] + long_val() - S["debt"] - short_val()

def exposure():
    return long_val() + short_val() + S["debt"]

def hint(cid, year):
    for (y, c, m, _h, *nb) in EVENTS:
        if c == cid and y == year:
            if nb and BANKS[nb[0]]["fallen"]:
                continue
            return "▲" if m > 1 else "▼"
    for b in BANK_DEFS:
        if b[1] == cid and b[2] <= year <= b[3] and not BANKS[b[0]]["fallen"]:
            return "◆"
    return " "

def net_line():
    eq = equity()
    ex = exposure()
    lev = (ex / eq) if eq > 0 else float("inf")
    return (f"◆ {yname(S['year'])} | 純資産 {fmt_g(eq)}"
            f"（銀 {fmt_g(S['silver'])} 借入 {fmt_g(S['debt'])}）"
            f"| 建値 {lev:.1f}倍/上限{LEV:.0f}倍")

def pos_line():
    ps = [f"買 {CURS[c]['name']}×{q:,.4g} ({fmt_g(q * price(c))})"
          for c, q in S["hold"].items() if q > 1e-12]
    ps += [f"売 {CURS[c]['name']}×{q:,.4g} ({fmt_g(q * price(c))})"
           for c, q in S["short"].items() if q > 1e-12]
    return "持ち高: " + (" / ".join(ps) if ps else "なし")

def year_end(y):
    """この年 y の大晦日: 利子・攻勢決着・紙幣劣化・死亡処理・銀行ウィンドウ終了"""
    out = []
    S["debt"] *= (1 + INTR)
    for b in BANKS.values():
        if b["attack"]:
            cid = b["cur"]
            if S["short"].get(cid, 0) > 0:
                S["short"][cid] *= (1 + ATT_INTR)
                out.append(f"　{CURS[cid]['name']}の中銀、利上げ。売り建てに年{ATT_INTR:.0%}の利子")
    if y >= 1971:
        for c in CURS.values():
            if c["regime"] == "f":
                c["factor"] *= DRIFT
    for bid in [k for k, b in BANKS.items() if b["attack"]]:
        settle_attack(bid, out)
    for cid in [k for k, v in CURS.items() if v["y1"] == y]:
        v = CURS[cid]
        hl = S["hold"].pop(cid, 0.0)
        sh = S["short"].pop(cid, 0.0)
        if hl > 1e-12 and v["succ"] and born(v["succ"]):
            s = v["succ"]
            got = hl * price(cid) / price(s)
            S["hold"][s] = S["hold"].get(s, 0.0) + got
            out.append(f"☠ {v['name']}、この世を去る。持っていた {hl:,.4g} 枚は"
                       f"継承通貨 {CURS[s]['name']} {got:,.4g} に生まれ変わった")
        elif hl > 1e-12:
            out.append(f"☠ {v['name']}、国家ごと滅んだ。継承なし——"
                       f"持っていた {hl:,.4g} 枚は紙屑と化した（-{fmt_g(hl * price(cid))}）")
        if sh > 1e-12:
            out.append(f"⚖ {v['name']}の売り建て {sh:,.4g}、債務ごと消滅。買い戻さなくて済んだ")
        v["factor"] = 0.0
    for bid, b in BANKS.items():
        if (not b["fallen"]) and (not b["missed"]) and y > b["y1"]:
            b["missed"] = True
            out.append(f"◎ 「{CURS[b['cur']]['name']}」の中央銀行 {bid}、為替防衛に成功。"
                       f"この機会は二度と来ない（取り逃し）")
    return out

def apply_event(ev):
    y, cid, m, head = ev[0], ev[1], ev[2], ev[3]
    nb = ev[4] if len(ev) > 4 else None
    if nb and BANKS[nb]["attack"]:
        return []
    if nb and BANKS[nb]["fallen"]:
        return [f"▶ {yname(y)} {head} —— だがその中銀は既にあなたに倒されていた"]
    CURS[cid]["factor"] = max(CURS[cid]["factor"] * m, 1e-30)
    return [f"▶ {yname(y)} {head}（{CURS[cid]['name']} {'急騰' if m > 1 else '急落'} ×{m:g}）"]

def advance_to(ny):
    """年 ny（ニュースの年、または 2026）まで進める。途中の年も飛ばして処理する"""
    lines = []
    while S["year"] < ny:
        y = S["year"]
        evs = [e for e in EVENTS if e[0] == y]
        for e in evs:
            lines += apply_event(e)
        lines += year_end(y)
        S["year"] = y + 1
        if equity() <= 0:
            return lines
    return lines

def can_do(after_eq=None):
    eq = equity() if after_eq is None else after_eq
    return eq > 0 and exposure() <= LEV * eq + 1e-9

def do_buy(cid, g, quiet=False):
    if not alive(cid):
        return "その通貨はまだこの世に無い（か、既に死んでいる）"
    if g <= 0:
        return "数量を正しく指定してね（例: b usd 10 / b usd all）"
    snap = (S["silver"], S["debt"])
    qty = g * (1 - FEE) / price(cid)
    S["silver"] -= g
    if S["silver"] < 0:
        S["debt"] += -S["silver"]
        S["silver"] = 0.0
    S["hold"][cid] = S["hold"].get(cid, 0.0) + qty
    if not can_do():
        S["hold"][cid] -= qty
        S["silver"], S["debt"] = snap
        return f"却下: レバレッジ上限（純資産の{LEV:.0f}倍）を超える買いは許されない"
    if not quiet:
        bor = "" if S["debt"] <= 0 else f"（うち借入 {fmt_g(g)}）"
        print(f"　{CURS[cid]['name']} を {fmt_g(g)} ぶん購入"
              f"（{qty:,.4g} 枚・手数料 {FEE:.1%}）{bor}")
    return None

def _repay_debt():
    if S["debt"] > 0 and S["silver"] > 0:
        r = min(S["debt"], S["silver"])
        S["debt"] -= r
        S["silver"] -= r

def do_sell(cid, g, quiet=False):
    have = S["hold"].get(cid, 0.0) * price(cid)
    if have <= 0:
        return "その通貨の現物を持っていない"
    g = min(g, have)
    qty = g / price(cid)
    S["hold"][cid] -= qty
    S["silver"] += g * (1 - FEE)
    _repay_debt()
    if not quiet:
        print(f"　{CURS[cid]['name']} を {fmt_g(g)} ぶん売却（受取 {fmt_g(g * (1 - FEE))}）")
    return None

def do_short(cid, n, quiet=False):
    if not alive(cid):
        return "その通貨を売り建てることはできない"
    g = n * price(cid)
    snap = (S["silver"], S["debt"])
    S["short"][cid] = S["short"].get(cid, 0.0) + n
    S["silver"] += g * (1 - FEE)
    _repay_debt()
    if not can_do():
        S["short"][cid] -= n
        S["silver"], S["debt"] = snap
        return f"却下: レバレッジ上限（{LEV:.0f}倍）を超えてしまう"
    if not quiet:
        print(f"　{CURS[cid]['name']} を {n:,.4g} 枚 売り建て"
              f"（受取 {fmt_g(g * (1 - FEE))}・下落が儲け）")
    return None

def do_cover(cid, n, quiet=False):
    have = S["short"].get(cid, 0.0)
    if have <= 1e-12:
        return "売り建てが無い"
    if n == "all" or n >= have:
        n = have
    g = n * price(cid)
    if S["silver"] < g * (1 + FEE):
        need = g * (1 + FEE) - S["silver"]
        S["silver"] += need
        S["debt"] += need
    S["short"][cid] -= n
    S["silver"] -= g * (1 + FEE)
    _repay_debt()
    if not quiet:
        print(f"　{CURS[cid]['name']} 売り建て {n:,.4g} 枚を買い戻し（支払 {fmt_g(g * (1 + FEE))}）")
    return None

def banks_line():
    lines = []
    for bid, b in BANKS.items():
        if b["fallen"]:
            st = "☠倒壊"
        elif b["missed"]:
            st = "…取り逃し"
        elif b["y0"] <= S["year"] <= b["y1"]:
            st = "●攻撃可"
        elif b["y0"] > S["year"]:
            st = f"先 ({b['y0']}〜)"
        else:
            st = "閉幕"
        need = 0.5 * b["reserves"]
        lines.append(f" {bid:10s} {CURS[b['cur']]['name']:14s} "
                     f"{yname(b['y0'])}〜{yname(b['y1'])} 準備金 {fmt_g(b['reserves'])}"
                     f"（売り建て {fmt_g(need)}〜）{st}")
    return "\n".join(lines)

def show_banks():
    print("売り攻勢の標的（条件: ウィンドウ内の年であること、"
          "対象の売り建てが準備金の半分以上）:")
    print(banks_line())
    print(" a <ID> で攻勢開始 / x <ID> で中止。準備金が尽きると通貨を撃墜、"
          "売り建ては安値で自動決済され戦利品が入る")

def do_attack(bid, quiet=False):
    if bid not in BANKS:
        return "そんな銀行は無い（a で一覧）"
    b = BANKS[bid]
    if b["fallen"]:
        return "もう倒した銀行だ。二度殺すのはやめよう"
    if b["missed"]:
        return "そのウィンドウは過ぎた。歴史は待ってくれない"
    if not (b["y0"] <= S["year"] <= b["y1"]):
        if S["year"] > b["y1"]:
            return f"その機会（きかい）は過ぎた（攻撃可能は {yname(b['y0'])}〜{yname(b['y1'])}）"
        return f"まだ早い（攻撃可能は {yname(b['y0'])}〜{yname(b['y1'])}）"
    if b["attack"]:
        return "既に攻勢中だ。耐えてくれ"
    cid = b["cur"]
    sv = S["short"].get(cid, 0.0) * price(cid)
    if sv < 0.5 * b["reserves"]:
        return (f"売り建てが足りない: {CURS[cid]['name']}の売り建てが "
                f"{fmt_g(0.5 * b['reserves'])}以上必要（現在 {fmt_g(sv)}）")
    b["attack"] = True
    if not quiet:
        print(f"⚔ 宣言: {CURS[cid]['name']}の中央銀行 {bid} へ売り攻勢を開始！"
              f"準備金 {fmt_g(b['reserves'])} を枯らすまで殴り続ける")
    return None

def do_stop(bid):
    b = BANKS.get(bid)
    if not b or not b["attack"]:
        return "攻勢中の銀行が無い"
    b["attack"] = False
    return f"{bid} への攻勢を中止した"

def settle_attack(bid, out):
    b = BANKS[bid]
    cid = b["cur"]
    sv = S["short"].get(cid, 0.0) * price(cid)
    if sv <= 0:
        b["attack"] = False
        out.append(f"　{bid}、売り持ちが居なくなって肩透かし。攻勢自然消滅")
        return
    b["reserves"] -= sv * (0.8 + random.random() * 0.8)
    CURS[cid]["factor"] *= 1.08
    if b["reserves"] > 0:
        out.append(f"　{bid}、利上げと介入で反撃（準備金残 {fmt_g(b['reserves'])}。"
                   f"{CURS[cid]['name']}を1.08倍買い支えた）")
        return
    b["attack"] = False
    b["fallen"] = True
    old = price(cid)
    CURS[cid]["factor"] = max(CURS[cid]["factor"] * b["deval"], 1e-30)
    out.append(f"★★☆ {bid} 陥落！！ {CURS[cid]['name']}が ×{b['deval']:g} に暴落"
               f"（{fmt_g(old)}→{fmt_g(price(cid))}）")
    sh = S["short"].pop(cid, 0.0)
    if sh > 1e-12:
        gain = sh * (old - price(cid))
        S["silver"] += gain
        out.append(f"　売り建て {sh:,.4g} 枚を安値で自動決済。+{fmt_g(gain)}")
    bounty = 0.03 * b["reserves0"]
    S["silver"] += bounty
    out.append(f"　戦利品 +{fmt_g(bounty)}（中銀の金庫から）")

def show_prices(hy):
    rows = [f"  {'ID':11s} {'通貨':16s} 現在値(銀g) 体制 終末 見通し"]
    for cid, c in CURS.items():
        if not alive(cid):
            continue
        d = ""
        if c["y1"] <= S["year"] + 10:
            d = "⚰滅亡へ" if not c["succ"] else "⌛継承あり"
        rows.append(f"  {cid:11s} {c['name']:16s} {price(cid):>12.4g}  "
                    f"{'金' if c['regime'] == 'g' else '紙'}   {d}  {hint(cid, S['year'])}")
    print("\n".join(rows))

HELP = """コマンド: b<通貨> <g数|all>=買 / s<通貨> <g数|all>=売 /
 sh<通貨> <枚数>=売り建て / cv<通貨> <枚数|all>=買戻し / a <銀行>=売り攻勢 /
 x <銀行>=攻勢中止 / n[年数]=進む / l=一覧 p=相場 w=資産 bank=標的 h=ここ q=中断"""

def parse_amt(tok):
    if tok is None:
        return 1.0
    if tok == "all":
        return "all"
    try:
        return float(tok)
    except ValueError:
        return None

def do_command(tokens, quiet=False):
    if not tokens:
        return None
    op = tokens[0].lower()
    if op in ("h", "help", "?"):
        print(HELP)
    elif op in ("l", "list"):
        show_prices(True)
    elif op in ("p", "price"):
        show_prices(True)
    elif op in ("w", "net"):
        print(net_line())
        print(pos_line())
    elif op == "bank":
        show_banks()
    elif op == "b":
        if len(tokens) < 3:
            print("b <通貨> <g数|all>")
            return None
        amt = parse_amt(tokens[2])
        cid = tokens[1]
        if cid not in CURS:
            print("その通貨は無い（l で一覧）")
            return None
        if amt is None:
            print("g数は数字か all で")
            return None
        g = S["silver"] if amt == "all" else amt
        err = do_buy(cid, g, quiet)
        if err:
            print("　" + err)
    elif op == "s":
        cid = tokens[1] if len(tokens) > 1 else ""
        if cid not in CURS:
            print("s <通貨> <g数|all>")
            return None
        amt = parse_amt(tokens[2]) if len(tokens) > 2 else "all"
        g = float("inf") if amt == "all" else (amt or 0)
        err = do_sell(cid, g, quiet)
        if err:
            print("　" + err)
    elif op == "sh":
        if len(tokens) < 3:
            print("sh <通貨> <枚数>")
            return None
        cid, n = tokens[1], parse_amt(tokens[2])
        if cid not in CURS or n in (None, "all"):
            print("枚数は数値で（sh usd 100）")
            return None
        err = do_short(cid, n, quiet)
        if err:
            print("　" + err)
    elif op == "cv":
        cid = tokens[1] if len(tokens) > 1 else ""
        if cid not in CURS:
            print("cv <通貨> <枚数|all>")
            return None
        n = parse_amt(tokens[2]) if len(tokens) > 2 else "all"
        if n is None:
            n = "all"
        err = do_cover(cid, n, quiet)
        if err:
            print("　" + err)
    elif op == "a":
        if len(tokens) < 2:
            show_banks()
            return None
        err = do_attack(tokens[1], quiet)
        if err:
            print("　" + err)
    elif op == "x":
        if len(tokens) > 1:
            print("　" + (do_stop(tokens[1]) or ""))

def next_news_year():
    ys = [y for (y, *_r) in EVENTS if y > S["year"]]
    return min(ys + [END_YEAR]) if ys else END_YEAR

def step_to(ny, out):
    ny = min(ny, END_YEAR)
    out += advance_to(ny)
    if S["year"] >= END_YEAR:
        for e in [e for e in EVENTS if e[0] == END_YEAR]:
            out += apply_event(e)

def all_fallen():
    return all(b["fallen"] for b in BANKS.values())

def wrap():
    print("\n" + "=" * 66)
    if equity() <= 0:
        print("▓▓ GAME OVER ▓▓ 資産が消し飛んだ。歴為替の波に呑まれた数は数知れず")
    elif all_fallen():
        print("★★ GAME CLEAR ★★ 8中央銀行、すべて撃破。あなたは歴史そのものになった")
    elif S["year"] >= END_YEAR:
        print("★ GAME CLEAR ★ 2026年まで生き残った。最終資産で歴史の勝ち組みを測る")
    print(net_line())
    print(pos_line())
    f = [b for b, v in BANKS.items() if v["fallen"]]
    print(f"倒した銀行 {len(f)}/{len(BANKS)}: {', '.join(f) if f else '無し'}")
    print(f"経過 {S['year'] - START_YEAR}年 / 全 {END_YEAR - START_YEAR}年")

def interact():
    while S["year"] < END_YEAR and equity() > 0 and not all_fallen():
        if S["year"] == next_news_year():
            print("\n" + net_line())
        try:
            raw = input(f"[{yname(S['year'])}]> ").strip()
        except EOFError:
            print("(入力が尽きたので n で時代を進め続ける)")
            out = []
            while S["year"] < END_YEAR and equity() > 0 and not all_fallen():
                step_to(next_news_year(), out)
                if out:
                    print("\n".join(out))
                    out = []
            break
        if not raw:
            continue
        if raw.lower() == "q":
            print("（そこで観念して幕を下ろした）")
            break
        if raw.lower().startswith("n"):
            ny = next_news_year()
            if len(raw) > 1:
                try:
                    ny = min(S["year"] + int(raw[1:]), END_YEAR)
                except ValueError:
                    print("n 後ろは年数（数字）")
                    continue
            out = []
            step_to(ny, out)
            print("\n".join(out))
            print(net_line())
            print(pos_line())
            continue
        do_command(raw.split())
    wrap()

def bot_turn():
    """適当に動く自動売買Bot: 攻勢狙い＋ランダム売買"""
    if random.random() < 0.55:
        return
    att = [bid for bid, b in BANKS.items()
           if not b["fallen"] and not b["missed"] and b["y0"] <= S["year"] <= b["y1"]]
    for bid in att:
        b = BANKS[bid]
        cid = b["cur"]
        need = 0.55 * b["reserves"] / max(price(cid), 1e-18)
        have = S["short"].get(cid, 0.0)
        if have < need:
            do_short(cid, max(1.0, (need - have) * 1.05), quiet=True)
        if equity() > 0 and S["short"].get(cid, 0.0) * price(cid) >= 0.5 * b["reserves"]:
            do_attack(bid, quiet=True)
    if random.random() < 0.65:
        cs = [c for c in CURS if alive(c)]
        if cs and S["silver"] > 0.2:
            do_buy(random.choice(cs), S["silver"] * random.uniform(0.1, 0.35), quiet=True)
    elif random.random() < 0.4:
        longs = [c for c, q in S["hold"].items() if q > 1e-9]
        if longs:
            do_sell(random.choice(longs), float("inf"), quiet=True)
    if random.random() < 0.1:
        cs = [c for c in CURS if alive(c) and not any(
            b["cur"] == c and not b["fallen"] and not b["attack"] for b in BANKS.values())]
        if cs:
            cid = random.choice(cs)
            do_short(cid, random.uniform(0.5, 3.0), quiet=True)
    for cid in [c for c, q in S["short"].items() if q > 1e-9]:
        if equity() > 0 and random.random() < 0.04:
            do_cover(cid, "all", quiet=True)

S = None

def intro():
    print("=" * 66)
    print("  CHRONO FX 〜エレクトロン・スタンダード〜")
    print("  紀元前700年・リディアのエレクトロン貨から2026年まで、1年1コマ")
    print("  ニュースを読んで Currency を売買し、資産を守り抜け。")
    print("  ・手数料 0.3% / レバレッジ上限 純資産の10倍 / 銀借入に年2%")
    print("  ・国家と運命を共にした通貨の現物は消滅、売り建ては債務ごと消滅")
    print("  ・貴金属本位・固定相場の時代、準備金を持つ中央銀行を売り攻勢で倒せる")
    print(f"  ・目標: 2026年まで破産せず生存、または {len(BANKS)} 中銀すべて撃破")
    print("  見通し記号 ▲=上げニュース ▼=下げニュース ◆=中銀攻撃可 ⌛=継承あり ⚰=滅亡へ")
    print("=" * 66)

def main():
    global S
    args = sys.argv[1:]
    seed, nbot = None, 0
    i = 0
    while i < len(args):
        if args[i] == "--seed" and i + 1 < len(args):
            seed = int(args[i + 1]); i += 2
        elif args[i] == "--bot" and i + 1 < len(args):
            nbot = int(args[i + 1]); i += 2
        else:
            i += 1
    random.seed(seed)
    S = {"year": START_YEAR, "silver": START_SILVER, "debt": 0.0,
         "hold": {}, "short": {}}
    for c in CURS.values():
        c["factor"] = 1.0
    for b in BANKS.values():
        b.update(fallen=False, missed=False, attack=False,
                 reserves=b["reserves0"])
    intro()
    print(net_line())
    print("当初からある通貨: ", ", ".join(CURS[c]["name"] for c in CURS if alive(c)))
    print("(h でヘルプ / p で相場 / n で次のニュースまで)")
    if nbot > 0:
        turns = 0
        last_show = START_YEAR
        while S["year"] < END_YEAR and equity() > 0 and not all_fallen():
            step_to(next_news_year(), [])
            if equity() <= 0 or all_fallen() or S["year"] >= END_YEAR:
                break
            bot_turn()
            turns += 1
            if turns % 50 == 0 and S["year"] - last_show >= 25:
                last_show = S["year"]
                print(f"　[bot {turns}手] {yname(S['year'])} "
                      f"純資産 {fmt_g(equity())} 建値 "
                      f"{exposure() / max(equity(), 1e-9):.1f}倍")
        print()
        wrap()
        print(f"(自動売買Bot: {turns}手でこの時代を泳ぎ切った)")
    else:
        interact()

if __name__ == "__main__":
    main()
