# 关于 evidence/run/llm_calls.jsonl 的说明

**本文件中不含任何真实的大模型调用记录。**

原因：开发环境里没有可用的国产模型 API key。

- 已检查的环境变量：`DEEPSEEK_API_KEY`、`DASHSCOPE_API_KEY`、`MOONSHOT_API_KEY` —— 均为空
- 已扫描的配置位置：`~/.workbuddy`、`~/.config`、常见 Skill 配置目录 —— 无命中
- `~/.workbuddy-key-fallback` 存在但为空目录

因此本次流水线以 `--no-llm` 运行，`llm_client.py` 一次都没有被调用，也没有生成 jsonl 留档。

## 这与「适配层可用」是两件事

`selftest.py` 的 T4 组用本地 mock OpenAI 服务真发 HTTP 验证了适配层本身（6/6 通过），
但那**只证明代码正确，不证明 DeepSeek / Qwen / Kimi 真的被调过**。

## 拿到 key 后如何补齐这条证据

```bash
export DEEPSEEK_API_KEY=sk-xxxxxx
python homework-solver/scripts/pipeline.py \
    "C:/Users/卢怡然/Desktop/C4C/卢怡然_C4C_作业原件.md" \
    "C:/Users/卢怡然/Desktop/C4C/evidence/run" \
    --compile --course "线性代数（工科）" --student "卢怡然" --lang zh \
    --llm-log "C:/Users/卢怡然/Desktop/C4C/evidence/run/llm_calls.jsonl"
```

届时本文件开头的声明应当被改写，并同步更新 `卢怡然_C4C_验证报告.md` §1 与 §3 的第 11、12 行。
