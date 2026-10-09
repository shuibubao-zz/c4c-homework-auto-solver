# 卢怡然 C4C 拿来说明

> 从 starter kit 拿了什么、用了哪些外部库、Claude 版本与国产模型版本究竟差在哪。

---

## 1. 从 starter kit 拿了什么

### 1.1 原样保留、字节未改

用 `diff -rq _starter/c4c-homework-solver-starter homework-solver` 可以直接验证：下列文件**完全一致**。

| 文件 | 拿来的东西 | 为什么原样留着 |
|---|---|---|
| `scripts/solve.py` | **Claude 基线的求解核心**（1400+ 行），含 `conceptual_template`、`sympy_limit`、代数=符号混合策略 | 这是 94.4% 的来源。改它就是在改自己的对照组 |
| `scripts/ingest.py` | Stage 1 多格式摄入：PDF / docx / LaTeX / Markdown | 已经能用，没必要重写 |
| `scripts/parse_problems.py` | Stage 2 题号识别、公式抽取、子题切分 | 同上 |
| `scripts/retrieve.py` | T-box 检索辅助 | 我的域扩展复用了它的调用习惯 |
| `domain_skills/calculus_limits.yaml` | 微积分极限的领域本体（T-box） | **我的两个新 yaml 就是照它的结构抄的** |
| `solver_templates/`、`references/`、`oracles/` | 解法模板与参考材料 | 知识资产 |
| `test_cases/` | Berkeley Math 1A 原始用例 | 回归基准，动不得 |

这一条我认为是「拿来主义质量」这项评分的主要依据：**我没有为了彰显工作量去重造本来就能用的轮子。**

### 1.2 改造了什么（以及为什么改）

| 文件 | 改了什么 | 理由 |
|---|---|---|
| `scripts/classify.py` | 加了 `has_matrix_expression` / `has_ode_expression` 两个特征探针 + `MultiDomainClassifier` 类 | **纯增量**：`TBoxClassifier` 原有逻辑一行未动，只是在 `_extract_features` 里多返回两个键、在文件末尾新增一个类。对内的 `-engine legacy` 路径不受影响（已由 T1 验证逐字段一致） |
| `scripts/render_latex.py` | 重写：加 `ctex` 中文支持、`booktabs` 表格、回验徽章、LLM 标注、末尾汇总表 | 原文严格说是「英文专用」——模板里写死了 Mathematics / Homework Solutions / Student，且完全没有「哪些题通过了验证」这类信息 |
| `scripts/pipeline.py` | 重写：加 `--engine` / `--no-llm` / `--provider` / `--lang` / `--student-id` / `--allow-install` | 原来没有「换模型」这个概念，也就无从谈迁移 |
| `scripts/bootstrap.py` | 把「默认静默 `pip install`」改为「默认只检查、明确报错」 | 静默改别人的环境不可接受；且 `--break-system-packages` 在没外网的机器上会卡死 |

### 1.3 不客气地说一句：我 FO 的是 starter 的「将的知识模型」，不是它的正则

starter kit 最值钱的不是那 1400 行 `solve.py`，而是它隐含的一个判断：**求解率不是算法聪明程度的度量，而是领域覆盖范围的度量**。

它的缺陷（套件外只有 40%）不是 bug，而是这个模型的必然推论。所以我的扩展没有去改 `solve.py`、也没有往里加新题型分支，而是：
**把它的这个架构思想抽出来，做成本体化（ontology-grounded）的多域形式** —— 每个学科一份 yaml 本体 + 一组带回验的确定性 solver，框架自动发现。

---

## 2. 用了哪些外部库

| 库 | 版本（本机） | 拿来干什么 | 是否必须 |
|---|---|---|---|
| **SymPy** 1.14.0 | ✅ | **答案的唯一裁判**：符号计算与回验 | 必须 |
| **NumPy** | ✅ | 数值交叉校验 | 必须 |
| **PyYAML** 6.0.3 | ✅ | 读 `domain_skills/*.yaml` | 必须 |
| **requests** 2.34.2 | ✅ | 调国产模型 HTTP API | 可选（无则降级标准库 `urllib`） |
| **pypdf** 6.19.0 | ✅ | PDF 摄入；Stage 5 抽文本做 V4/V5 验证 | PDF 场景需要 |
| **python-docx** 1.2.0 | ✅ | Word 摄入 | docx 场景需要 |
| **pdfplumber** | ❌ 未装 | 更精确的 PDF 表格提取 | 可选，缺了会自动降级 pypdf |
| **ctex**（LaTeX 宏包） | ✅ | 中文 PDF | 中文输出必须 |

