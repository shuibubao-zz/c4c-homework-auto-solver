# Oracle Source 2: Study Guide

**Type:** Study Guide (distilled pedagogical knowledge)
**Reference:** 微积分学习指南：概念、上下文与精确定义 (Distilled from Stewart + Berkeley Math 1A)
**Language:** Bilingual (Chinese + English)

## Distilled Knowledge

### ε-δ Proofs — Four Keywords Method
1. **Given** (任意): For any ε > 0
2. **Choose** (取): Choose δ = [expression depending only on ε]
3. **Suppose** (假设): Suppose 0 < |x - a| < δ
4. **Check** (验证): Then |f(x) - L| = ... < ε ✓

**Critical rule:** δ CANNOT depend on x — it must be fixed before x is chosen.

### Common Student Errors (High-Value for Classification)
- Confusing "limit exists" with "function is defined"
- Writing δ as a function of x (illegal dependency)
- Forgetting the punctured neighborhood (0 < |x - a|, not just |x - a| < δ)
- Applying L'Hôpital without verifying 0/0 or ∞/∞ precondition
- Treating ∞ as a real number

### Learning Sequence
1. Intuitive limits (graphical, numerical) → formal definition
2. ε-δ notation (neighborhoods) → ε-δ proofs (linear) → ε-δ proofs (nonlinear)
3. Limit laws → continuity → IVT
4. Derivative as limit → tangent lines → differentiation rules

### Key Formulas & Methods
- **L'Hôpital's Rule:** If lim f(x)/g(x) = 0/0 or ∞/∞, then lim f(x)/g(x) = lim f'(x)/g'(x)
- **Newton's Method:** x_{n+1} = x_n - f(x_n)/f'(x_n)
- **Implicit differentiation:** Differentiate both sides w.r.t. x, apply chain rule, solve for dy/dx
- **Growth hierarchy:** ln(x) ≪ x^p ≪ e^x as x → ∞

## What This Oracle Provides to the T-box

- **Classification keywords** → new classification rules (L'Hôpital, Newton's method, implicit diff)
- **Error patterns** → validation rules (check for common mistakes)
- **Learning sequence** → prerequisite edges in concept graph
- **Method summaries** → solver template specifications
