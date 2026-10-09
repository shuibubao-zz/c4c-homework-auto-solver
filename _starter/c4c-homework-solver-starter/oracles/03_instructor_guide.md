# Oracle Source 3: Instructor Guide

**Type:** Instructor Guide (teaching strategies + problem-solving frameworks)
**Reference:** 伯克利 Math 1A 极限概念全解析与工作单解题指南 (Berkeley chief calculus lecturer)
**Authority:** Primary

## GCSC Proof Structure (ε-δ)

The canonical structure for ε-δ proofs, extracted from the instructor's grading rubric:

```
G — Given:   "Let ε > 0 be given."
C — Choose:  "Choose δ = [expression]. Note δ > 0 since ε > 0."
S — Suppose: "Suppose 0 < |x - a| < δ."
C — Check:   "Then |f(x) - L| = [algebra] < ε. ■"
```

### Nonlinear ε-δ Strategy
For f(x) = x² at a = 3, L = 9:
1. Need: |x² - 9| < ε, given |x - 3| < δ
2. Factor: |x² - 9| = |x - 3| · |x + 3|
3. **Bound the variable factor:** Restrict δ ≤ 1, then |x - 3| < 1 ⟹ 2 < x < 4 ⟹ |x + 3| < 7
4. So |x² - 9| < 7|x - 3| < 7δ
5. **Choose:** δ = min{1, ε/7}
6. Then |x² - 9| < 7 · (ε/7) = ε ✓

### Limit Scenario Classification
The instructor identifies 5 limit scenarios that cover all worksheet problems:

| Scenario | What Happens | Approach |
|----------|-------------|----------|
| Continuous | f(a) is defined, plug in | Direct substitution |
| Removable discontinuity | 0/0 form, simplifiable | Factor/cancel, then substitute |
| Jump discontinuity | Left ≠ Right | Evaluate one-sided limits |
| Infinite discontinuity | Denominator → 0 | Determine sign → ±∞ |
| Oscillatory | No limit (e.g., sin(1/x)) | Show two subsequences with different limits |

### Algebraic Toolbox (ranked by frequency of use)
1. **Factoring** — for 0/0 indeterminate forms (most common)
2. **Rationalization** — multiply by conjugate (for square root expressions)
3. **Simplification** — combine fractions, expand, cancel
4. **Squeeze theorem** — for bounded × vanishing products
5. **Variable substitution** — t = 1/x, t = π/n, etc.

### Exam Traps (High-Value for Template Matching)
- "Is ∞ a number?" → No, ∞ ∉ ℝ; writing lim = ∞ means divergence
- "Can you always exchange limit and sum?" → No, need both limits to exist
- "Does differentiable ⟹ continuous?" → Yes; converse is false (|x| at 0)
- "Recognize lim_{x→1} (x^1000 - 1)/(x - 1)" → This IS the derivative definition: f'(1) where f(x) = x^1000

### Growth Hierarchy
For limits at infinity, the dominant term wins:
```
ln(x) ≪ x^p ≪ a^x ≪ x! ≪ x^x    (as x → ∞, for any p > 0, a > 1)
```

### IVT and Fixed Points
- **IVT statement:** f continuous on [a,b], N between f(a) and f(b) ⟹ ∃c ∈ (a,b): f(c) = N
- **Fixed point proof:** Let g(x) = f(x) - x. Then g(0) = f(0) ≥ 0 and g(1) = f(1) - 1 ≤ 0. By IVT, ∃c with g(c) = 0, i.e., f(c) = c.

## What This Oracle Provides to the T-box

- **GCSC structure** → enriched `epsilon_delta_proof_method` concept with detailed template
- **Nonlinear ε-δ strategy** → `epsilon_delta_nonlinear` with strategy_variants and worked example
- **Scenario classification** → 5 new conceptual template entries
- **Algebraic toolbox** → classification rules for limit solving methods (priority 48)
- **Exam traps** → conceptual template trigger keywords
- **Growth hierarchy** → conceptual template (priority 60)
- **IVT + fixed point** → conceptual template (priority 65)
