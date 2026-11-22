import json, urllib.request

req = urllib.request.Request(
    "https://api.github.com/repos/ggml-org/llama.cpp/releases",
    headers={"User-Agent": "setup"})
with urllib.request.urlopen(req, timeout=60) as r:
    rels = json.load(r)
rel = next(x for x in rels if x["tag_name"].startswith("b") and not x["draft"])
print("tag:", rel["tag_name"], "| published:", rel["published_at"])
for a in rel["assets"]:
    if "win" in a["name"] and "cuda" in a["name"].lower():
        print(f'  {a["name"]:60s} {a["size"]/1024**2:6.0f} MB')
        print("   ", a["browser_download_url"])
