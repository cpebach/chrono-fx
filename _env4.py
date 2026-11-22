import json, os, subprocess, sys, time, urllib.request

B = r"D:\whittle-next-27b"
EXE = os.path.join(B, "llama", "llama-server.exe")
MODEL = os.path.join(B, "models", "Whittle-Next-27B-A3B-v4.4-Q5_K_M.gguf")
assert os.path.exists(EXE) and os.path.exists(MODEL), "missing exe or model"

srv = subprocess.Popen(
    [EXE, "-m", MODEL, "-ngl", "99", "-c", "16384", "--jinja", "-fa", "on",
     "-ot", "per_layer_token_embd=CPU", "--host", "127.0.0.1", "--port", "8181"],
    cwd=os.path.join(B, "llama"),
    stdout=open(os.path.join(B, "server_test.log"), "w", encoding="utf-8"),
    stderr=subprocess.STDOUT)

def get(path):
    with urllib.request.urlopen("http://127.0.0.1:8181" + path, timeout=10) as r:
        return json.load(r)

ok = False
for i in range(240):
    time.sleep(2)
    if srv.poll() is not None:
        print("SERVER DIED rc=", srv.returncode)
        print(open(os.path.join(B, "server_test.log"), encoding="utf-8").read()[-2000:])
        sys.exit(1)
    try:
        h = get("/health")
        p = get("/props")
        if h.get("status") == "ok" and "Whittle" in str(p.get("model_path", "")):
            ok = True
            break
    except Exception:
        pass
print("health ok:", ok, f"(waited ~{i*2}s)")
if not ok:
    sys.exit(1)

body = {
    "messages": [{"role": "user",
                  "content": "17の3乗を整数で答えなさい。簡潔に。"}],
    "temperature": 0.7, "top_p": 0.8, "top_k": 20, "repeat_penalty": 1.05,
    "max_tokens": 256,
    "chat_template_kwargs": {"enable_thinking": False},
}
req = urllib.request.Request(
    "http://127.0.0.1:8181/v1/chat/completions",
    data=json.dumps(body).encode(), method="POST",
    headers={"Content-Type": "application/json"})
t0 = time.time()
with urllib.request.urlopen(req, timeout=600) as r:
    res = json.load(r)
el = time.time() - t0
u = res.get("usage", {})
txt = res["choices"][0]["message"]["content"]
print("answer:", txt[:400])
print(f"tokens: {u.get('completion_tokens')} in {el:.1f}s "
      f"(= {u.get('completion_tokens', 0)/max(el, 0.1):.1f} tok/s)")
srv.terminate()
time.sleep(2)
print("SERVER TEST PASS")
