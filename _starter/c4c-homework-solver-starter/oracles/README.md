# Oracle Source Documents

This directory contains the oracle knowledge sources that were distilled into the T-box
(`domain_skills/calculus_limits.yaml`). Each document represents a different layer of
authoritative knowledge about calculus limits.

## How Oracle Ingestion Works

```
Oracle Document → Read & Extract → Distill into T-box entries:
  - Concept nodes (definitions, theorems)
  - Solution methods (computational approaches)
  - Conceptual templates (definitions, counterexamples, proof patterns)
  - Classification rules (how to map problem text → concept)
  - Validation rules (how to check answer correctness)
  - Common errors (what students get wrong)
```

## Oracle Sources (Priority Order)

| # | File | Type | Authority | What It Provides |
|---|------|------|-----------|------------------|
| 1 | `01_textbook_stewart.md` | Textbook | Primary | Formal definitions, theorems, proofs |
| 2 | `02_study_guide.md` | Study Guide | Primary | Distilled concepts, learning sequences, common pitfalls |
| 3 | `03_instructor_guide.md` | Instructor Guide | Primary | Teaching strategies, problem-solving frameworks, exam traps |
| 4 | `04_pedagogy_guide.md` | Pedagogy Guide | Primary | ε-δ proof teaching method (GCSC), grading rubrics, error taxonomy |
| 5 | `05_exemplars.md` | Exemplars | Secondary | Berkeley Math 1A Worksheets 3-4 with expected answers |

## For Students

When extending the solver to a new domain (e.g., derivatives, integrals, linear algebra):

1. **Gather oracle sources** — textbook chapters, worked examples, instructor notes
2. **Extract T-box entries** — identify concepts, methods, classification keywords
3. **Write the domain YAML** — follow the structure in `calculus_limits.yaml`
4. **Implement solver templates** — parameterized code for each solution method
5. **Test against exemplars** — verify solve rate on known problems

The quality of your T-box directly determines your solve rate. More oracle sources = better coverage.
