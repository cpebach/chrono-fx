import io
p = r"C:/Users/omicron/Desktop/chrono_fx/_stitch.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('body = head + "るとイベントは見送られる（攻勢で既に実現済み）\n"',
              'body = head  # _p1 が「ると…」で始まるので続きを継げる')
io.open(p, "w", encoding="utf-8").write(s)
print("fixed")
