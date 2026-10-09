#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国产大模型适配层 (Domestic LLM Adapter Layer)
=============================================

C4C 的核心迁移点：把 starter kit 里由 Claude 承担的「推理 / 证明 / 文字解释」
职责，迁移到国产大模型上。

设计原则
--------
1. **OpenAI 兼容协议**：DeepSeek / Moonshot(Kimi) / 通义千问(兼容模式) 都提供
   OpenAI 兼容的 /chat/completions 接口，因此只维护一套 HTTP 调用代码，
   通过 PROVIDERS 表切换 base_url / model / key 环境变量。
2. **零新增依赖**：优先用 requests，requests 不存在时降级到标准库 urllib。
   这样在没有网络的机器上 import 本模块不会崩。
3. **不做静默降级**：没有 key 时抛 LLMUnavailable，由调用方显式决定
   （跳过 / 标记未求解）。绝不假装"模型说过了"。
4. **全程留档**：每次真实调用把 (provider, model, 耗时, token, prompt 前 200 字,
   response 前 200 字) 追加写入 jsonl，供验证报告核对。

环境变量
--------
    DEEPSEEK_API_KEY    DeepSeek 开放平台 key（默认 provider）
    DASHSCOPE_API_KEY   通义千问（Qwen）
    MOONSHOT_API_KEY    Moonshot（Kimi）
    C4C_LLM_LOG         留档 jsonl 路径（可选，默认不写）
    C4C_LLM_PROVIDER    覆盖默认 provider: deepseek|qwen|kimi|custom

用法
----
    from llm_client import LLMClient
    client = LLMClient()                      # 自动按 provider 优先级探测 key
    if client.available():
        text = client.chat("求矩阵 A 的特征值，只给结果")
    else:
        print(client.unavailable_reason())    # 明确告诉用户为什么没调
