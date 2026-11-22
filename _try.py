import json, os, subprocess, time, urllib.request

B = r"D:\whittle-next-27b"
EXE = os.path.join(B, "llama", "llama-server.exe")
MODEL = os.path.join(B, "models", "Whittle-Next-27B-A3B-v4.4-Q5_K_M.gguf")
P = 8181

srv = subprocess.Popen(
    [EXE, "-m", MODEL, "-ngl", "99", "-c", "16384", "--jinja", "-fa", "on",
     "--host", "127.0.0.1", "--port", str(P)],
    cwd=os.path.join(B, "llama"),
    stdout=open(os.path.join(B, "try_server.log"), "w", encoding="utf-8"),
    stderr=subprocess.STDOUT)

def ask(label, prompt, mx, think):
    body = {"messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7, "top_p": 0.8, "top_k": 20,
            "repeat_penalty": 1.05, "max_tokens": mx,
            "chat_template_kwargs": {"enable_thinking": think}}
    req = urllib.request.Request(f"http://127.0.0.1:{P}/v1/chat/completions",
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=1200) as r:
        res = json.load(r)
    el = time.time() - t0
    m = res["choices"][0]["message"]
    u = res["usage"]
    print(f"\n===== {label} ({u.get('completion_tokens')}tok {el:.1f}s "
          f"= {u.get('completion_tokens',0)/max(el,.1):.1f} tok/s) =====")
    txt = m.get("content") or ""
    rs = m.get("reasoning_content")
    if rs:
        print("[thinking]", rs[:600].replace("\n", " "))
    print("[answer]", txt[:800])

try:
    for i in range(300):
        time.sleep(2)
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{P}/health", timeout=5) as r:
                if json.load(r).get("status") == "ok":
                    break
        except Exception:
            pass
    ask("算数(think on)",
        "店に17箱りんごがあり、1箱12個入っています。83個売れました。残りは何個? 簡潔に。",
        1024, True)
    ask("コードレビュー(think on)",
        "次の中関数のバグを日本語で簡潔に指摘して:\ndef avg(xs):\n    return sum(xs)/len(xs)",
        1500, True)
    ask("知識(think off)",
        "TypeScriptのinterfaceとtypeの違いを3行で。", 256, False)
finally:
    srv.terminate()
    srv.wait(timeout=60)
print("\nTRY DONE")
