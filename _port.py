import subprocess

for cmd in (["netstat", "-ano", "-p", "TCP"],):
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    for ln in (r.stdout or "").splitlines():
        if ":8080" in ln and "LISTEN" in ln.upper():
            print(ln.strip())
