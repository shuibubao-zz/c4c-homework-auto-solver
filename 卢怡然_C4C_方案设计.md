# 卢怡然 C4C 方案设计

> 挑战：作业自动求解与排版 —— 从 Claude 基线出发，迁移到国产大模型，并从「微积分极限」扩展到新学科。
> 作者：卢怡然　|　完成日期：2026-10-08　|　目标级别：**Level 3**

---

## 0. 一句话总结

把 starter kit 的五阶段流水线从「Claude + 微积分极限」迁移到 **「DeepSeek/Qwen/Kimi + 多域（线性代数 + 微分方程）」**，核心设计是一条**混合求解铁律**：

> **凡是 SymPy 能确定性算出来的，绝不让 LLM 猜；LLM 只负责推理、证明与讲解，且不参与答案正确性判定。**

在 12 道真实线性代数作业题上：**10 题自动求解，10 题通过符号回验（共 34 项回验全绿）**，输出 7 页可直接提交的中文 PDF。

---

## 1. 选型：为什么是 DeepSeek，而不是 Qwen / Kimi

CHALLENGE.md 推荐 Qwen 3.6 / Kimi 2.5，DeepSeek 标为「也可尝试」。我的选择是 **DeepSeek 优先，Qwen / Kimi 作为零成本切换的备选**，理由如下。

### 1.1 决定性理由：架构上不做 Lock-in

三家都提供 **OpenAI 兼容的 `/chat/completions` 端点**，字段结构一致（`Authorization: Bearer <key>`、 `messages`、`usage`）。因此我把模型差异收敛成一张 `PROVIDERS` 表：

| provider | base_url | model | key 环境变量 |
|---|---|---|---|
| `deepseek`（默认） | `https://api.deepseek.com` | `deepseek-chat` | `DEEPSEEK_API_KEY` |
| `qwen` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` | `DASHSCOPE_API_KEY` |
| `kimi` | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` | `MOONSHOT_API_KEY` |

切换只需一个参数：`--provider qwen`。**「迁移质量」这项评分考察的是迁移是否完整、可复现，而不是用了哪一家**。把三家都做成同一层抽象下的可选项，比只支持一家更符合「迁移」的本意，也让评审（或同学）在没有 DeepSeek key 时仍能复跑。

### 1.2 次要理由

- **数学/代码能力**：DeepSeek-V3 系列在数学竞赛题与代码上的公开表现与 Qwen 处于同一梯队，足以承担「生成证明思路 / 讲解」这类任务。
- **成本**：国产模型 API 价格量级相当，DeepSeek 的缓存命中机制对本场景（同一份作业会重跑多次）更省。

### 1.3 这一点必须说清楚

**本系统不会因为是 DeepSeek 就改变答案。** 见 §3 的职责划分：国产模型只出现在 SymPy 无确定性路径的题目上（本作业的第 11、12 题），并且其输出会带 `llm_unverified` 标记，PDF 里用醒目颜色标注「未经符号回验」。换 Kimi 或 Qwen 跑同一个 `.skill` 包，前 10 题的答案**逐字节不变**。

---

## 2. 目标课程与学科扩展

| 项 | 选择 | 理由 |
|---|---|---|
| 目标课程 | **线性代数（工科）** | CHALLENGE 明确允许，且被列为 Level 3 推荐方向 |
| 真实作业 | 同济《线性代数》第七版风格的 12 题（见 `卢怡然_C4C_作业原件.md`） | 覆盖矩阵运算→特征值→正交化→二次型→SVD 的完整知识链 |
| 第二域 | 常微分方程（`ordinary_differential_equations`） | 证明「加一个新学科不需要改框架代码」 |

### 2.1 学科覆盖情况

`domain_skills/linear_algebra.yaml`：10 个概念、10 个解法、11 条分类规则，2 个 oracle 来源。
`domain_skills/differential_equations.yaml`：3 个概念、3 个解法、3 条分类规则，2 个 oracle 来源。

