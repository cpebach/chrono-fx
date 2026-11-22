import json, os, subprocess, threading, time, urllib.request

B = r"D:\whittle-next-27b"
EXE = os.path.join(B, "llama", "llama-server.exe")
MODEL = os.path.join(B, "models", "Whittle-Next-27B-A3B-v4.4-Q5_K_M.gguf")
P = 8181

srv = subprocess.Popen(
    [EXE, "-m", MODEL, "-ngl", "99", "-c", "16384", "--jinja", "-fa", "on",
     "-lv", "5", "--host", "127.0.0.1", "--port", str(P)],
    cwd=os.path.join(B, "llama"),
    stdout=open(os.path.join(B, "bench_verbose.log"), "w", encoding="utf-8"),
    stderr=subprocess.STDOUT)

util = []
stop = False
def sampler():
    while not stop:
        r = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used",
                            "--format=csv,noheader"], capture_output=True, text=True)
        util.append(r.stdout.strip())
        time.sleep(1)
th = threading.Thread(target=sampler, daemon=True)
th.start()

try:
    for i in range(300):
        time.sleep(2)
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{P}/health", timeout=5) as r:
                if json.load(r).get("status") == "ok":
                    break
        except Exception:
            pass
    body = {"messages": [{"role": "user", "content":
            "1から30まで1つずつ、それぞれ素数か合成か分類して1行ずつ列挙して。"}],
            "temperature": 0.7, "top_p": 0.8, "top_k": 20,
            "repeat_penalty": 1.05, "max_tokens": 200,
            "chat_template_kwargs": {"enable_thinking": False}}
    req = urllib.request.Request(f"http://127.0.0.1:{P}/v1/chat/completions",
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as r:
        res = json.load(r)
    el = time.time() - t0
    u = res["usage"]
    n = u.get("completion_tokens", 1)
    print(f"measured: {n} tok / {el:.1f}s = {n/el:.1f} tok/s")
    print("GPU samples during run:", util[-30:])
finally:
    stop = True
    srv.terminate()
    srv.wait(timeout=60)
