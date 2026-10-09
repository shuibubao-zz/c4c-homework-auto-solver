# 卢怡然 C4C 教学说明

> 怎么安装、怎么用、支持哪些课程 —— 面向「拿到这个包就想跑起来」的人。
> 环境假设：Windows / macOS / Linux 通用，Python ≥ 3.10。

---

## 1. 三分钟上手指北

### 1.1 装依赖

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r homework-solver/requirements.txt
```

需要 `sympy pyyaml numpy python-docx pypdf requests`。

> ⚠️ 本包**默认不会**自动 `pip install`。这是刻意的：starter kit 原来会在导入时就静默装包，我不想在一个「别人也要用」的技能里偷偷修改你的 Python 环境。缺什么它会明确告诉你装什么。
> 如果你确认要它自动装，加 `--allow-install`。

### 1.2 装 LaTeX（要出 PDF 才需要）

- **Windows**：TeX Live 完整安装，然后补一个宏包 —— 中文文档需要 `ctex`。
  ```bash
  # 若本机装的是 MiKTeX，包名同样叫 ctex
  tlmgr install ctex
  ```
  > 用户名含中文时 `tlmgr` 可能报 `Error in tempdir() ... Illegal byte sequence`。
  > 解决办法是把临时目录指向纯 ASCII 路径，见 `卢怡然_C4C_方案设计.md` §5。
- **macOS**：`brew install --cask mactex-no-gui`
- **Linux**：`sudo apt install texlive-full texlive-lang-chinese`

不想装？用 `--no-compile` 只生成 `.tex`，丢到 Overleaf 编译即可。

### 1.3 跑第一份作业

```bash
python homework-solver/scripts/pipeline.py \
    卢怡然_C4C_作业原件.md out/ \
    --compile \
    --course "线性代数（工科）" \
    --student "卢怡然" \
    --lang zh
```

跑完 `out/` 下会出现：

| 文件 | 是什么 |
|---|---|
| `1_ingested.json` | Stage 1：原文被切成的结构化段落 |
| `2_parsed.json` | Stage 2：识别出的题目、子题、公式 |
| `3_solutions.json` | Stage 3：每题答案 + 解题步骤 + **回验明细** |
| `homework.tex` | Stage 4：LaTeX 源码 |
| `homework.pdf` | Stage 5：可直接提交的 PDF |
| `run_report.json` | 运行报告，含 Stage5 的六项验证结果 |

---

## 2. 支持的输入格式

| 格式 | 支持情况 | 依赖 |
|---|---|---|
| Markdown `.md` | ✅ | 内置 |
| LaTeX `.tex` | ✅ | 内置 |
| 文本型 PDF | ✅ | `pypdf` |
| Word `.docx` | ✅ | `python-docx` |
| 图片/扫描 PDF | ❌ 未做 | 需要 OCR 或 Vision；公式识别可靠性不足，不做半成品 |

支持的题号格式：`第 N 题` / `Problem N` / `N.` / `N)` / `Q.N`。

**建议在交作业 Markdown 时把矩阵写成 `\begin{pmatrix} ... \end{pmatrix}`**，这是解析器抓矩阵的主入口。写在代码块里也能解析。

---

## 3. 支持的课程与题型

### 3.1 线性代数（本次的主目标）

| 题型 | 关键词示例 | 触发的 solver |
|---|---|---|
| 行列式 | 行列式、det、det(A) | `determinant_solver` |
| 逆矩阵 | 逆矩阵、inverse、A⁻¹ | `matrix_inverse_solver` |
| 矩阵乘法 | 乘积、AB、matrix product | `matrix_product_solver` |
| 矩阵的秩 | 秩、rank | `matrix_rank_solver` |
| 线性方程组 | 解方程组、cases 环境 | `linear_system_solver` |
| 特征值/特征向量 | 特征值、特征向量、eigen | `eigen_decomposition_solver` |
| 矩阵对角化 | 对角化、diagonalize、P⁻¹AP=D | `diagonalization_solver` |
| 施密特正交化 | 正交化、Gram-Schmidt、正交单位 | `gram_schmidt_solver` |
| 二次型 | 二次型、正交变换、标准形 | `quadratic_form_solver` |
| 奇异值分解 | 奇异值、SVD、UΣVᵀ | `svd_solver` |

### 3.2 常微分方程

支持 `y''`、`dy/dx`、`\frac{d^2y}{dx^2}` 三种写法：

| 题型 | solver |
|---|---|
| 通解（`y'' + 3y' + 2y = 0`） | `ode_solver` |
| 初值问题（带 y(0)=1, y'(0)=0） | `ode_solver` + `ics` 逐条回验 |
| 拉普拉斯正/反变换 | `laplace_transform_solver` |

### 3.3 微积分极限（Claude 基线，完整保留）

用 `--engine legacy` 可以走 starter kit 的原始求解器：

```bash
python homework-solver/scripts/pipeline.py \
    homework-solver/test_cases/test2_limits.md out/ --engine legacy
```

---

## 4. 怎么再加一门课（这是设计的核心）

**加一个新学科不需要改任何框架代码。** 两步：

### 第 1 步：写一个 yaml

往 `homework-solver/domain_skills/` 丢一个 `<学科>.yaml`：

