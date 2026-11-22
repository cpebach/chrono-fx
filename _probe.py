import json, shutil, subprocess, sys, urllib.request

def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()

rc, out = sh(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
              "--format=csv"])
print("GPU rc=", rc)
print(out if rc == 0 else "(no nvidia-smi)")
t, u, f = shutil.disk_usage("D:\\")
print(f"D free = {f/1024**3:.0f} GB")
print("python", sys.version.split()[0])
rc, out = sh([sys.executable, "-m", "pip", "--version"])
print("pip", out if rc == 0 else "-")

url = "https://huggingface.co/api/models/whittleOrg/Whittle-Next-27B-A3B"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "chrono-setup"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    print("model id:", d.get("id"), "| gated:", d.get("gated"),
          "| downloads:", d.get("downloads"))
    print("tags:", d.get("tags", [])[:15])
    st = d.get("safetensors")
    print("safetensors params:", st.get("total") if st else None)
    files = [s.get("rfilename") for s in d.get("siblings", [])]
    print("files(%d):" % len(files))
    for x in files:
        print("  ", x)
except Exception as e:
    print("HF API error:", e)
