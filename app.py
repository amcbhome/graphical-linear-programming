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
# PAGE CONFIG & CALCULATOR CSS
# ------------------------------------------------------------
st.set_page_config(page_title="X,Y Optimisation Calculator", layout="wide")

# CSS to mimic the classic dark-mode calculator theme and compact the layout
st.markdown("""
    <style>
    /* COMPACT STREAMLIT WHITESPACE */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* GLOBAL OVERRIDES - Dark Theme Background */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #22242c !important; 
    }
    
    /* TEXT COLORS FOR DARK THEME */
    h1, h3 { color: #f0f0f0 !important; margin-bottom: 0 !important; margin-top: 0.5rem !important;}
    p.stCaption { color: #8a8d9e !important; font-size: 1.1rem !important; margin-bottom: 1rem !important; }
    label[data-testid="stWidgetLabel"] p { color: #b0b3c5 !important; font-size: 1rem !important; font-weight: 600 !important; }
    div[data-testid="stCaptionContainer"] p { color: #8a8d9e !important; font-size: 0.9rem !important; font-weight: 700 !important; }

    /* RADIO BUTTONS */
    div[data-testid="stRadio"] label p { color: #f0f0f0 !important; font-size: 1.1rem !important; font-weight: 600 !important;}

    /* INPUT FIELDS - Styled like the dark grey keys */
    div[data-baseweb="input"] input, div[data-baseweb="number-input"] input {
        background-color: #3b3e4e !important;
        color: #ffffff !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        padding: 0.5rem 0.5rem !important; 
        border-radius: 12px !important;
        border: 1px solid #2e313e !important;
    }

    /* THE CALCULATE BUTTON - Styled like the orange operator keys */
    div.stButton > button:first-child {
        background-color: #f49020 !important;
        color: #ffffff !important;
        height: 3.5em !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(244, 144, 32, 0.3) !important;
        transition: all 0.3s ease 0s !important;
        margin-top: 0.5rem !important;
    }
    div.stButton > button:first-child p {
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 2px !important;
        margin: 0 !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #ff9d33 !important;
        transform: translateY(-2px) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# LOGO AND TITLE 
# ------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/plasticine/200/calculator.png", width=120)
    st.divider()

st.title("🧮 X, Y Optimisation Calculator")
st.caption("A streamlined linear programming solver using PuLP")

# ------------------------------------------------------------
# COMPACT UI LAYOUT
# ------------------------------------------------------------
col_obj, col_cons = st.columns(2, gap="large")

with col_obj:
    st.subheader("1. Objective Function")
    
    c1, c2 = st.columns([1, 2])
    opt_type = c1.radio("Goal", ["Maximise", "Minimise"], label_visibility="collapsed")
    maximise = opt_type == "Maximise"
    
    obj_label = c2.text_input("Objective Label", value="Profit", placeholder="Enter objective label...", label_visibility="collapsed")
    
    c3, c4 = st.columns(2)
    x_label = c3.text_input("Variable 1", value="Product A", placeholder="Enter Var 1 label...", label_visibility="collapsed")
    cx = c3.number_input(f"{x_label if x_label else 'Var 1'} Coefficient", value=30.0, step=1.0)
    
    y_label = c4.text_input("Variable 2", value="Product B", placeholder="Enter Var 2 label...", label_visibility="collapsed")
    cy = c4.number_input(f"{y_label if y_label else 'Var 2'} Coefficient", value=40.0, step=1.0)

with col_cons:
    st.subheader("2. Constraints")
    
    h1, h2, h3, h4 = st.columns([1.5, 1, 1, 1])
    h1.caption("Constraint Name")
    h2.caption(f"{x_label if x_label else 'Var 1'} Coeff")
    h3.caption(f"{y_label if y_label else 'Var 2'} Coeff")
    h4.caption("Limit (≤)")
    
    constraints = []
    
    for i in range(2):
        r1, r2, r3, r4 = st.columns([1.5, 1, 1, 1])
        c_label = r1.text_input("Name", value="Labour" if i == 0 else "Material", placeholder="Constraint name...", key=f"l_{i}", label_visibility="collapsed")
        
        default_ax = 4.0 if i == 0 else 3.0
        default_ay = 4.0 if i == 0 else 5.0
        # Whole numbers keep the RHS clean
        default_rhs = 16000 if i == 0 else 15000 
        
        ax = r2.number_input("X Coeff", value=default_ax, key=f"ax_{i}", step=0.5, label_visibility="collapsed")
        ay = r3.number_input("Y Coeff", value=default_ay, key=f"ay_{i}", step=0.5, label_visibility="collapsed")
        rhs = r4.number_input("Limit", value=default_rhs, key=f"rhs_{i}", step=100, label_visibility="collapsed")
        
        constraints.append((c_label, ax, ay, rhs))

solve_btn = st.button("Calculate X and Y", type="primary", use_container_width=True)

# ------------------------------------------------------------
# SOLVER & DIGITAL LCD OUTPUT
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
        opt_x = value(x) if value(x) is not None else 0.0
        opt_y = value(y) if value(y) is not None else 0.0
        opt_z = value(model.objective) if value(model.objective) is not None else 0.0
        
        # HTML un-indented so Markdown doesn't parse it as a code block
        lcd_html = f"""
<div style="background-color: #3a4372; border-radius: 15px; padding: 20px; text-align: center; box-shadow: inset 0px 4px 10px rgba(0,0,0,0.3); margin-top: 10px;">
    <p style="font-size: 1.2rem; color: #a4adcf; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 3px; font-weight: 600;">Calculated {obj_label}</p>
    <div style="font-size: 5.5rem; color: #ffffff; margin: 0; font-family: 'Courier New', Courier, monospace; font-weight: 900; line-height: 1.1;">
        £{opt_z:,.0f}
    </div>
    <hr style="border-color: #555f94; margin: 20px 0;">
    <p style="font-size: 1.8rem; color: #e0e4f5; margin: 0; font-weight: 400;">
        <span style="font-weight: bold;">{opt_x:,.2f}</span> {x_label} 
        <span style="color: #8a94c4; margin: 0 20px;">|</span> 
        <span style="font-weight: bold;">{opt_y:,.2f}</span> {y_label}
    </p>
</div>
"""
        st.markdown(lcd_html, unsafe_allow_html=True)
            
    else:
        st.error(f"Solver Status: {status}. Please check your constraints to ensure a feasible region exists.")