```yaml
domain: probability_statistics
oracle_sources:
  - title: 某本教材
    location: 第 X 章
concepts:
  - id: expectation
    name: 数学期望
    # ...
solution_methods:
  - id: expectation_solver
    concept_id: expectation
    # ...
classification_rules:
  - id: rule_expectation
    concept_id: expectation
    solver_id: expectation_solver
    priority: 90
    conditions:
      - key: text_contains
        value: "期望"
```

### 第 2 步：注册同名 solver

在 `homework-solver/scripts/solvers_<学科>.py` 里实现 `expectation_solver(parsed) -> dict`，
然后在模块末尾注册、并在 `solve_ext.py` 的 `DOMAIN_SOLVER_MODULES` 里加一行。

**`classify.py` 一行都不用改。** 我加微分方程这个域的时候确实没改它 —— 这件事本身就是「可复用性」的证据。

> 分类规则按 `priority` 降序匹配。建议把最具体、最容易误判的规则排高（例如「奇异值/SVD」prio 98），把 `has_matrix_expression: true` 这类兜底规则排低（prio 60）。

---

## 5. 关于国产大模型

### 5.1 不配 key 也能用

**是的。** 计算类题目（本作业的第 1–10 题）走 SymPy，与 LLM 完全无关，不配 key 也能出完整 PDF。只是第 11、12 题这类证明/概念题会标注为「未求解」。

### 5.2 配了 key 会怎样

```bash
export DEEPSEEK_API_KEY=sk-xxxxxx          # 或 DASHSCOPE_API_KEY / MOONSHOT_API_KEY
python homework-solver/scripts/pipeline.py 作业.md out/ --compile --lang zh \
       --llm-log out/llm_calls.jsonl
```

`--llm-log` 会把每次调用记成 jsonl（时间戳、provider、model、token 数、耗时）。留个调用记录，回头能对账。

### 5.3 换模型

```bash
--provider deepseek   # 默认
--provider qwen
--provider kimi
```

三家都走 OpenAI 兼容协议，换 provider 只改 base_url 和 model，**其他代码不动**。

### 5.4 重要：LLM 的产出会被标出来

这是刻意设计，**请不要把红色警告当作 bug**：

| 标注 | 含义 |
|---|---|
| 🟢 **回验徽章 n/n** | 答案经过 n 项独立符号回验，全部通过 |
| 🔴 **未经符号回验** | 这一题的答案本身来自 LLM，没有符号回验，**请自己核对** |
| ⚪ **AI 讲解，仅供参考** | 这一段的文字是 LLM 写的讲解；答案另有出处，讲解不影响答案 |

一句话：**让 LLM 说的话，和让它评判的答案，必须分开。**

---

## 6. 常见问题

**Q：PDF 里中文是豆腐块 / 方框？**
Stage 5 的 V5 验证会拦截这种情况（会报「抽取到的汉字数不足」）。真遇到的话检查 `homework.tex` 首部是否有 `\usepackage{ctex}`；`--lang zh` 默认会加。

**Q：xelatex 报 Fontconfig error？**
本机会自动降级到 `pdflatex`（走 CJK 字体），这是预期的。引擎尝试顺序是 xelatex → pdflatex → lualatex，任一成功即返回。

**Q：为什么输出目录传绝对路径更稳？**
曾经有个 bug：传相对路径时 PDF 会落到嵌套子目录里被误判为失败。已修复并加了回归测试，但用绝对路径仍然是最省事的习惯。

**Q：某题标了 `[none] 未求解`？**
说明这道题 SymPy 没有确定性路径，且没配 LLM key（或配了但那题是证明题还没走通）。看 `3_solutions.json` 里该题的 `classify_reason` 字段，能看到它被判成哪一类的原因。

**Q：怎么确认真跑通了而不是碰巧？**

```bash
python homework-solver/tests/selftest.py        # 45 项
python homework-solver/tests/selftest.py --quick   # 跳过 PDF 编译，快一点
```

---

## 7. 文件地图

```
homework-solver/
├── SKILL.md                # 技能说明（给 AI agent 读的）
├── README.md               # 项目速览
├── requirements.txt
├── scripts/
│   ├── pipeline.py         # 一键跑 Stage 1–5（你最常碰的就是它）
│   ├── ingest.py           # Stage 1
│   ├── parse_problems.py   # Stage 2
│   ├── solve.py            # Stage 3 —— starter kit 原求解器，字节未改
│   ├── solve_ext.py        # Stage 3 —— 混合调度器（新增）
│   ├── solvers_linalg.py   # 线性代数确定性求解器 + 回验（新增）
│   ├── solvers_ode.py      # 微分方程确定性求解器 + 回验（新增）
│   ├── llm_client.py       # 国产模型适配层（新增）
│   ├── render_latex.py     # Stage 4
│   ├── compile_pdf.py      # Stage 5 编译 + 六项验证（新增）
│   └── bootstrap.py        # 依赖检查（改为默认不自动安装）
├── domain_skills/          # 领域本体：加学科只需丢 yaml
│   ├── calculus_limits.yaml
│   ├── linear_algebra.yaml
│   └── differential_equations.yaml
├── tests/
│   ├── selftest.py         # 45 项自检
│   ├── record_golden.py    # 固化 pristine starter 基线黄金
│   └── golden/             # 基线黄金 + MANIFEST（含 sha256）
└── test_cases/             # Berkeley 原始用例（来自 starter kit，未改动）
```
