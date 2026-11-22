import os, sys, time, urllib.request

F = "Whittle-Next-27B-A3B-v4.4-Q5_K_M.gguf"
URL = "https://huggingface.co/logic65/Whittle-Next-27B-A3B-GGUF/resolve/main/" + F
DST = r"D:\whittle-next-27b\models" + "\\" + F
os.makedirs(os.path.dirname(DST), exist_ok=True)
LOG = r"D:\whittle-next-27b\dl_gguf.log"

def log(msg):
    with open(LOG, "a", encoding="utf-8") as lf:
        lf.write(time.strftime("%H:%M:%S ") + msg + "\n")

try:
    for attempt in range(8):
        pos = os.path.getsize(DST) if os.path.exists(DST) else 0
        hdr = {"User-Agent": "Mozilla/5.0 setup"}
        if pos:
            hdr["Range"] = f"bytes={pos}-"
        req = urllib.request.Request(URL, headers=hdr)
        with urllib.request.urlopen(req, timeout=90) as r:
            if pos and r.status != 206:
                pos = 0
            mode = "ab" if pos else "wb"
            total = int(r.headers.get("Content-Length", 0)) + pos
            log(f"attempt {attempt} resume at {pos/2**30:.2f}/{total/2**30:.2f} GiB")
            t0 = time.time()
            with open(DST, mode) as f:
                while True:
                    b = r.read(1024 * 1024)
                    if not b:
                        break
                    f.write(b)
                    pos += len(b)
                    if time.time() - t0 > 30:
                        sp = (pos - (pos - 0)) / 1  # noop
                        log(f"  {pos/2**30:.2f}/{total/2**30:.2f} GiB")
                        t0 = time.time()
        size = os.path.getsize(DST)
        log(f"stream ended at {size/2**30:.2f} GiB (expected {total/2**30:.2f})")
        if size == total:
            log("DOWNLOAD COMPLETE " + F)
            print("DOWNLOAD COMPLETE")
            sys.exit(0)
    log("GAVE UP after retries")
    sys.exit(1)
except Exception as e:
    log("FATAL " + repr(e))
    sys.exit(1)
