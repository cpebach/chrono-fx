import os

B = r"D:\whittle-next-27b"
bat = r"""@echo off
cd /d %~dp0llama
llama-server.exe ^
  -m ..\models\Whittle-Next-27B-A3B-v4.4-Q5_K_M.gguf ^
  -ngl 99 -c 16384 --jinja -fa on ^
  --host 127.0.0.1 --port 8181
"""
open(os.path.join(B, "start_server.bat"), "w", encoding="cp932").write(bat)
readme = """# Whittle-Next-27B-A3B 環境（Dドライブ）

- llama.cpp b12602 CUDA 12.4 ビルド -> llama\\
- モデル v4.4 Q5_K_M (18.3GB) -> models\\Whittle-Next-27B-A3B-v4.4-Q5_K_M.gguf
- 起動: start_server.bat をダブルクリック
  - n-gramメモリ(per_layer_token_embd)はRAM置き（公式推奨、VRAM節約）
  - OpenAI互換API: http://127.0.0.1:8181/v1/chat/completions
  - ブラウザで http://127.0.0.1:8181 に.WebUIも付いてくる

## 推奨サンプル設定
temperature 0.7 / top_p 0.8 / top_k 20 / repeat_penalty 1.05
max_tokens は 4096 以上（thinkingが長い）。greedydecodeはループするので禁止。

## thinking制御
chat_template_kwargs: {"enable_thinking": true} が本命（trueで考える、falseで即答）

## 実測 (RTX 4090 24GB)
- 全GPU載せ(Q5_K_M): 約11.7 tok/s・VRAM ~23.9GB（このbatがその構成）
- n-gramメモリをCPU置き(-ot per_layer_token_embd=CPU)は逆に遅かった(7 tok/s)ので不採用
- VRAMが足りないPC用の公式フォールバック:
  -ot "per_layer_token_embd=CPU" -ot "\\.ffn_(up|down|gate)_exps\\.=CPU" (4-8 tok/s)
"""
open(os.path.join(B, "README_JA.md"), "w", encoding="utf-8").write(readme)
print("wrote", os.path.join(B, "start_server.bat"))
print("wrote", os.path.join(B, "README_JA.md"))