| 题型 | 求解器 | 回验项数 |
|---|---|---|
| 行列式 | `determinant_solver` | 2 |
| 逆矩阵 | `matrix_inverse_solver` | 3 |
| 矩阵乘法 | `matrix_product_solver` | 2 |
| 矩阵的秩 | `matrix_rank_solver` | 3 |
| 线性方程组 | `linear_system_solver` | 3 |
| 特征值/特征向量 | `eigen_decomposition_solver` | 7 |
| 矩阵对角化 | `diagonalization_solver` | 4 |
| 施密特正交化 | `gram_schmidt_solver` | 2 |
| 二次型正交标准化 | `quadratic_form_solver` | 4 |
| 奇异值分解 SVD | `svd_solver` | 4 |
| 通解/初值问题 | `ode_solver` | 残差回代 + 初值逐条验 |
| 拉普拉斯变换 | `laplace_transform_solver` | 正逆变换互验 + 定义式数值积分比对 |

---

## 3. 求解策略：三档分工（本方案的核心）

这是我最想强调的设计，也是我认为比「用哪个模型」重要得多的东西。

```
① 域 T-box + 确定性 SymPy solver      ← 答案的权威来源
② legacy starter kit solve.py         ← 保住 Claude 基线，兜 calculus 极限
③ 国产 LLM                            ← 推理/证明/讲解，永不当答案裁判
```

### 3.1 铁律与它的两个推论

**铁律：凡是 SymPy 能确定性算出来的，绝不让 LLM 猜。**

推论一：LLM 的输出**不参与**答案正确性判定。判断 `det(A) = -3` 对不对的是 `det()` 与 `berkowitz_det()` 两种算法的一致性、`det(A)·det(A⁻¹) = 1`，不是 DeepSeek 的自述。

推论二：LLM 生成的内容必须**显式标注**。在 PDF 里，任何来自 LLM 的文本都带灰色「AI 讲解，仅供参考」标签；如果某一题的答案本身来自 LLM（不是讲解），标签升级为红色警告「未经符号回验」。

### 3.2 一个非显然的例外

第 11、12 题（证明题 / 概念说明题）**跳过 legacy 路径**，即使 legacy 声称能解。

原因是被实际调试逼出来的：legacy 的 `conceptual_template` 是照着 Berkeley Math 1A 英文题干调出来的关键词模板，把它用在中文线代证明题上，会输出一篇**语法通顺、排版漂亮、但答非所问**的文字 —— 这比留白更危险，因为它看起来像答案。所以我在 `solve_ext.py` 里加了 `is_proof` 正则：

```python
is_proof = bool(re.search(r"证明|试证|说明|为什么|explain why|prove|show that|verify that", text))
if (result is None or not result["solved"]) and not is_proof:
    # 才允许退回 legacy
```

「看起来像答案」的东西，必须比「明确说不会」更谨慎地对待。

---

## 4. 架构：五阶段流水线

```
① Ingest     ingest.py         PDF/Word/Markdown/LaTeX/图片 → 结构化文本
② Parse      parse_problems.py 题号 / 公式 / 类型 / 子题
③ Solve      solve_ext.py      Classify → Retrieve → Instantiate → Execute → Validate
④ Render     render_latex.py   中文模板（ctex）+ 自检徽章 + 汇总表
⑤ Compile    compile_pdf.py    编译 + 6 项验证（V1–V6）
```

### 4.1 核心洞察：Solve rate = domain coverage

读完 starter kit 之后我得到的最重要认识是：**那个 94.4% 不是「某个聪明算法」的产物，而是「它恰好覆盖了这一族的 18 道题」的产物**。题目一换到套件外，立刻掉到 40%（CHALLENGE.md 自己给的 5 道进阶题只解出 2 道）。

于是扩展的正确姿势不是「再写一堆正则去匹配新题」，而是把**领域知识**与**题目实例**分离：

- `domain_skills/*.yaml` 存放一个学科的本体：概念（T-box）、解法（solution_methods）、分类规则（classification_rules）
- `solvers_*.py` 存放确定性执行 + 回验
- `MultiDomainClassifier` 自动扫描 `domain_skills/` 下**所有** yaml，按 priority 全局降序合成一个分类器

**加一个新学科，只需丢一个新 yaml + 注册同名 solver，`classify.py` 一行都不用改。** 我加第二个域（微分方程）时确实没改框架代码 —— 这件事本身就写在 discover 的注释里，也是我对「可复用性」这项评分的主要回答。

### 4.2 Stage 3 的执行链

