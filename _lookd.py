import os

D = "D:\\"
for name in sorted(os.listdir(D)):
    p = os.path.join(D, name)
    if os.path.isdir(p):
        try:
            kids = len(os.listdir(p))
        except OSError:
            kids = -1
        print(f"[D] {name:35s} ({kids} items)")
print("---- env hints ----")
for v in ("ProgramFiles", "LOCALAPPDATA", "APPDATA", "NPM_CONFIG_PREFIX",
          "PIP_CACHE_DIR", "TEMP", "HOMEDRIVE", "HOMEPATH", "CARGO_HOME",
          "GOROOT", "ANDROID_HOME", "JAVA_HOME"):
    print(f"{v:18s} = {os.environ.get(v, '-')}")
