"""
Solver Template: ε-δ Neighborhood Notation
T-box concept: epsilon_delta_notation
Tool: template (no computation needed)

Oracle source: Stewart Ch. 2.4, Berkeley Math 1A Worksheet 3 Problems 1–3.
The oracle teaches three equivalent representations:
  inequality:     a - δ < x < a + δ (with optional x ≠ a)
  absolute_value: |x - a| < δ (or 0 < |x-a| < δ)
  interval:       (a - δ, a + δ) (or punctured: (a-δ,a) ∪ (a,a+δ))
"""


# ──────────────────────────────────────────────
# Template lookup table (T-box knowledge)
# ──────────────────────────────────────────────

TEMPLATES = {
    # center=0, exclude=False
    ("0", False): {
        "inequality":     r"-\delta < x < \delta",
        "absolute_value": r"|x| < \delta",
        "interval":       r"(-\delta, \delta)",
        "graph":          r"\text{Number line: open circles at } -\delta, \delta",
    },
    # center=0, exclude=True
    ("0", True): {
        "inequality":     r"-\delta < x < 0 \text{ or } 0 < x < \delta",
        "absolute_value": r"0 < |x| < \delta",
        "interval":       r"(-\delta, 0) \cup (0, \delta)",
        "graph":          r"\text{Number line: open circles at } -\delta, 0, \delta",
    },
    # center=a, exclude=False
    ("a", False): {
        "inequality":     r"a - \delta < x < a + \delta",
        "absolute_value": r"|x - a| < \delta",
        "interval":       r"(a - \delta, a + \delta)",
        "graph":          r"\text{Number line: open circles at } a-\delta, a+\delta, \text{ center at } a",
    },
    # center=a, exclude=True
    ("a", True): {
        "inequality":     r"a - \delta < x < a + \delta, \quad x \neq a",
        "absolute_value": r"0 < |x - a| < \delta",
        "interval":       r"(a - \delta, a) \cup (a, a + \delta)",
        "graph":          r"\text{Number line: open circles at } a-\delta, a, a+\delta",
    },
}


def solve(
    center: str,                # "0" or "a"
    exclude_center: bool,       # whether x ≠ center
    representation: str,        # "inequality" | "absolute_value" | "interval" | "graph"
) -> dict:
    """
    Generate the ε-δ notation for 'x within δ of center'.

    This is a pure template solver — no computation, just knowledge retrieval
    from the T-box. The oracle (textbook) defines these equivalences; the solver
    reproduces them.
    """
    key = (center, exclude_center)
    templates = TEMPLATES.get(key)

    if not templates:
        return {
            "solved": False,
            "answer": None,
            "answer_latex": "",
            "steps": [f"Unknown configuration: center={center}, exclude={exclude_center}"],
            "method": "template_lookup_failed",
        }

    answer_latex = templates.get(representation, templates["absolute_value"])

    # Build explanation steps
    center_desc = f"${center}$"
    exclude_desc = " (not equal to center)" if exclude_center else ""
    steps = [
        f"$x$ within $\\delta$ of {center_desc}{exclude_desc}:",
        f"${answer_latex}$",
    ]

    # Show all three equivalent forms for completeness
    if representation != "graph":
        equiv_forms = [f"${templates[r]}$" for r in ["inequality", "absolute_value", "interval"]]
        steps.append("Equivalent forms: " + " $\\Leftrightarrow$ ".join(equiv_forms))

    return {
        "solved": True,
        "answer": answer_latex,
        "answer_latex": answer_latex,
        "steps": steps,
        "method": "template",
    }
