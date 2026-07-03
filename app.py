import streamlit as st
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
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="X,Y Optimisation Calculator", layout="wide")
st.title("🧮 X, Y Optimisation Calculator")
st.caption("A streamlined linear programming solver using PuLP")

# ------------------------------------------------------------
# COMPACT UI LAYOUT
# ------------------------------------------------------------
col_obj, col_cons = st.columns(2, gap="large")

with col_obj:
    st.subheader("1. Objective Function")
    
    # Goal and Objective Name
    c1, c2 = st.columns([1, 2])
    opt_type = c1.radio("Goal", ["Maximise", "Minimise"], label_visibility="collapsed")
    maximise = opt_type == "Maximise"
    obj_label = c2.text_input("Objective Label", value="Profit")
    
    # Decision Variables and Coefficients
    c3, c4 = st.columns(2)
    x_label = c3.text_input("Variable 1 Label", value="Product A")
    cx = c3.number_input(f"{x_label} Coefficient", value=30.0, step=1.0)
    
    y_label = c4.text_input("Variable 2 Label", value="Product B")
    cy = c4.number_input(f"{y_label} Coefficient", value=40.0, step=1.0)

with col_cons:
    st.subheader("2. Constraints")
    
    # Column headers for visual alignment
    h1, h2, h3, h4 = st.columns([1.5, 1, 1, 1])
    h1.caption("Constraint Name")
    h2.caption(f"{x_label} Coeff")
    h3.caption(f"{y_label} Coeff")
    h4.caption("Limit (≤)")
    
    constraints = []
    
    # Compact constraint rows
    for i in range(2):
        r1, r2, r3, r4 = st.columns([1.5, 1, 1, 1])
        c_label = r1.text_input("Name", value="Labour" if i == 0 else "Material", key=f"l_{i}", label_visibility="collapsed")
        ax = r2.number_input("X Coeff", value=1.0, key=f"ax_{i}", step=0.5, label_visibility="collapsed")
        ay = r3.number_input("Y Coeff", value=1.0, key=f"ay_{i}", step=0.5, label_visibility="collapsed")
        rhs = r4.number_input("Limit", value=100.0, key=f"rhs_{i}", step=10.0, label_visibility="collapsed")
        
        constraints.append((c_label, ax, ay, rhs))

st.write("") 
solve_btn = st.button("Calculate Optimum", type="primary", use_container_width=True)
st.divider()

# ------------------------------------------------------------
# SOLVER & OUTPUT
# ------------------------------------------------------------
if solve_btn:
    sense = LpMaximize if maximise else LpMinimize
    model = LpProblem("XY_Model", sense)

    x = LpVariable("x", lowBound=0)
    y = LpVariable("y", lowBound=0)

    model += cx * x + cy * y

    for label, ax, ay, rhs in constraints:
        model += ax * x + ay * y <= rhs, label

    model.solve(PULP_CBC_CMD(msg=False))
    status = LpStatus[model.status]

    if status == "Optimal":
        # Extract values
        opt_x = value(x) if value(x) is not None else 0.0
        opt_y = value(y) if value(y) is not None else 0.0
        opt_z = value(model.objective) if value(model.objective) is not None else 0.0
        
        # Clean, single-line output
        st.success(f"**Decision Variables:** {opt_x:,.2f} {x_label}, {opt_y:,.2f} {y_label} results in **£{opt_z:,.2f}** {obj_label.lower()}")
            
    else:
        st.error(f"Solver Status: {status}. Please check your constraints to ensure a feasible region exists.")
else:
    st.info("👈 Configure your variables, objective function, and constraints, then click **Calculate Optimum**.")
