import os, shutil, subprocess, sys, zipfile

ROOT = r"C:/Users/omicron/Desktop/chrono_fx"
TOOLS = r"C:/Users/omicron/android-build"  # C側はjdkとkeystore残存(フォールバック用)
JDK = r"D:/dev/android-build/jdk"
SDK = r"D:/dev/android-tools/Sdk"  # 2026-11-22 Dドライブ移行済み
BT = os.path.join(SDK, "build-tools", "34.0.0")
AJAR = os.path.join(SDK, "platforms", "android-34", "android.jar")
BUILD = os.path.join(ROOT, "android", "build")
DIST = os.path.join(ROOT, "dist")
ENV = dict(os.environ, JAVA_HOME=JDK,
           PATH=os.pathsep.join([os.path.join(JDK, "bin"), BT, os.environ["PATH"]]))

def run(args, **kw):
    print("$", " ".join(os.path.basename(str(a)) for a in args))
    r = subprocess.run(args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=ENV, **kw)
    if r.returncode != 0:
        print(r.stdout[-1500:]); print(r.stderr[-1500:])
        sys.exit("FAILED: " + str(args[0]))
    return r

os.makedirs(BUILD, exist_ok=True)
os.makedirs(DIST, exist_ok=True)
# 1) assets に Web 版を同梱
assets = os.path.join(BUILD, "assets")
shutil.rmtree(assets, ignore_errors=True)
os.makedirs(assets)
for f in ("index.html", "data.js", "game.js", "ui.js", "style.css"):
    shutil.copyfile(os.path.join(ROOT, "web", f), os.path.join(assets, f))
# 2) aapt2 link
base = os.path.join(BUILD, "base.apk")
run([os.path.join(BT, "aapt2.exe"), "link", "-o", base, "-I", AJAR,
     "--manifest", os.path.join(ROOT, "android", "AndroidManifest.xml"), "-A", assets])
# 3) javac
obj = os.path.join(BUILD, "obj")
shutil.rmtree(obj, ignore_errors=True)
run([os.path.join(JDK, "bin", "javac.exe"), "-classpath", AJAR,
     "-encoding", "UTF-8", "-d", obj,
     os.path.join(ROOT, "android", "src", "dev", "chronofx", "app", "MainActivity.java")])
# 4) d8 -> classes.dex
dexdir = os.path.join(BUILD, "dex")
shutil.rmtree(dexdir, ignore_errors=True)
os.makedirs(dexdir)
run([os.path.join(BT, "d8.bat"), "--lib", AJAR, "--release", "--output", dexdir,
     os.path.join(obj, "dev", "chronofx", "app", "MainActivity.class")])
# 5) dex を APK に同梱
unsigned = os.path.join(BUILD, "unsigned.apk")
with zipfile.ZipFile(base) as zin, zipfile.ZipFile(unsigned, "w", zipfile.ZIP_DEFLATED) as zout:
    for it in zin.infolist():
        zout.writestr(it, zin.read(it.filename))
    zout.writestr("classes.dex", open(os.path.join(dexdir, "classes.dex"), "rb").read())
# 6) zipalign
aligned = os.path.join(BUILD, "aligned.apk")
run([os.path.join(BT, "zipalign.exe"), "-f", "4", unsigned, aligned])
# 7) 署名キー（無ければ生成）と apksigner 署名
ks = r"D:/dev/android-build/chronofx.keystore"
KSP = "pass:chronofx2026"
if not os.path.exists(ks):
    run([os.path.join(JDK, "bin", "keytool.exe"), "-genkeypair", "-v",
         "-keystore", ks, "-alias", "chronofx", "-keyalg", "RSA", "-keysize", "2048",
         "-validity", "10000", "-storepass", "chronofx2026", "-keypass", "chronofx2026",
         "-dname", "CN=ChronoFX, OU=dev, O=chrono-fx, L=Tokyo, C=JP"])
apk = os.path.join(DIST, "chrono-fx.apk")
run([os.path.join(BT, "apksigner.bat"), "sign", "--ks", ks, "--ks-pass", KSP,
     "--key-pass", KSP, "--ks-key-alias", "chronofx", "--out", apk, aligned])
r = run([os.path.join(BT, "apksigner.bat"), "verify", "--print-certs", apk])
print((r.stdout or "")[:600])
print("APK OK:", apk, os.path.getsize(apk), "bytes")
media = r"D:/dev/discord-claude-bridge/media/chronofx-gui.apk"
shutil.copyfile(apk, media)
print("copied ->", media)

