"""
Solver Template: Limit Does Not Exist (One-Sided Disagreement)
T-box concept: limit_existence
Tool: SymPy

Oracle source: Stewart Ch. 2.2 — "lim_{x→a} f(x) exists iff
lim_{x→a⁻} f(x) = lim_{x→a⁺} f(x)"
"""

from sympy import Symbol, limit, latex


def solve(
    expression,          # SymPy expression
    variable: Symbol,    # Symbol
    point,               # Value approached
) -> dict:
    """
    Show that a limit does not exist by computing one-sided limits
    and showing they disagree.
    """
    steps = []

    try:
        left = limit(expression, variable, point, "-")
        right = limit(expression, variable, point, "+")

        steps.append(
            f"Left limit: $\\lim_{{{latex(variable)} \\to {latex(point)}^-}} "
            f"{latex(expression)} = {latex(left)}$"
        )
        steps.append(
            f"Right limit: $\\lim_{{{latex(variable)} \\to {latex(point)}^+}} "
            f"{latex(expression)} = {latex(right)}$"
        )

        if left != right:
            steps.append(
                f"Since ${latex(left)} \\neq {latex(right)}$, "
                f"the limit does not exist."
            )
            return {
                "solved": True,
                "answer": "DNE",
                "answer_latex": "\\text{DNE}",
                "steps": steps,
                "method": "one_sided_disagreement",
                "left_limit": left,
                "right_limit": right,
            }
        else:
            # One-sided limits agree — limit actually exists!
            steps.append(
                f"Both one-sided limits equal ${latex(left)}$. "
                f"The limit exists and equals ${latex(left)}$."
            )
            return {
                "solved": True,
                "answer": left,
                "answer_latex": latex(left),
                "steps": steps,
                "method": "one_sided_agreement",
            }

    except Exception as e:
        return {
            "solved": False,
            "answer": None,
            "answer_latex": "",
            "steps": [f"One-sided limit computation failed: {e}"],
            "method": "failed",
        }
