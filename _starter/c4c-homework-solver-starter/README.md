# C4C Homework Auto-Solver Starter Kit

**SIAS AI+X Elite 20 — Coding for Cognition Challenge**

An ontology-grounded homework solver that converts raw math worksheets into submission-ready answer sheets. Domain knowledge is separated from problem instances, making the system extensible by expanding what the solver *knows* rather than writing more code.

## Exemplar Results

Validated against Berkeley Math 1A Worksheets 3–4 (18 problems total):

| Test | Domain | Solved | Rate |
|------|--------|--------|------|
| Worksheet 3 | Tangent lines & ε-δ notation | 8/8 | **100%** |
| Worksheet 4 | Limits | 9/10 | **90%** |
| **Combined** | | **17/18** | **94.4%** |

Also tested against 5 advanced challenge problems (integration, optimization, combinatorics, physics):

| Test | Domain | Auto-Solved | Manual | Rate |
|------|--------|-------------|--------|------|
| Challenge | Beyond limits domain | 2/5 | 5/5 | **40% auto / 100% manual** |

**Caveat:** The 94.4% rate is specific to the limits domain. Advanced problems outside the solver's domain knowledge require new domain extensions (see CHALLENGE.md L2–L4). Full manual solutions are provided in `challenge_answers_cn.pdf`.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run on a test case
python scripts/pipeline.py test_cases/test1_tangent_epsilon_delta.md output/

# View the output
cat output/3_solutions.json   # Solutions with steps
cat output/homework.tex       # Generated LaTeX
```

## What's in the Kit

```
├── CHALLENGE.md              ← Student challenge guide (L1→L4 graded tasks)
├── SKILL.md                  ← Skill documentation + pipeline usage
├── scripts/                  ← 5-stage pipeline (ingest → parse → solve → render → compile)
├── domain_skills/            ← Domain knowledge: calculus_limits.yaml
├── solver_templates/         ← Parameterized SymPy + template solvers
├── oracles/                  ← Oracle source documents (textbook, study guide, instructor guide, pedagogy guide)
├── test_cases/               ← Berkeley Math 1A worksheets + validated outputs
├── references/               ← LaTeX template + SymPy cheatsheet
├── examples/                 ← Sample input + output
├── *_cn.pdf                  ← Chinese worksheets + answer sheets (limits domain)
└── challenge_answers_cn.pdf  ← Advanced challenge answers (5 problems, manually solved)
```

## Start Here

1. **Read** `CHALLENGE.md` for the graded challenge tasks
2. **Run** the exemplar pipeline on both test cases
3. **Study** the domain knowledge (`domain_skills/calculus_limits.yaml`) and solver code
4. **Reverse-engineer** the architecture from code — understand *how* it works, then extend it
5. **Extend** to a new math domain

## Key Insight

```
Solve rate = domain knowledge coverage (domain-scoped)
```

The solver's capability is determined by what it has learned from oracle sources, not by code complexity. To solve more problems, expand the domain knowledge with new concepts, solvers, and classification rules. The challenge problems prove this empirically: 94.4% within the limits domain, 40% outside it.

## Requirements

- Python 3.10+
- SymPy, PyYAML
- XeLaTeX + Noto Sans CJK SC (optional, for Chinese PDF output)
