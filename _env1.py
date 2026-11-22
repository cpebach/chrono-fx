import os, urllib.request, zipfile

BASE = "D:\\whittle-next-27b"
ZIPDIR = os.path.join(BASE, "dl")
LLAMA = os.path.join(BASE, "llama")
os.makedirs(ZIPDIR, exist_ok=True)
os.makedirs(LLAMA, exist_ok=True)
os.makedirs(os.path.join(BASE, "models"), exist_ok=True)

URLS = [
    "https://github.com/ggml-org/llama.cpp/releases/download/b12602/llama-b12602-bin-win-cuda-12.4-x64.zip",
    "https://github.com/ggml-org/llama.cpp/releases/download/b12602/cudart-llama-bin-win-cuda-12.4-x64.zip",
]

def fetch(url, dst):
    pos = os.path.getsize(dst) if os.path.exists(dst) else 0
    hdr = {"User-Agent": "setup"}
    if pos:
        hdr["Range"] = f"bytes={pos}-"
    req = urllib.request.Request(url, headers=hdr)
    with urllib.request.urlopen(req, timeout=60) as r:
        mode = "ab" if pos and r.status == 206 else "wb"
        pos = 0 if mode == "wb" else pos
        total = pos + int(r.headers.get("Content-Length", 0))
        with open(dst, mode) as f:
            while True:
                b = r.read(1024 * 512)
                if not b:
                    break
                f.write(b)
                pos += len(b)
                if pos // 2**22 != (pos - len(b)) // 2**22:
                    print(f"\r  {pos/2**20:.0f}/{total/2**20:.0f} MB", end="", flush=True)
    print()

for u in URLS:
    dst = os.path.join(ZIPDIR, u.rsplit("/", 1)[-1])
    print("download", os.path.basename(dst))
    fetch(u, dst)
    print("extract ->", LLAMA)
    with zipfile.ZipFile(dst) as z:
        z.extractall(LLAMA)
for root, _, fs in os.walk(LLAMA):
    for f in fs:
        if f.endswith(".exe"):
            print("EXE:", os.path.relpath(os.path.join(root, f), LLAMA))
print("ENV1 OK")
