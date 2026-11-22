import zipfile
z = zipfile.ZipFile(r"D:/dev/chrono_fx/dist/chrono-fx.apk")
ui = z.read("assets/ui.js").decode("utf-8")
ix = z.read("assets/index.html").decode("utf-8")
cs = z.read("assets/style.css").decode("utf-8")
for need, src in (("liveVal", ui), ("requestAnimationFrame(loop)", ui),
                  ("clockrow", ix), ("LIVE CHART", ix), ("#tickbar", cs)):
    print(need, "in APK:", need in src)
print("ui.js bytes in apk:", len(ui.encode("utf-8")))
