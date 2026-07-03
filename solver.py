"""
solver.py

Solves LPModel using PuLP
"""

from pulp import (
    LpProblem,
    LpVariable,
    LpMaximize,
    LpMinimize,
    LpStatus,
    value,
    PULP_CBC_CMD,
)


def solve(model):
    sense = LpMaximize if model.maximise else LpMinimize

    lp = LpProblem("XY_Model", sense)

    x = LpVariable("x", lowBound=0)
    y = LpVariable("y", lowBound=0)

    cx, cy = model.objective

    lp += cx * x + cy * y

    for i, c in enumerate(model.constraints):
        expr = c.ax * x + c.ay * y

        if c.relation == "<=":
            lp += expr <= c.rhs, f"C{i+1}"
        elif c.relation == ">=":
            lp += expr >= c.rhs, f"C{i+1}"
        elif c.relation == "=":
            lp += expr == c.rhs, f"C{i+1}"

    lp.solve(PULP_CBC_CMD(msg=False))

    return {
        "status": LpStatus[lp.status],
        "x": value(x),
        "y": value(y),
        "objective_value": value(lp.objective),
        "objective": model.objective,
        "constraints": model.constraints,
    }
