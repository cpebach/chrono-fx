import shutil

for d in ("C:\\", "D:\\"):
    try:
        t, u, f = shutil.disk_usage(d)
        g = 1024 ** 3
        print(f"{d} total={t/g:.0f}GB used={u/g:.0f}GB free={f/g:.1f}GB ({f/t*100:.0f}% free)")
    except OSError as e:
        print(d, "ERROR", e)
