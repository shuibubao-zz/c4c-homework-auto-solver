# Oracle Source 1: Textbook — Stewart/Kokoska, Calculus

**Type:** Textbook (highest authority)
**Reference:** Stewart/Kokoska, *Calculus: Concepts and Contexts*, 5th ed., Chapter 2

## Key Definitions Extracted

### 2.1 Tangent Line
- **Formal:** The tangent line to curve y = f(x) at point P(a, f(a)) is the line through P with slope:
  m = lim_{x→a} [f(x) - f(a)] / (x - a)
- **Equation:** y - f(a) = f'(a)(x - a)
- **Horizontal tangent:** occurs where f'(x) = 0

### 2.2 Limit of a Function
- **Intuitive:** lim_{x→a} f(x) = L means f(x) approaches L as x approaches a
- **Formal (ε-δ):** For every ε > 0, there exists δ > 0 such that:
  0 < |x - a| < δ ⟹ |f(x) - L| < ε
- **One-sided limits:** lim_{x→a⁻} f(x) and lim_{x→a⁺} f(x)
- **Two-sided exists ⟺** both one-sided exist and are equal

### 2.3 Limit Laws
- Sum: lim[f + g] = lim f + lim g (both must exist)
- Product: lim[f · g] = lim f · lim g (both must exist)
- Quotient: lim[f / g] = lim f / lim g (lim g ≠ 0)
- **Critical prerequisite:** laws only apply when individual limits exist

### 2.4 Continuity
- f is continuous at a if: (1) f(a) is defined, (2) lim_{x→a} f(x) exists, (3) lim_{x→a} f(x) = f(a)
- For continuous functions: can "plug in" to evaluate limits

### 2.5 Squeeze Theorem
- If g(x) ≤ f(x) ≤ h(x) near a (except possibly at a), and lim g(x) = lim h(x) = L, then lim f(x) = L
- Canonical example: lim_{x→0} x² sin(1/x) = 0

### 2.6 Intermediate Value Theorem (IVT)
- If f is continuous on [a, b] and N is between f(a) and f(b), then ∃c ∈ (a,b) with f(c) = N
- Application: fixed point proof — if f continuous on [0,1] with f(0)≥0, f(1)≤1, then ∃c with f(c) = c

## Concepts Extracted → T-box Nodes

| Textbook Section | → T-box Concept ID | Node Type |
|-----------------|-------------------|-----------|
| 2.1 | `tangent_line`, `horizontal_tangent` | concept, solution_method |
| 2.2 | `limit_definition`, `one_sided_limit`, `epsilon_delta_proof` | concept, proof_pattern |
| 2.3 | `limit_computation`, `limit_laws` | solution_method |
| 2.4 | `continuity` | concept |
| 2.5 | `squeeze_theorem` | concept |
| 2.6 | `intermediate_value_theorem` | concept |

## What This Oracle Provides to the T-box

- **Formal definitions** → concept node `formal` fields
- **Theorem statements** → conceptual template content
- **Proof structures** → proof_pattern templates
- **Computation methods** → solution_method solver templates
- **Prerequisites** → concept graph edges (requires, specializes)
