import streamlit as st
import numpy as np
import plotly.graph_objects as go

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
# PAGE SETUP
# ------------------------------------------------------------

st.set_page_config(page_title="X,Y Optimisation Tool", layout="wide")
st.title("X,Y Optimisation Model")
st.caption("Single-file linear programming visualisation tool")

# ------------------------------------------------------------
# INPUTS
# ------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("Objective Function")
    cx = st.number_input("Coefficient of x", value=40.0)
    cy = st.number_input("Coefficient of y", value=30.0)
    maximise = st.radio("Type", ["Maximise", "Minimise"]) == "Maximise"

with col2:
    st.subheader("Constraints")

constraints = []

for i in range(4):
    c1, c2, c3, c4 = st.columns(4)

    ax = c1.number_input(f"x{i+1}", value=1.0, key=f"ax{i}")
    ay = c2.number_input(f"y{i+1}", value=1.0, key=f"ay{i}")
    rel = c3.selectbox(f"rel{i+1}", ["<=", ">=", "="], key=f"rel{i}")
    rhs = c4.number_input(f"rhs{i+1}", value=40.0, key=f"rhs{i}")

    constraints.append((ax, ay, rel, rhs))

# ------------------------------------------------------------
# SOLVER (PuLP)
# ------------------------------------------------------------

def solve_lp():
    sense = LpMaximize if maximise else LpMinimize
    model = LpProblem("XY_Model", sense)

    x = LpVariable("x", lowBound=0)
    y = LpVariable("y", lowBound=0)

    model += cx * x + cy * y

    for i, (ax, ay, rel, rhs) in enumerate(constraints):
        expr = ax * x + ay * y

        if rel == "<=":
            model += expr <= rhs
        elif rel == ">=":
            model += expr >= rhs
        else:
            model += expr == rhs

    model.solve(PULP_CBC_CMD(msg=False))

    return {
        "x": value(x),
        "y": value(y),
        "z": value(model.objective),
        "status": LpStatus[model.status],
    }


# ------------------------------------------------------------
# FEASIBLE REGION (GRID APPROXIMATION)
# ------------------------------------------------------------

def build_feasible_region(x_max=50, y_max=50):
    grid = np.linspace(0, x_max, 40)
    points = []

    for x in grid:
        for y in grid:
            ok = True

            for ax, ay, rel, rhs in constraints:
                val = ax * x + ay * y

                if rel == "<=" and val > rhs + 1e-6:
                    ok = False
                if rel == ">=" and val < rhs - 1e-6:
                    ok = False
                if rel == "=" and abs(val - rhs) > 1e-6:
                    ok = False

            if ok:
                points.append((x, y))

    if len(points) < 3:
        return [], (x_max, y_max)

    pts = np.array(points)

    x_max = max(pts[:, 0]) * 1.1
    y_max = max(pts[:, 1]) * 1.1

    return pts, (x_max, y_max)


# ------------------------------------------------------------
# PLOTTER
# ------------------------------------------------------------

def plot_graph(solution, region, limits):
    fig = go.Figure()

    x_max, y_max = limits
    x_range = np.linspace(0, x_max, 300)

    # constraints
    for i, (ax, ay, rel, rhs) in enumerate(constraints):

        if ay != 0:
            y = (rhs - ax * x_range) / ay
            fig.add_trace(go.Scatter(x=x_range, y=y, mode="lines", name=f"C{i+1}"))

    # feasible region
    if len(region) > 0:
        vx, vy = region[:, 0], region[:, 1]

        fig.add_trace(go.Scatter(
            x=vx,
            y=vy,
            mode="markers",
            marker=dict(size=3),
            name="Feasible Region"
        ))

    # optimum
    fig.add_trace(go.Scatter(
        x=[solution["x"]],
        y=[solution["y"]],
        mode="markers+text",
        marker=dict(size=12, color="red"),
        text=["OPT"],
        name="Optimal"
    ))

    fig.update_layout(
        title="Feasible Region & Optimal Solution",
        template="simple_white",
        width=900,
        height=650
    )

    fig.update_xaxes(range=[0, x_max])
    fig.update_yaxes(range=[0, y_max])

    return fig


# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------

if st.button("Solve Model"):

    sol = solve_lp()
    region, limits = build_feasible_region()
    fig = plot_graph(sol, region, limits)

    st.subheader("Algebraic Model")

    st.code(f"""
Max Z = {cx}x + {cy}y

Subject to:
""" + "\n".join(
        [f"{a}x + {b}y {r} {rhs}" for a, b, r, rhs in constraints]
    ))

    colA, colB = st.columns(2)

    with colA:
        st.write(sol)

    with colB:
        st.plotly_chart(fig, use_container_width=True)
