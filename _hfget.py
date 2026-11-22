import os, subprocess, sys, urllib.request

D = r"D:\whittle-next-27b\repo_meta"
os.makedirs(D, exist_ok=True)
BASE = "https://huggingface.co/whittleOrg/Whittle-Next-27B-A3B/raw/main/"
for name in ("README.md", "config.json", "generation_config.json"):
    try:
        req = urllib.request.Request(BASE + name, headers={"User-Agent": "setup"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        p = os.path.join(D, name)
        open(p, "wb").write(data)
        print("saved", name, len(data), "bytes")
    except Exception as e:
        print(name, "ERROR", e)

r = subprocess.run(["py", "-0p"], capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
print("py launchers:", (r.stdout or r.stderr).strip()[:500])
import shutil
for exe in ("python3.12", "python3.11", "conda", "uv", "git"):
    print(exe, "->", shutil.which(exe) or "-")
