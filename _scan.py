import subprocess, re, os

ROOT = r"D:\dev\chrono_fx"
files = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                       cwd=ROOT).stdout.split()
print(len(files), "tracked files")
pat = re.compile(r"(token|password|pass:|secret|webhook|api[_-]?key|BOT[_ ]?TOKEN)", re.I)
bad = []
for f in files:
    try:
        t = open(os.path.join(ROOT, f), encoding="utf-8", errors="replace").read()
    except OSError:
        continue
    for i, line in enumerate(t.splitlines(), 1):
        if pat.search(line):
            bad.append((f, i, line.strip()[:100]))
for b in bad:
    print("HIT", *b)
print("done. hits:", len(bad))