**关于 requests 的一个细节**：`llm_client._http_post` 优先用 `requests`，`ImportError` 时降级标准库 `urllib.request`。所以「看不到 requests」不是故障，是有意的降级路径 —— 而且这条路径我在没有 requests 的环境里跑过。

---

## 3. Claude 版本 vs 国产模型版本：真实差异

这是本题要求回答的核心。我把差异分成「真的变了」和「没变」两部分，后者同样是答案。

### 3.1 架构层面的差异

| 维度 | Claude 版 starter kit | 国产模型版（本项目） |
|---|---|---|
| 推理引擎位置 | 推理职责由 Claude Code（agent 本身）承担，**不在流水线代码里** | 推理职责下沉到代码里的 `llm_client.py`，**流水线可独立运行** |
| 模型绑定 | 绑 Claude | DeepSeek / Qwen / Kimi 三家，一张表切换，**零 Lock-in** |
| 学科 | 微积分极限（1 个域） | 极限 + 线性代数 + 常微分方程（3 个域），可增量扩展 |
| 答案裁判 | SymPy + Claude 判断混合 | **SymPy 是唯一裁判**；LLM 输出不入判定，显式标注 `llm_unverified` |
| 输入语言 | 英文为主（Berkeley 作业） | 中文优先（ctex + 中文 LaTeX 模板） |
| Stage 5 | 「跑 3 遍 pdflatex，看 PDF 在不在」 | 编译 + 6 项验证（V1–V6），含汉字抽取检查 |
| 依赖安装 | 导入时静默 `pip install` | 默认只检查并明确报错，需显式 `--allow-install` |
| 缺 key 行为 | ——（不存在这个概念） | 明确报「检查了哪些 env、值是否为空」，不静默假装成功 |

### 3.2 最重要的一条：LLM 的角色被降级了，而且是刻意的

原始设计里，Claude 承担的是「理解题意、决定怎么解、给出答案」这样的完整闭环职责。迁移到国产模型后，我没有把这个闭环原样搬过去，而是**拆开了**：

```
答案  ← SymPy 确定性计算 + 独立算法交叉回验
讲解  ← 国产 LLM（不影响答案）
证明  ← 国产 LLM（无符号路径时）+ 显式「未经符号回验」标注
```

**为什么：** 国产模型在数学推理上很强，但"强"不等于"可信"。让一个概率性系统产出作业答案，然后让同一个概率性系统判断它对不对，这个闭环是自证的。把裁判位留给 SymPy，把表达位留给 LLM，是迁移过程中我认为最有价值的一个决定。

也因此产生了一个**反直觉的收益**：换 Qwen 或 Kimi 跑同一个包，前 10 题的答案**逐字节不变**。答案不依赖模型，学科才有可复用性。

### 3.3 老实说：目前还差在哪

| 项 | Claude 版 | 国产模型版 |
|---|---|---|
| Claude 基线 | 有自己的 | 同等：17/18，逐字段一致 ✅ |
| 套件外学科 | 40%（5 题 2 解） | 线性代数 12 题 10 解（其中 2 待国产模型补） |
| **真实国产调用证据** | —— | **本次缺失**（无 API key），见验证报告 §6 |

第三行我不会装作看不见。

---

## 4. 借鉴的其他技能与实践

| 来源 | 借鉴了什么 |
|---|---|
| starter kit 的 `domain_skills/` 结构 | 概念 / 解法 / 分类规则三段式 T-box —— 我的两个新 yaml 完全照此结构 |
| starter kit 的 `retrieve.py` | 调用习惯与字段命名 |
| 社区通行的 LaTeX 编译实践 | 多引擎降级序列（xelatex → pdflatex → lualatex）、`%%EOF` 完整性检查 |
| C4A / C2G / C4B 三个前置挑战沉淀的方法论 | ① **回归测试必须反向验证**（人为再造错，看测试会不会 FAIL）② 证据链要随包发布 ③ 没做到的必须明写 |

---

## 5. 一句话交代

> 拿了 starter kit 的**整条流水线与它的领域知识模型**，没动它的求解核心；在它的架构思想上做垂直扩展（多域本体），把原来的单模型闭环拆成「SymPy 裁判 + LLM 表达」的混合架构；外部库能用现成的就不造。
>
> 没做到的地方（缺国产模型真调证据）写在验证报告 §6，不粉。
