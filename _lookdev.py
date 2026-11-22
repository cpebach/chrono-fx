import os

B = "D:\\dev"
for name in sorted(os.listdir(B)):
    p = os.path.join(B, name)
    if os.path.isdir(p):
        try:
            kids = sorted(os.listdir(p))[:6]
        except OSError:
            kids = []
        print(f"{name:30s} -> {kids}")
    else:
        print(f"{name:30s} (file {os.path.getsize(p)/2**20:.1f} MB)")
