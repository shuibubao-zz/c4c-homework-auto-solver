# Oracle Source 4: Pedagogy Guide

**Type:** Pedagogy Guide (ε-δ proof teaching and assessment methodology)
**Reference:** ε-δ 极限证明教学与评估规范指南 (senior math education consultant)
**Authority:** Primary

## Core Insight: The Paradigm Shift

The pedagogy guide identifies a fundamental paradigm shift that students must make:

```
BEFORE (intuitive):  "What value does f(x) approach?" → discovering L
AFTER  (rigorous):   "Can you PROVE that for any ε?" → verifying L for all ε
```

This shift is analogous to going from "guessing the answer" to "proving it in court."

## Game Metaphor for ε-δ

The guide introduces a game-theoretic metaphor:

| Role | Action | Analogy |
|------|--------|---------|
| **Challenger** | Gives ε > 0 (any positive number) | "I bet you can't get f(x) within ε of L" |
| **Responder** | Produces δ > 0 | "Watch this — take any x within δ of a" |
| **Verification** | Check |f(x) - L| < ε for all such x | The bet is settled |

**Key rule:** The Responder's δ must be **fixed before** any specific x is tested. This is why δ cannot depend on x.

## Preliminary Analysis vs. Formal Proof

The guide sharply distinguishes two phases:

### Phase 1: Preliminary Analysis (Scratchwork)
- **Direction:** Work BACKWARDS from |f(x) - L| < ε to find what δ should be
- **Goal:** Discover the relationship δ = g(ε)
- **This is NOT the proof** — it's reverse engineering

### Phase 2: Formal Proof (GCSC)
- **Direction:** Work FORWARDS from the chosen δ
- **Structure:** Given ε → Choose δ → Suppose 0 < |x-a| < δ → Check (forward deduction)
- **Critical:** Must use FORWARD deduction in the Check step, not repeat the scratchwork

### Common Confusion
Students often write the scratchwork as the proof. The guide emphasizes:
- Scratchwork: "We need |f(x) - L| < ε. So we need |...| < ε. So δ = ..."  (backward)
- Proof: "Suppose 0 < |x - a| < δ. Then |f(x) - L| = |...| ≤ ... < ε."  (forward)

## Error Taxonomy (4 Common Errors)

### Error 1: Illegal Dependency
```
WRONG:  "Choose δ = ε / |x + 3|"     ← δ depends on x!
RIGHT:  "Choose δ = min(1, ε/7)"      ← δ depends only on ε
```
**Why it's wrong:** δ must be fixed BEFORE x is chosen (game rule: Responder moves before seeing specific x).

### Error 2: Scratchwork Confusion
```
WRONG:  "We need |f(x) - L| < ε, so |x - a| < ε/C, so choose δ = ε/C. Done."
RIGHT:  Phase 1 (scratchwork) → discover δ = ε/C.
        Phase 2 (proof) → Given ε, choose δ = ε/C. Suppose 0<|x-a|<δ. Then [forward chain].
```

### Error 3: Binding Error
```
WRONG:  "... < ε. Therefore δ = ε/7."  ← appears at the END of the proof
RIGHT:  δ is CHOSEN at the BEGINNING, then verified at the end
```

### Error 4: Missing Punctured Neighborhood
```
WRONG:  "Suppose |x - a| < δ"         ← allows x = a
RIGHT:  "Suppose 0 < |x - a| < δ"     ← excludes x = a (punctured)
```

## Grading Rubric (Assessment Criteria)

| Component | Weight | Criteria |
|-----------|--------|----------|
| Correct δ selection | 40% | δ > 0, depends only on ε, works for all x in punctured neighborhood |
| Forward deduction | 60% | Starts from 0 < |x-a| < δ, deduces |f(x)-L| < ε by chain of inequalities |

## min-Notation for Nonlinear Functions

For nonlinear f(x), the variable factor |g(x)| must be bounded:

```
Example: f(x) = x², a = 3, L = 9
  |x² - 9| = |x - 3| · |x + 3|
                ↑ controlled    ↑ variable (depends on x!)

  Restrict: δ ≤ 1 ⟹ |x - 3| < 1 ⟹ 2 < x < 4 ⟹ |x + 3| < 7

  So: |x² - 9| = |x - 3| · |x + 3| < δ · 7

  Want: δ · 7 < ε ⟹ δ < ε/7

  Choose: δ = min{1, ε/7}
```

The `min{1, ε/7}` ensures BOTH constraints are met:
- δ ≤ 1 (so the bound |x + 3| < 7 holds)
- δ ≤ ε/7 (so the final inequality gives < ε)

## Conjugate Method for Radicals

For f(x) = √x at a = 4, L = 2:
```
  |√x - 2| = |√x - 2| · |√x + 2| / |√x + 2| = |x - 4| / |√x + 2|

  Since √x + 2 ≥ 2 for x ≥ 0: |√x - 2| ≤ |x - 4| / 2

  Choose: δ = 2ε. Then |√x - 2| ≤ δ/2 = ε. ✓
```

## What This Oracle Provides to the T-box

- **Game metaphor** → enriched conceptual template for ε-δ understanding
- **GCSC structure** → `epsilon_delta_proof_method` concept enrichment
- **Preliminary Analysis / Formal Proof** → dual-phase solver template
- **Error taxonomy** → 4 `common_errors` entries in concept node
- **Grading rubric** → validation rule weights (40% δ selection, 60% forward deduction)
- **min-notation** → `epsilon_delta_nonlinear` strategy_variants
- **Conjugate method** → additional solver variant for radical functions
