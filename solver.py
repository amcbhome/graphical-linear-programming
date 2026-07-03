"""
solver.py

X,Y Optimisation Model
Core Linear Programming Engine

Responsibilities:
- Build LP model (2 variables only: x, y)
- Solve using PuLP
- Return structured result for UI + plotting
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


# ------------------------------------------------------------
# MAIN SOLVER
# ------------------------------------------------------------

def solve_model(objective, constraints, maximise=True):
    """
    Solve a 2-variable linear programming model.

    Parameters
    ----------
    objective : tuple
        (cx, cy)

    constraints : list of tuples
        (ax, ay, relation, rhs)

        relation ∈ {"<=", ">=", "="}

    maximise : bool
        True = maximise Z
        False = minimise Z

    Returns
    -------
    dict
        Full solution package for UI + plotting
    """

    # --------------------------------------------------------
    # 1. CREATE LP MODEL
    # --------------------------------------------------------

    sense = LpMaximize if maximise else LpMinimize

    model = LpProblem("XY_Optimisation_Model", sense)

    # Decision variables (always non-negative)
    x = LpVariable("x", lowBound=0)
    y = LpVariable("y", lowBound=0)

    cx, cy = objective

    # Objective function
    model += cx * x + cy * y

    # --------------------------------------------------------
    # 2. ADD CONSTRAINTS
    # --------------------------------------------------------

    for i, (ax, ay, relation, rhs) in enumerate(constraints):

        expr = ax * x + ay * y

        if relation == "<=":
            model += expr <= rhs, f"C{i+1}"

        elif relation == ">=":
            model += expr >= rhs, f"C{i+1}"

        elif relation == "=":
            model += expr == rhs, f"C{i+1}"

        else:
            raise ValueError(f"Invalid relation: {relation}")

    # --------------------------------------------------------
    # 3. SOLVE MODEL
    # --------------------------------------------------------

    model.solve(PULP_CBC_CMD(msg=False))

    status = LpStatus[model.status]

    x_val = value(x)
    y_val = value(y)
    z_val = value(model.objective)

    # --------------------------------------------------------
    # 4. IDENTIFY ACTIVE CONSTRAINTS
    # --------------------------------------------------------

    active_constraints = []

    for i, constraint in enumerate(model.constraints.values()):

        lhs_value = constraint.value()
        rhs_value = constraint.constant

        # tolerance for floating point
        if abs(lhs_value - rhs_value) < 1e-5:
            active_constraints.append(f"C{i+1}")

    # --------------------------------------------------------
    # 5. RETURN STRUCTURED RESULT
    # --------------------------------------------------------

    result = {
        "status": status,

        "x": x_val,
        "y": y_val,

        "objective_value": z_val,

        "objective": {
            "cx": cx,
            "cy": cy,
            "maximise": maximise,
        },

        "constraints": constraints,

        "active_constraints": active_constraints,
    }

    return result
