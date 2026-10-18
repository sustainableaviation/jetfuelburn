"""Figures for the documentation of the aerodynamics module."""

import plotly.graph_objects as go
from jetfuelburn import ureg

from jetfuelburn.utility.aerodynamics import poll_schumann_drag_polars
from jetfuelburn.utility.physics import (
    _calculate_dynamic_pressure,
    _calculate_airspeed_from_mach,
)


def figure_poll_schumann_dragpolar() -> go.Figure:
    """
    Creates a Plotly figure of the lift-to-drag ratio over the drag coefficient
    of an A320 at 58,800 kg for five Mach numbers, using the Poll & Schumann (2025) drag polar.
    Along each curve, the altitude varies from FL250 to FL430, which varies the lift coefficient.

    This is the case of Fig. 3 in Poll & Schumann (2025).

    Returns:
        go.Figure: Plotly figure object with L/D vs CD plot
    """
    acft = "A320"
    lift = 58800 * ureg.kg * ureg.gravity
    S = poll_schumann_drag_polars.get_basic_drag_parameters(acft)["S"]

    fig = go.Figure()

    for mach in [0.65, 0.70, 0.75, 0.80, 0.82]:
        cd_values = []
        ld_values = []
        for flight_level in range(250, 431, 5):
            altitude = flight_level * 100 * ureg.ft
            q = _calculate_dynamic_pressure(
                speed=_calculate_airspeed_from_mach(mach, altitude), altitude=altitude
            )
            drag = poll_schumann_drag_polars.calculate_drag(acft, lift, mach, altitude)
            cd_values.append((drag / (q * S)).to("dimensionless").magnitude)
            ld_values.append((lift / drag).to("dimensionless").magnitude)

        fig.add_trace(
            go.Scatter(
                x=cd_values,
                y=ld_values,
                mode="lines",
                name=f"M = {mach:.2f}",
                line=dict(width=2),
                hovertemplate=(
                    f"<b>M = {mach:.2f}</b><br>"
                    + "CD: %{x:.4f}<br>"
                    + "L/D: %{y:.2f}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        xaxis_title="Drag Coefficient (C<sub>D</sub>)",
        yaxis_title="Lift-to-Drag Ratio (L/D)",
        font=dict(family="Arial", size=11),
        legend=dict(
            yanchor="bottom",
            y=0.05,
            xanchor="right",
            x=0.95,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="LightGrey",
            borderwidth=1,
        ),
        showlegend=True,
        xaxis=dict(showgrid=True, gridcolor="lightgrey"),
        yaxis=dict(showgrid=True, gridcolor="lightgrey"),
        plot_bgcolor="white",
        autosize=True,
        height=400,
    )

    return fig


# Deprecated aliases of figures replaced in jetfuelburn 4.0.0 (to be removed in 5.0.0).
from jetfuelburn.utility.code import _deprecated_module_attribute

_DEPRECATED = {
    "figure_openap_dragpolar": (
        "figure_poll_schumann_dragpolar",
        figure_poll_schumann_dragpolar,
    ),
    "figure_jsbsim_dragpolar_mach_effects": (
        "figure_poll_schumann_dragpolar",
        figure_poll_schumann_dragpolar,
    ),
}


def __getattr__(name):
    return _deprecated_module_attribute(__name__, name, _DEPRECATED)
