import os, shutil, stat, sys

SRC = r"C:\Users\omicron\Desktop\chrono_fx"
DST = r"D:\dev\chrono_fx"
for need in (r".git\HEAD", r"web\game.js", r"web\ui.js", r"dist\chrono-fx.apk",
             r"D:\dev\android-build\chronofx.keystore"):
    p = need if ":" in need[1:3] else os.path.join(DST, need)
    assert os.path.exists(p), "missing " + p
assert os.path.isdir(SRC)
# .git objects are read-only on Windows; strip and retry on failure
def onerr(fn, path, e):
    os.chmod(path, stat.S_IWRITE)
    fn(path)
shutil.rmtree(SRC, onexc=onerr)
print("deleted", SRC, "exists now:", os.path.exists(SRC))