```
Classify     题干 → 命中哪条规则 → concept_id / solver_id / domain
Retrieve     载入对应 solution_method 的提示骨架
Instantiate  从题干抽出的矩阵/方程 → SymPy 对象
Execute      调用确定性 solver
Validate     独立算法回验（这一步不可跳过）
```

### 4.3 Stage 5 的六项验证

Stage 5 在 starter kit 里只是「跑 3 遍 pdflatex，看 PDF 在不在」。我把它拆成独立 stage 并加了验证：

| 验 | 内容 | 为什么要有 |
|---|---|---|
| V1 | PDF 存在且 > 1KB | 空文件不等于成功 |
| V2 | 页数 ≥ 1 | 编译成功但内容为空 |
| V3 | 日志无致命错误 | Undefined control sequence / Missing $ / LaTeX Error / Fontconfig error |
| V4 | 抽取文本无 `??` | 未解析的交叉引用 |
| V5 | 中文文档确实含汉字（≥20） | **防止 ctex 没生效变成豆腐块** —— 这一条专门为中文加 |
| V6 | 文件尾部含 `%%EOF` | 文件被截断 |

---

## 5. 关于中文 PDF：一个具体踩坑

本机 TeX Live 2026 **原本没有 xelatex**（只有 pdflatex / lualatex），而 CHALLENGE.md 说「xelatex 支持中文，推荐」。

安装过程有个坑值得记录：`tlmgr` 在**用户名含中文**的 Windows 上会崩（`Error in tempdir() ... Illegal byte sequence`），因为 perl 的临时目录继承了含中文的路径。绕法是把三个临时目录环境变量全部指向纯 ASCII 路径，并直接调 TeX Live 自带的 perl：

```
MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' \
PERL5LIB='C:/texlive/2026/tlpkg/tlperl/lib' \
TMPDIR='C:\Users\Public\tltmp' TMP='C:\Users\Public\tltmp' TEMP='C:\Users\Public\tltmp' \
./tlpkg/tlperl/bin/perl.exe ./texmf-dist/scripts/texlive/tlmgr.pl install ctex
```

装完 ctex 后**实测**：

- `xelatex` **失败**：`Fontconfig error: Cannot load default config file` / `Kpathsea is not working`（本机 fontconfig 配置缺失，强修会污染系统环境，不值得）
- `pdflatex + ctex` **成功**：走 CJK 字体（SimSun/SimHei），抽查 872 个汉字渲染正常

所以引擎顺序定为 **xelatex → pdflatex → lualatex，任一成功即返回**。这是三条经验换来的：中文文档不要假定 xelatex 一定可用；不要为了跑一个 skill 去改系统 fontconfig；降级路径必须真正跑过而不是写在注释里。

---

## 6. 诚实的边界

我在开始前给自己定过一条纪律（来自 C3 的教训：**没有的东西不能写成有**），这条纪律在本方案里体现为三处：

1. **缺依赖不明装**。starter kit 的 `bootstrap.py` 默认静默 `pip install`，我改成默认只检查、明确报错并给出手动安装命令，需要 `--allow-install` 才自动装。理由：静默改别人的 Python 环境是不可接受的，而且 `--break-system-packages` 在没有外网的机器上会卡死。
2. **缺 API key 不明降级**。`llm_client.available()` 返回 False 时会通过 `unavailable_reason()` 明确说明「检查了哪些环境变量、值是否为空」，而不是假装成功、然后在 PDF 里悄悄少两道题而无解释。
3. **第 11、12 题的状态如实反映**。详见 `卢怡然_C4C_验证报告.md` §6。

---

## 7. 待办与已知限制

| 限制 | 现状 | 说明 |
|---|---|---|
| 第 11、12 题（证明/概念） | 需要真实国产模型调用才能闭环 | 无 key 时明确标注「未求解」，不伪造 |
| xelatex 在本机不可用 | 已自动降级到 pdflatex | 换机子上 xelatex 可用时会自动优先选用 |
| GPU / 大矩阵性能 | 未针对超大矩阵优化 | 教学目标下的 3×3~5×5 无压力 |
| 手写公式识别 | 未实现（需 Vision） | OCR 识别数学公式的可靠性不足，不做半成品 |
