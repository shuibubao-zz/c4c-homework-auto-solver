# C4C —— 作业自动求解与排版（卢怡然）

> 从 Claude 基线出发，迁移到国产大模型，并从「微积分极限」扩展到「线性代数 + 常微分方程」。
> 目标级别：**Level 3**

**English summary:** This repo takes the Claude-based starter kit and migrates it to Chinese LLMs (DeepSeek / Qwen / Kimi) while adding two new subject domains. On a real 12-problem linear algebra homework set it auto-solves 10 with 34/34 symbolic verification checks passing, and keeps the Claude baseline intact at 17/18 (94.4%).

---

## 目录一览（即 GitHub 提交全集）

```
C4C/
├── README.md                          ← 你在这里
├── homework-solver/                   ← 可运行技能包（完整流水线）
│   └── tests/golden/                  ← ★ Claude 基线黄金（pristine starter 实跑固化 + sha256）
├── evidence/                          ← 端到端留档 + 自检输出
│   ├── run/                           ← 1_ingested / 2_parsed / 3_solutions / tex / pdf / run_report
│   │   └── 关于_llm_calls.jsonl的说明.md   ← 为什么没有真模型调用记录
│   ├── selftest_run.txt               ← 自检 45/45 完整输出
│   ├── final_check.txt                ← 提交前核对 27/27 完整输出
│   └── skill_manifest.json            ← .skill 包内每个文件的 sha256
│
├── pack_skill.py                      ← 重新打包 .skill（含包内哈希自校验）
├── final_check.py                     ← 提交前核对：7 项必交 + 包完整性 + 一致性（27 项）
│
├── 卢怡然_C4C_方案设计.md              ← 【必交】架构、模型选型理由、求解策略
├── 卢怡然_C4C_验证报告.md              ← 【必交】10 题答案对比 + Claude 基线对比
├── 卢怡然_C4C_教学说明.md              ← 【必交】安装、使用、支持哪些课程
├── 卢怡然_C4C_拿来说明.md              ← 【必交】拿了什么、Claude 版 vs 国产版差异
├── 卢怡然_C4C_AI日志.md                ← 【必交·无此项无法评审】开发全过程 AI 使用记录
├── 卢怡然_C4C_作业原件.md              ← 【必交】真实作业输入（线性代数，12 题）
├── 卢怡然_C4C_output.pdf              ← 【必交】真实作业输出（7 页中文 PDF）
├── 卢怡然_C4C_homework-solver.skill   ← 【必交】打包的技能包
│
├── c4c-homework-solver-starter.zip    ← Claude 基线原件（sha256 与下发包一致）

# 以下三项本地存在但不提交（见 .gitignore）
#   _starter/   基线对照源码，用于重新固化基线黄金
#   _archive/   早期调试草稿，已被 tests/golden/ 取代
```

---

## 结果速览

| 指标 | 结果 |
|---|---|
| 真实作业求解率 | 10 / 12（83.3%） |
| 符号回验 | 10 / 10 通过，共 **34 项断言全绿** |
| Claude 基线保持 | **17 / 18 = 94.4%**，三个阶段的 JSON 与基线**逐字段一致** |
| 新增学科 | 线性代数（10 个求解器）+ 常微分方程（3 个求解器） |
| Stage 5 编译验证 | 6 / 6 通过，7 页中文 PDF，465,789 字节 |
| 自检套件 | **45 / 45** 通过 |
| **未完成** | 第 11、12 题缺真实国产模型调用（无 API key），详见下方声明 |

---

## 快速开始

```bash
pip install -r homework-solver/requirements.txt

# 一键跑通（无需 API key 也能出 PDF）
python homework-solver/scripts/pipeline.py \
    "C:/Users/卢怡然/Desktop/C4C/卢怡然_C4C_作业原件.md" \
    "C:/Users/卢怡然/Desktop/C4C/evidence/run" \
    --compile --course "线性代数（工科）" --student "卢怡然" --lang zh

# 自检
python homework-solver/tests/selftest.py
```

更多用法见 `卢怡然_C4C_教学说明.md`。

---

## 核心设计：一条铁律

> **凡是 SymPy 能确定性算出来的，绝不让 LLM 猜；LLM 只做推理、证明与讲解，且不参与答案正确性判定。**

由此产生一个反直觉的收益：**换 DeepSeek / Qwen / Kimi 跑同一个包，前 10 题的答案逐字节不变。** 答案不依赖模型，学科才有可复用性。

```
① 域 T-box + 确定性 SymPy solver   ← 答案的权威来源（34 项独立回验）
② legacy starter kit solve.py      ← 保住 Claude 基线（字节未改）
③ 国产 LLM                         ← 推理/证明/讲解，永不当答案裁判
```

---

## 加一门新学科要改几行框架代码？

**零行。** 两步：

1. 往 `homework-solver/domain_skills/` 丢一个 yaml（概念 / 解法 / 分类规则）
2. 在 `homework-solver/scripts/solvers_<学科>.py` 里注册同名 solver

`MultiDomainClassifier` 会自动扫描 `domain_skills/` 下所有 yaml。我加「常微分方程」这个域时 `classify.py` 确实一行没改。

---

## ⚠️ 诚实声明：本次未发生真实国产模型调用

- 开发环境中 `DEEPSEEK_API_KEY` / `DASHSCOPE_API_KEY` / `MOONSHOT_API_KEY` 均为空，常见配置目录扫描无命中。
- 因此第 11、12 题（证明题 / 概念说明题）输出为「未求解」，PDF 中如实标注，**没有伪造任何答案**。
- 适配层本身经过验证（T4 组用本地 mock OpenAI 服务真发 HTTP，6/6 通过），但那只能证明代码正确，**不能证明 DeepSeek 真的被调过**。这两个区别我没有混为一谈。
- 详见 `evidence/run/关于_llm_calls.jsonl的说明.md` 与 `卢怡然_C4C_验证报告.md` §6。

拿到 key 后补齐这条证据只需一条命令（见上述说明文件）。

---

## 依赖

```
Python >= 3.10    SymPy  NumPy  PyYAML  requests(可选)  pypdf  python-docx
LaTeX：TeX Live / MiKTeX + ctex 宏包（中文 PDF 需要）
```

本包**默认不会**自动安装任何东西。缺依赖时会明确告诉你要装什么；确认要它自动装请加 `--allow-install`。
