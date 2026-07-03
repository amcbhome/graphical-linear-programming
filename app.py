"""
app.py

X,Y Optimisation Model
Single-screen Streamlit application

Focus:
- Algebraic formulation
- Graphical feasible region
- Optimal solution interpretation
"""

import streamlit as st

from solver import solve_model
from plotter import build_plot


# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------

st.set_page_config(
    page_title="X,Y Optimisation Model",
    layout="wide"
)

st.title("X,Y Optimisation Model")
st.caption("An educational graphical linear programming tool (2 variables only)")


# ------------------------------------------------------------
# SESSION STATE (DEFAULT MODEL)
# ------------------------------------------------------------

if "constraints" not in st.session_state:
    st.session_state.constraints = [
        [1, 1, "<=", 40],
        [2, 1, "<=", 60],
        [1, 0, "<=", 30],
        [0, 1, "<=", 20],
    ]


# ------------------------------------------------------------
# LAYOUT: TWO PANELS
# ------------------------------------------------------------

left, right = st.columns([1, 2])


# ============================================================
# LEFT PANEL: MODEL INPUT + ALGEBRA
# ============================================================

with left:

    st.subheader("Build the Model")

    # -------------------------
    # Objective
    # -------------------------

    st.markdown("### Objective Function")

    maximise = st.radio(
        "Type",
        ["Maximise", "Minimise"]
    )

    cx = st.number_input("Coefficient of x", value=40)
    cy = st.number_input("Coefficient of y", value=30)

    # -------------------------
    # Constraints
    # -------------------------

    st.markdown("### Constraints")

    constraints = []

    for i, c in enumerate(st.session_state.constraints):

        st.markdown(f"**Constraint {i+1}**")

        col1, col2, col3, col4 = st.columns(4)

        ax = col1.number_input(
            "x",
            value=float(c[0]),
            key=f"ax_{i}"
        )

        ay = col2.number_input(
            "y",
            value=float(c[1]),
            key=f"ay_{i}"
        )

        rel = col3.selectbox(
            "Rel",
            ["<=", ">=", "="],
            index=["<=", ">=", "="].index(c[2]),
            key=f"rel_{i}"
        )

        rhs = col4.number_input(
            "RHS",
            value=float(c[3]),
            key=f"rhs_{i}"
        )

        constraints.append([ax, ay, rel, rhs])

    st.session_state.constraints = constraints

    # -------------------------
    # Solve button
    # -------------------------

    st.markdown("---")

    solve = st.button("Build & Solve Model", type="primary")


# ============================================================
# RIGHT PANEL: GRAPH
# ============================================================

with right:

    st.subheader("Graphical Solution")

    fig_placeholder = st.empty()


# ============================================================
# BOTTOM: ALGEBRAIC MODEL + RESULTS
# ============================================================

st.markdown("---")

model_col, result_col = st.columns(2)


# ------------------------------------------------------------
# RUN MODEL
# ------------------------------------------------------------

if solve:

    objective = (cx, cy)

    maximise_flag = maximise == "Maximise"

    result = solve_model(
        objective=objective,
        constraints=constraints,
        maximise=maximise_flag
    )

    # --------------------------------------------------------
    # ALGEBRAIC MODEL
    # --------------------------------------------------------

    with model_col:

        st.subheader("Algebraic Model")

        st.code(
            f"""
{maximise} Z = {cx}x + {cy}y

Subject to

""" +
"\n".join(
    [f"{a}x + {b}y {r} {rhs}" for a, b, r, rhs in constraints]
) +
"""

x ≥ 0
y ≥ 0
""",
            language="text"
        )

    # --------------------------------------------------------
    # PLOT
    # --------------------------------------------------------

    geometry_placeholder = {
        "vertices": [],  # geometry.py would normally supply this
        "limits": (50, 50),
    }

    fig = build_plot(
        geometry=geometry_placeholder,
        solution=result,
        constraints=constraints
    )

    fig_placeholder.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    with result_col:

        st.subheader("Optimal Solution")

        st.markdown(f"**x = {result['x']:.2f}**")
        st.markdown(f"**y = {result['y']:.2f}**")
        st.markdown(f"**Z = {result['objective_value']:.2f}**")

        st.markdown("---")

        st.subheader("Active Constraints")

        if result["active_constraints"]:
            for c in result["active_constraints"]:
                st.write(c)
        else:
            st.write("None identified")

else:

    with model_col:
        st.info("Click 'Build & Solve Model' to generate algebraic and graphical solution.")
