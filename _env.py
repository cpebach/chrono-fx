import os, shutil, socket, urllib.request
import urllib.error

def w(name):
    p = shutil.which(name)
    print(f"{name}: {p or '-'}")

for t in ("git", "gh", "java", "javac", "keytool", "sdkmanager", "gradle", "node", "npm"):
    w(t)
print("ANDROID_HOME:", os.environ.get("ANDROID_HOME", "-"))
print("ANDROID_SDK_ROOT:", os.environ.get("ANDROID_SDK_ROOT", "-"))
for d in (r"C:\Android", r"C:\android-sdk", os.path.expanduser("~/AppData/Local/Android/Sdk")):
    print(d, "exists" if os.path.isdir(d) else "-")
try:
    import shutil as sh
    du = sh.disk_usage("C:/")
    print(f"disk free: {du.free/2**30:.1f} GB / {du.total/2**30:.1f} GB")
except Exception as e:
    print("disk:", e)
for url in ("https://dl.google.com/android/repository/repository2-3.xml",
            "https://github.com"):
    try:
        req = urllib.request.Request(url, method="HEAD")
        r = urllib.request.urlopen(req, timeout=8)
        print("net", url.split("/")[2], r.status)
    except Exception as e:
        print("net", url.split("/")[2], "FAIL", type(e).__name__)
