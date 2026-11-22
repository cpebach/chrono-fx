import os, shutil
SRC = r"C:\Users\omicron\Desktop\chrono_fx"
DST = r"D:\whittle-next-27b\scripts"
os.makedirs(DST, exist_ok=True)
moved = []
for f in os.listdir(SRC):
    if f.endswith(".py") and not f.startswith("_build") and f != "_delc.py":
        a, b = os.path.join(SRC, f), os.path.join(DST, f)
        if not os.path.exists(b):
            shutil.copy2(a, b)
            moved.append(f)
print("saved ->", DST, ":", sorted(moved))
