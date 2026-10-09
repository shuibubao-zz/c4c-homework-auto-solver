"""
Solver Template: Direct Limit Computation
T-box concept: limit_definition
Tool: SymPy

This is a parameterized solver. The runtime binds problem-specific
variables (expression, variable, point, direction) from the A-box,
then executes this template.

Oracle source: Stewart Ch. 2 — direct evaluation and algebraic
simplification are the primary methods for computing limits.
"""

from sympy import Symbol, limit, oo, simplify, latex, Abs, Piecewise
from typing import Optional


def solve(
    expression,          # SymPy expression (already parsed)
    variable: Symbol,    # Symbol to take limit of
    point,               # Value approached (SymPy number/expression/oo)
    direction: Optional[str] = None,  # None, '+', or '-'
) -> dict:
    """
    Compute lim_{variable → point} expression.

    Returns:
        {
            "solved": bool,
            "answer": sympy expression,
            "answer_latex": str,
            "steps": list[str],
            "method": "direct" | "simplify" | "lhopital"
        }
    """
    steps = []

    # Step 1: Attempt direct computation
    try:
        if direction:
            result = limit(expression, variable, point, direction)
            dir_str = f"^{direction}"
        else:
            result = limit(expression, variable, point)
            dir_str = ""

        steps.append(
            f"$\\lim_{{{latex(variable)} \\to {latex(point)}{dir_str}}} "
            f"{latex(expression)} = {latex(result)}$"
        )

        return {
            "solved": True,
            "answer": result,
            "answer_latex": latex(result),
            "steps": steps,
            "method": "direct",
        }

    except Exception as e:
        return {
            "solved": False,
            "answer": None,
            "answer_latex": "",
            "steps": [f"SymPy limit computation failed: {e}"],
            "method": "failed",
        }
