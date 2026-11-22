import json, os, subprocess, time, urllib.request

B = r"D:\whittle-next-27b"
EXE = os.path.join(B, "llama", "llama-server.exe")
MODEL = os.path.join(B, "models", "Whittle-Next-27B-A3B-v4.4-Q5_K_M.gguf")
P = 8181

def post(msgs, mx, thinking=False):
    body = {"messages": msgs, "temperature": 0.7, "top_p": 0.8, "top_k": 20,
            "repeat_penalty": 1.05, "max_tokens": mx,
            "chat_template_kwargs": {"enable_thinking": thinking}}
    req = urllib.request.Request(f"http://127.0.0.1:{P}/v1/chat/completions",
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as r:
        res = json.load(r)
    return res, time.time() - t0

def bench(name, extra):
    args = [EXE, "-m", MODEL, "-ngl", "99", "-c", "16384", "--jinja",
            "-fa", "on", "--host", "127.0.0.1", "--port", str(P)] + extra
    logf = open(os.path.join(B, f"bench_{name}.log"), "w", encoding="utf-8")
    srv = subprocess.Popen(args, cwd=os.path.join(B, "llama"),
                           stdout=logf, stderr=subprocess.STDOUT)
    try:
        for i in range(300):
            time.sleep(2)
            if srv.poll() is not None:
                print(name, "SERVER DIED rc=", srv.returncode)
                return None
            try:
                with urllib.request.urlopen(
                        f"http://127.0.0.1:{P}/health", timeout=5) as r:
                    if json.load(r).get("status") == "ok":
                        break
            except Exception:
                pass
        else:
            print(name, "TIMEOUT loading")
            return None
        q = [{"role": "user", "content": "1+1=?"}]
        post(q, 8)  # warmup
        res, el = post([{"role": "user", "content":
                         "JSONで {\"a\": [1,2,3]} に3を掛けた結果を関数 f(x)=3x の表形式で5行。"}],
                       128)
        u = res["usage"]
        n = u.get("completion_tokens", 1)
        print(f"{name}: {n} tok / {el:.1f}s = {n/el:.1f} tok/s")
        return n / el
    finally:
        srv.terminate()
        srv.wait(timeout=60)
        logf.close()

bench("A_cpu_nommap", ["-ot", "per_layer_token_embd=CPU", "--mmap", "false"])
bench("B_all_gpu", [])
