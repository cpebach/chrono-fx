import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "setup"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

t = get("https://huggingface.co/api/models/logic65/Whittle-Next-27B-A3B-GGUF/tree/main?recursive=true")
print("GGUF repo files:")
for f in t:
    if f["type"] == "file":
        sz = f.get("size", 0) or f.get("lfs", {}).get("size", 0)
        print(f"  {f['path']:60s} {sz/1024**3:7.2f} GB")

rel = get("https://api.github.com/repos/ggml-org/llama.cpp/releases/latest")
print("\nllama.cpp latest:", rel["tag_name"])
for a in rel["assets"]:
    if "win" in a["name"] and "cuda" in a["name"].lower():
        print("  ", a["name"], f'{a["size"]/1024**2:.0f} MB')
