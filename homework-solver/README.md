# C4C Homework Auto-Solver（国产模型 · 多域扩展版）

> **上游**：Claude 基线 starter kit（`c4c-homework-solver-starter.zip`）
> **改动**：迁移到 DeepSeek / Qwen / Kimi；新增线性代数、常微分方程两个学科；新增国产模型适配层、Stage 5 编译验证、中文 LaTeX 模板、自检套件。
> **作者**：卢怡然　|　2026-10-08

SIAS AI+X Elite 20 — Coding for Cognition Challenge C4C。
一个本体驱动的（ontology-grounded）作业求解器：把原始作业变成可直接提交的答案 PDF。
**领域知识与题目实例分离** —— 扩展靠扩展它"知道什么"，而不是写更多代码。

---

## 结果

| 测试 | 学科 | 求解 | 回验 |
|---|---|---|---|
| 真实作业 12 题（`../卢怡然_C4C_作业原件.md`） | 线性代数 | **10 / 12** | 34/34 断言通过 |
| Claude 基线 test1 + test2（`--engine legacy`） | 微积分极限 | 17 / 18 = 94.4% | 与基线逐字段一致 |
| 自检套件 `tests/selftest.py` | —— | **45 / 45** | —— |

---

## 快速开始

```bash
pip install -r requirements.txt

# 线性代数作业 → 中文 PDF
python scripts/pipeline.py 作业.md out/ --compile \
       --course "线性代数（工科）" --student "卢怡然" --lang zh

# 微积分极限 → 走 Claude 基线的原求解器
python scripts/pipeline.py test_cases/test2_limits.md out/ --engine legacy

# 自检（45 项，含反向验证）
python tests/selftest.py
python tests/selftest.py --quick        # 跳过 PDF 编译，更快
```

不需要 API key 也能跑出完整 PDF（计算题走 SymPy）。详见 `../卢怡然_C4C_教学说明.md`。

---

## 五阶段流水线

```
① Ingest     ingest.py         PDF/Word/Markdown/LaTeX → 结构化文本
② Parse      parse_problems.py 题号 / 公式 / 子题 / 类型
③ Solve      solve_ext.py      Classify → Retrieve → Instantiate → Execute → Validate
④ Render     render_latex.py   中文模板（ctex）+ 回验徽章 + 汇总表
⑤ Compile    compile_pdf.py    编译 + 6 项验证（V1–V6）
```

### 求解优先级

```
① 域 T-box + 确定性 SymPy solver    ← 答案的权威来源
② legacy starter kit solve.py       ← 保住 Claude 基线（字节未改）
③ 国产 LLM                          ← 推理/证明/讲解，永不当答案裁判
```

**铁律：凡是 SymPy 能确定性算出来的，绝不让 LLM 猜。**
LLM 的输出**不参与**答案正确性判定，并在 PDF 中被显式标注。

---

## 目录结构

```
├── SKILL.md                    ← 给 AI agent 读的技能说明
├── scripts/
│   ├── pipeline.py             ← 一键 Stage 1–5
│   ├── ingest.py               ← Stage 1（starter 原件）
│   ├── parse_problems.py       ← Stage 2（starter 原件）
│   ├── solve.py                ← Stage 3 starter 原求解器（字节未改）
│   ├── solve_ext.py            ← ★ 混合调度器
│   ├── solvers_linalg.py       ← ★ 线性代数 10 个求解器 + 回验
│   ├── solvers_ode.py          ← ★ 常微分方程 3 个求解器 + 回验
│   ├── llm_client.py           ← ★ 国产模型适配层（deepseek/qwen/kimi）
│   ├── render_latex.py         ← Stage 4（改造：ctex、徽章、汇总表）
│   ├── compile_pdf.py          ← ★ Stage 5 编译 + 六项验证
│   └── bootstrap.py            ← 依赖检查（改为默认不自动安装）
├── domain_skills/              ← 领域本体；加学科只需丢 yaml
│   ├── calculus_limits.yaml        （starter 原件）
│   ├── linear_algebra.yaml         ★ 10 concepts / 10 methods / 11 rules
│   └── differential_equations.yaml ★ 3 concepts / 3 methods / 3 rules
├── tests/
│   ├── selftest.py             ← ★ 45 项自检（含 T3 反向验证）
│   ├── record_golden.py        ← ★ 固化 pristine starter 基线黄金
│   └── golden/                 ← 基线黄金 + MANIFEST（含 sha256）
└── test_cases/                 ← Berkeley Math 1A 原始用例（未改动）
```

★ = 本项目新增或重写。

---

## 加一个新学科

**不需要改任何框架代码。**

1. 往 `domain_skills/` 丢 `<学科>.yaml`（照 `linear_algebra.yaml` 的结构写：`concepts` / `solution_methods` / `classification_rules`）
2. 在 `scripts/solvers_<学科>.py` 里实现同名 solver，并在 `solve_ext.py` 的 `DOMAIN_SOLVER_MODULES` 注册

`MultiDomainClassifier` 自动扫描 `domain_skills/` 下所有 yaml，按 `priority` 全局降序合成分类器。
加「常微分方程」时 `classify.py` 一行未改 —— 这点可以当场验。

---

## 关于国产模型

```bash
export DEEPSEEK_API_KEY=sk-xxxxxx        # 或 DASHSCOPE_API_KEY / MOONSHOT_API_KEY
python scripts/pipeline.py 作业.md out/ --compile --provider deepseek \
       --llm-log out/llm_calls.jsonl
```

`--provider` 可选 `deepseek`（默认）/ `qwen` / `kimi`，三家都是 OpenAI 兼容端点。

**不配 key 也能用**：计算类题目走 SymPy，与 LLM 无关。只是证明题/概念题会标注为「未求解」——
**这是刻意的**，本包不会在没有凭据时伪造答案，也不会静默降级假装成功。

---

## 已知限制

| 限制 | 现状 |
|---|---|
| 证明题 / 概念题 | 需真实国产模型调用；无 key 时如实标注「未求解」 |
| xelatex 在部分 Windows 机器不可用（fontconfig 缺失） | 自动降级 pdflatex + ctex，中文正常 |
| 图片 / 扫描 PDF | 未实现（需 OCR 或 Vision），公式识别可靠性不足，不做半成品 |
| 超大矩阵性能 | 未针对 GPU/并行优化 |

---

## Key Insight

```
Solve rate = domain knowledge coverage（且是 domain-scoped 的）
```

求解器的能力取决于它从 oracle 里学到了什么，而不是代码有多复杂。
上游 starter 在极限域内 94.4%、域外 40%，正是这条规律的实证。
本项目的扩展走的也是这条路：**加 yaml 本体，而不是加 if-else。**
