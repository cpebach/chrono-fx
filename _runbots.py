import os, re, subprocess, sys

PY = sys.executable
GAME = r"D:/dev/chrono_fx/chronofx.py"
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
pats = [r"GAME OVER", r"GAME CLEAR", r"経過 (\d+)年", r"純資産 (\S+)",
        r"倒した銀行 (\d)/8", r"Traceback"]
for seed in (3, 7, 11, 42, 2026):
    r = subprocess.run([PY, GAME, "--bot", "9999", "--seed", str(seed)],
                       capture_output=True, text=True, timeout=180,
                       encoding="utf-8", errors="replace", env=ENV)
    out = (r.stdout or "") + (r.stderr or "")
    hits = [p for p in pats if re.search(p, out)]
    tail = [l for l in out.splitlines()
            if re.search(r"GAME|経過|倒した銀行|最終|純資産", l)]
    print(f"seed {seed}: rc={r.returncode} 一致={hits}")
    for l in tail[-4:]:
        print("   ", l.strip())
    if r.returncode != 0:
        print(out[-800:])
