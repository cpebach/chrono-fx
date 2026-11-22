import os, subprocess, sys, zipfile, urllib.request, shutil, time

TOOLS = r"C:/Users/omicron/android-build"
SDK = r"C:/Users/omicron/android-tools/Sdk"  # consolidated; old android-build/android-sdk removed
os.makedirs(TOOLS, exist_ok=True)

def fetch(url, dst):
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        print("skip (cached)", os.path.basename(dst))
        return
    print("fetching", url)
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dst + ".part", "wb") as f:
        got = 0
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
            got += len(b)
            if got % (20 << 20) < (1 << 20):
                print(f"  {got/2**20:.0f}MB {time.time()-t0:.0f}s", flush=True)
    os.replace(dst + ".part", dst)
    print("done", os.path.basename(dst), os.path.getsize(dst), "bytes")

# 1) JDK 17
JDK_DIR = os.path.join(TOOLS, "jdk")
JAVA = os.path.join(JDK_DIR, "bin", "java.exe")
if not os.path.exists(JAVA):
    jz = os.path.join(TOOLS, "jdk.zip")
    fetch("https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse", jz)
    with zipfile.ZipFile(jz) as z:
        names = z.namelist()
        root = names[0].split("/")[0]
        for m in z.infolist():
            if m.is_dir():
                continue
            rel = os.path.relpath(m.filename.replace("\\", "/"), root)
            out = os.path.join(JDK_DIR, *rel.split("/"))
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with z.open(m) as src, open(out, "wb") as dstf:
                shutil.copyfileobj(src, dstf)
    print("jdk extracted")
else:
    print("jdk ok")
print("java -version:")
print(subprocess.run([JAVA, "-version"], capture_output=True, text=True).stderr[:200])
print("SETUP_STAGE_JDK_DONE", flush=True)

# 2) cmdline-tools
CT = os.path.join(SDK, "cmdline-tools", "latest")
SDKMGR = os.path.join(CT, "bin", "sdkmanager.bat")
if not os.path.exists(SDKMGR):
    cz = os.path.join(TOOLS, "cmdline-tools.zip")
    fetch("https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip", cz)
    tmp = os.path.join(TOOLS, "ct-extract")
    shutil.rmtree(tmp, ignore_errors=True)
    with zipfile.ZipFile(cz) as z:
        z.extractall(tmp)
    os.makedirs(os.path.dirname(CT), exist_ok=True)
    shutil.move(os.path.join(tmp, "cmdline-tools"), CT)
    print("cmdline-tools extracted")
else:
    print("cmdline-tools ok")
print("SETUP_STAGE_SDKMGR_DONE", flush=True)

# 3) licenses + packages
env = dict(os.environ, JAVA_HOME=JDK_DIR)
r = subprocess.run([SDKMGR, "--licenses"], input="y\n" * 80, capture_output=True,
                   text=True, env=env, timeout=300)
print("licenses rc=", r.returncode)
for pkg in ("platforms;android-34", "build-tools;34.0.0"):
    r = subprocess.run([SDKMGR, pkg], input="y\n" * 10, capture_output=True,
                       text=True, env=env, timeout=1800)
    print(pkg, "rc=", r.returncode, (r.stderr or "")[-300:])
print("SETUP_ALL_DONE", flush=True)
