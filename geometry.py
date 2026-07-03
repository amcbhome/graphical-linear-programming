"""
plotter.py

Visualises LPModel solution + geometry
"""

import numpy as np
import plotly.graph_objects as go


def build_plot(geometry, solution, model):

    fig = go.Figure()

    x_max, y_max = geometry["limits"]

    x_range = np.linspace(0, x_max, 300)

    # ---------------------------
    # constraints
    # ---------------------------

    for i, c in enumerate(model.constraints):

        if c.ay != 0:
            y = (c.rhs - c.ax * x_range) / c.ay
            fig.add_trace(go.Scatter(
                x=x_range,
                y=y,
                mode="lines",
                name=f"C{i+1}"
            ))

    # ---------------------------
    # feasible region
    # ---------------------------

    v = geometry["vertices"]

    if v:
        vx = [p[0] for p in v] + [v[0][0]]
        vy = [p[1] for p in v] + [v[0][1]]

        fig.add_trace(go.Scatter(
            x=vx,
            y=vy,
            fill="toself",
            fillcolor="rgba(0,150,255,0.25)",
            name="Feasible Region"
        ))

        fig.add_trace(go.Scatter(
            x=[p[0] for p in v],
            y=[p[1] for p in v],
            mode="markers",
            name="Vertices"
        ))

    # ---------------------------
    # optimum
    # ---------------------------

    fig.add_trace(go.Scatter(
        x=[solution["x"]],
        y=[solution["y"]],
        mode="markers+text",
        marker=dict(size=12, color="red"),
        text=["OPT"],
        name="Optimal"
    ))

    # ---------------------------
    # layout
    # ---------------------------

    fig.update_layout(
        title="X,Y Optimisation Model",
        template="simple_white",
        width=900,
        height=650
    )

    return fig