"""

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# Provider 注册表
# ─────────────────────────────────────────────────────────────
# 说明：base_url 均为各厂商官方文档公开的 OpenAI 兼容端点。
# 如需换厂商，只改这张表，不用动调用逻辑。

PROVIDERS = {
    "deepseek": {
        "label": "DeepSeek（深度求索）",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "key_env": "DEEPSEEK_API_KEY",
        "doc": "https://api-docs.deepseek.com/",
    },
    "qwen": {
        "label": "通义千问 Qwen（阿里云百炼，OpenAI 兼容模式）",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
        "key_env": "DASHSCOPE_API_KEY",
        "doc": "https://help.aliyun.com/zh/model-studio/",
    },
    "kimi": {
        "label": "Kimi（Moonshot AI）",
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-8k",
        "key_env": "MOONSHOT_API_KEY",
        "doc": "https://platform.moonshot.cn/docs/",
    },
}

# 探测顺序：谁有 key 用谁
DEFAULT_PROVIDER_ORDER = ["deepseek", "qwen", "kimi"]


class LLMUnavailable(Exception):
    """没有可用 key / 网络不通时抛出。调用方必须显式处理，不得假装成功。"""


class LLMError(Exception):
    """接口返回非 200 或解析失败时抛出。"""


def _http_post(url: str, headers: dict, payload: dict, timeout: int) -> dict:
    """
    发一个 POST。优先 requests（若已装），否则用标准库 urllib。
    返回解析后的 dict。
    """
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    try:
        import requests  # 可选依赖
        resp = requests.post(url, headers=headers, data=body, timeout=timeout)
        raw = resp.text
        status = resp.status_code
    except ImportError:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode("utf-8", errors="replace")
                status = r.getcode()
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            status = e.code

    if status != 200:
        raise LLMError(f"HTTP {status}: {raw[:400]}")

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise LLMError(f"响应不是合法 JSON: {e}; 前 200 字符={raw[:200]}")


class LLMClient:
    """国产大模型客户端（OpenAI 兼容协议）。"""

    def __init__(
        self,
        provider: str = None,
        model: str = None,
        base_url: str = None,
        api_key: str = None,
        timeout: int = 120,
        log_path: str = None,
        temperature: float = 0.2,
    ):
        self.provider = provider or os.environ.get("C4C_LLM_PROVIDER")
        self._explicit_model = model
        self._explicit_base = base_url
        self._explicit_key = api_key
        self.timeout = timeout
        self.temperature = temperature
        self.log_path = log_path or os.environ.get("C4C_LLM_LOG")
        self._resolved = False
        self._unavailable_reason = None

    # ── provider 解析 ──────────────────────────────────────

    def _resolve(self):
        """按优先级挑一个真正有 key 的 provider。"""
        if self._resolved:
            return
        self._resolved = True

        if self._explicit_key:
            pname = self.provider or "deepseek"
            spec = PROVIDERS.get(pname, {
                "label": pname, "base_url": self._explicit_base or "",
                "model": self._explicit_model or "", "key_env": None, "doc": "",
            })
            if not spec.get("base_url"):
                self._unavailable_reason = f"provider={pname} 未提供 base_url"
                return
            self._active = self._make_active(pname, spec, self._explicit_key)
            return

        order = [self.provider] if self.provider else DEFAULT_PROVIDER_ORDER
        tried = []
        for pname in order:
            spec = PROVIDERS.get(pname)
            if not spec:
                continue
            key = os.environ.get(spec["key_env"], "").strip()
            tried.append(f"{pname}({spec['key_env']}={'有' if key else '空'})")
            if key:
                self._active = self._make_active(pname, spec, key)
                return

        self._unavailable_reason = (
            "未检测到任何国产模型的 API key。已检查：" + "、".join(tried) + "。"
            "设置对应环境变量后重试；或用 --no-llm 明确以「纯 SymPy」模式运行"
            "（报告中会如实标注未调用模型）。"
        )

    def _make_active(self, pname, spec, key):
        return {
            "provider": pname,
            "label": spec.get("label", pname),
            "base_url": (self._explicit_base or spec["base_url"]).rstrip("/"),
            "model": self._explicit_model or spec.get("model", ""),
            "key": key,
            "doc": spec.get("doc", ""),
        }

    # ── 对外接口 ──────────────────────────────────────────

    def available(self) -> bool:
        self._resolve()
        return hasattr(self, "_active")

    def unavailable_reason(self) -> str:
        self._resolve()
        return self._unavailable_reason or ""

    @property
    def active(self) -> dict:
        self._resolve()
        if not hasattr(self, "_active"):
            raise LLMUnavailable(self._unavailable_reason)
        return self._active

    def describe(self) -> str:
        """给报告用的一行描述。"""
        if not self.available():
            return f"未启用：{self.unavailable_reason()}"
        a = self.active
        return f"{a['label']} / model={a['model']} / endpoint={a['base_url']}"

    def chat(
        self,
        prompt: str,
        system: str = None,
        max_tokens: int = 2048,
        temperature: float = None,
        tag: str = "",
    ) -> str:
        """
        发一次对话请求，返回模型输出文本。

        失败一律抛 LLMError / LLMUnavailable，不返回空串冒充成功。
        """
        a = self.active
        url = f"{a['base_url']}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {a['key']}",
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": a["model"],
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": self.temperature if temperature is None else temperature,
            "stream": False,
        }

        t0 = time.time()
        try:
            data = _http_post(url, headers, payload, self.timeout)
        except Exception as e:
            self._log({
                "ok": False, "tag": tag, "error": str(e)[:300],
                "provider": a["provider"], "model": a["model"],
                "elapsed": round(time.time() - t0, 2),
                "prompt_head": prompt[:200],
            })
            raise LLMError(str(e))
        elapsed = round(time.time() - t0, 2)

        try:
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
        except (KeyError, IndexError, TypeError) as e:
            self._log({"ok": False, "tag": tag, "error": f"响应结构异常: {e}",
                       "raw_head": json.dumps(data, ensure_ascii=False)[:300]})
            raise LLMError(f"响应结构异常: {e}")

        self._log({
            "ok": True, "tag": tag,
            "provider": a["provider"], "model": a["model"],
            "endpoint": a["base_url"],
            "elapsed": elapsed,
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "prompt_head": prompt[:200],
            "response_head": content[:200],
        })
        return content

    # ── 留档 ──────────────────────────────────────────────

    def _log(self, record: dict):
        if not self.log_path:
            return
        try:
            p = Path(self.log_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            import datetime
            record["ts"] = datetime.datetime.now().isoformat(timespec="seconds")
            with open(p, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            pass  # 留档失败不能影响主流程，但会在控制台提示

    # ── 连通性自检 ────────────────────────────────────────

    def ping(self) -> dict:
        """发一条最小请求，确认 key 与网络可用。返回结果 dict。"""
        if not self.available():
            return {"ok": False, "reason": self.unavailable_reason()}
        try:
            txt = self.chat("只回复两个字：可用", max_tokens=16, tag="ping")
            return {"ok": True, "reply": txt.strip()[:50], **self.active}
        except Exception as e:
            return {"ok": False, "reason": str(e)[:300], **self.active}


# ─────────────────────────────────────────────────────────────
# CLI：python llm_client.py --ping
# ─────────────────────────────────────────────────────────────

def main():
    import argparse
    ap = argparse.ArgumentParser(description="国产大模型适配层自检")
    ap.add_argument("--ping", action="store_true", help="发一条最小请求验证连通性")
    ap.add_argument("--provider", help="deepseek|qwen|kimi")
    ap.add_argument("--ask", help="直接问一句")
    args = ap.parse_args()

    c = LLMClient(provider=args.provider)
    print("适配器状态:", c.describe())
    if not c.available():
        print("不可用原因:", c.unavailable_reason())
        raise SystemExit(2)
    if args.ping or args.ask:
        r = c.chat(args.ask or "只回复两个字：可用", max_tokens=256, tag="cli")
        print("模型回复:", r)


if __name__ == "__main__":
    main()
