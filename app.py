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
# PAGE CONFIG & ENHANCED CALCULATOR CSS
# ------------------------------------------------------------
st.set_page_config(page_title="X,Y Optimisation Calculator", layout="wide")

# CSS to fix contrast, enlarge text safely, and COMPACT layout to prevent scrolling
st.markdown("""
    <style>
    /* COMPACT STREAMLIT WHITESPACE */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* GLOBAL OVERRIDES */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f4f6f9 !important;
    }
    
    /* COMPACT HEADERS */
    h1 { font-size: 3rem !important; font-weight: 800 !important; color: #111827 !important; margin-bottom: 0 !important;}
    p.stCaption { font-size: 1.1rem !important; font-weight: 500 !important; color: #64748b !important; margin-bottom: 1rem !important; }
    h3 { font-size: 1.8rem !important; font-weight: 700 !important; color: #1f2937 !important; margin-top: 0.5rem !important;}

    /* FIX STANDARD LABELS & CAPTIONS FOR READABILITY */
    label[data-testid="stWidgetLabel"] p { font-size: 1rem !important; font-weight: 600 !important; color: #334155 !important; }
    div[data-testid="stCaptionContainer"] p { color: #475569 !important; font-size: 0.9rem !important; font-weight: 700 !important; }

    /* ENLARGE RADIO BUTTONS */
    div[data-testid="stRadio"] label p { font-size: 1.1rem !important; font-weight: 600 !important; color: #111827 !important; }

    /* STYLE AND ENLARGE ALL INPUT FIELDS SAFELY */
    div[data-baseweb="input"] input, div[data-baseweb="number-input"] input {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        padding: 0.5rem 0.5rem !important; 
        border-radius: 8px !important;
    }

    /* HIGHLY APPEALING GRADIENT CALCULATE BUTTON */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%) !important;
        height: 3.5em !important;
        border-radius: 10px !important;
        box-shadow: 0 6px 15px rgba(255, 75, 43, 0.3) !important;
        border: none !important;
        transition: all 0.3s ease 0s !important;
        margin-top: 0.5rem !important;
    }
    div.stButton > button:first-child p {
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        text-transform: uppercase;
        letter-spacing: 2px !important;
        margin: 0 !important;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 20px rgba(255, 75, 43, 0.5) !important;
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
        
        # Using integers (16000 instead of 16000.0) removes the decimals from the RHS inputs
        default_rhs = 16000 if i == 0 else 15000
        
        ax = r2.number_input("X Coeff", value=default_ax, key=f"ax_{i}", step=0.5, label_visibility="collapsed")
        ay = r3.number_input("Y Coeff", value=default_ay, key=f"ay_{i}", step=0.5, label_visibility="collapsed")
        rhs = r4.number_input("Limit", value=default_rhs, key=f"rhs_{i}", step=100, label_visibility="collapsed")
        
        constraints.append((c_label, ax, ay, rhs))

# Changed button text to be more appealing and instructional
solve_btn = st.button("✨ Calculate X and Y ✨", type="primary", use_container_width=True)

# ------------------------------------------------------------
# SOLVER & MASSIVE DIGITAL OUTPUT
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
        
        # HTML is un-indented and padding reduced to prevent scrolling
        # Objective value formatting updated to {opt_z:,.0f} to omit decimals
        lcd_html = f"""
<div style="background-color: #1a1c23; border: 8px solid #2e3440; border-radius: 12px; padding: 20px; text-align: center; box-shadow: inset 0px 0px 20px rgba(0,0,0,0.8); margin-top: 10px;">
    <p style="font-size: 1.2rem; color: #8892b0; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 3px; font-family: 'Segoe UI', sans-serif; font-weight: 600;">Calculated {obj_label}</p>
    <div style="font-size: 5.5rem; color: #10b981; margin: 0; font-family: 'Courier New', Courier, monospace; font-weight: 900; text-shadow: 0px 0px 15px rgba(16, 185, 129, 0.5); line-height: 1.1;">
        £{opt_z:,.0f}
    </div>
    <hr style="border-color: #3b4252; margin: 20px 0;">
    <p style="font-size: 1.8rem; color: #eceff4; margin: 0; font-weight: 400; font-family: 'Segoe UI', sans-serif;">
        <span style="color: #10b981; font-weight: bold;">{opt_x:,.2f}</span> {x_label} 
        <span style="color: #4c566a; margin: 0 20px;">|</span> 
        <span style="color: #10b981; font-weight: bold;">{opt_y:,.2f}</span> {y_label}
    </p>
</div>
"""
        st.markdown(lcd_html, unsafe_allow_html=True)
            
    else:
        st.error(f"Solver Status: {status}. Please check your constraints to ensure a feasible region exists.")
