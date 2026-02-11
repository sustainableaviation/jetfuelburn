# %%
import plotly.graph_objects as go
from jetfuelburn import ureg

from jetfuelburn.utility.aerodynamics import openap_drag_polars, jsbsim_drag_polars


def figure_openap_dragpolar():
    """
    Creates a Plotly figure comparing the drag polars for A320 and B738
    aircraft using the OpenAP model parameters.

    The plot visualizes the parabolic relationship: CD = CD0 + K * CL^2

    Returns:
        go.Figure: Plotly figure object with CL vs CD plot
    """
    aircraft_targets = ["A320", "B738"]
    colors = {"A320": "blue", "B738": "red"}

    # Generate CL range from 0.0 to 1.5 without NumPy
    # Steps of 0.05: 0, 0.05, 0.10, ... 1.50
    cl_values = [i * 0.05 for i in range(31)]

    fig = go.Figure()

    for acft in aircraft_targets:
        # Retrieve aerodynamic parameters
        # Returns dict with 'CD0' (float), 'K' (float), and 'S' (pint.Quantity)
        params = openap_drag_polars.get_basic_drag_parameters(acft)

        cd0 = params["CD0"]
        k = params["K"]

        # Calculate Drag Coefficient (CD)
        # Polar Equation: CD = CD0 + K * CL^2
        cd_values = [cd0 + k * (cl**2) for cl in cl_values]

        fig.add_trace(
            go.Scatter(
                x=cd_values,
                y=cl_values,
                mode="lines",
                name=f"{acft} (OpenAP)",
                line=dict(color=colors[acft], width=2),
                hovertemplate=(
                    f"<b>{acft}</b><br>"
                    + "CL: %{y:.2f}<br>"
                    + "CD: %{x:.4f}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        xaxis_title="Drag Coefficient (C<sub>D</sub>)",
        yaxis_title="Lift Coefficient (CL)",
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
        xaxis=dict(
            showgrid=True, gridcolor="lightgrey", zeroline=True, zerolinecolor="grey"
        ),
        yaxis=dict(
            showgrid=True, gridcolor="lightgrey", zeroline=True, zerolinecolor="grey"
        ),
        plot_bgcolor="white",
        width=600,
        height=400,
    )

    return fig


def figure_jsbsim_dragpolar_mach_effects():
    """
    Creates a Plotly figure showing the effect of Mach number on the drag polar
    using the JSBSim component-based model.

    The plot demonstrates how Drag Coefficient (CD) increases for the same
    Lift Coefficient (CL) as Mach number rises (wave drag).

    Returns:
        go.Figure: Plotly figure object with CL vs CD curves for various Mach numbers
    """
    acft = "B788"

    # Define conditions
    # We use a fixed altitude to calculate a reference dynamic pressure (q)
    altitude = 30000 * ureg.foot
    mach_values = [0.4, 0.6, 0.7, 0.76, 0.78, 0.80, 0.82]

    # Helper to estimate air density at altitude (Standard Atmosphere)
    # to calculate valid Lift forces for the model inputs.
    # rho_0 = 1.225 kg/m^3
    # at 30k ft (~9144m), sigma ~ 0.37
    rho = 0.458 * ureg("kg/m^3")  # Approx density at 30k ft

    # Retrieve Wing Area (S) to calculate Lift Force (L) inputs
    # We access the private dictionary because we need S to sweep CL correctly
    if acft not in jsbsim_drag_polars._aircraft_data:
        raise ValueError(f"Aircraft {acft} not found")

    acft_data = jsbsim_drag_polars._aircraft_data[acft]
    S = acft_data["wing_area_sqft"] * ureg.square_feet

    # Generate Target CL range
    # 0.0 to 1.3 in steps of 0.05
    target_cls = [x * 0.05 for x in range(27)]

    fig = go.Figure()

    # Color scale for Mach numbers
    colors = [
        "#ffeebb",
        "#ffcc88",
        "#ffaa66",
        "#ff8844",
        "#ff6622",
        "#ff4400",
        "#cc0000",
    ]

    for i, mach in enumerate(mach_values):

        # 1. Calculate Dynamic Pressure (q) for this Mach
        # Speed of Sound (a) at 30k ft is approx 303 m/s
        a = 303 * ureg("m/s")
        v = mach * a
        q = 0.5 * rho * v**2

        cd_results = []
        cl_results = []

        for cl in target_cls:
            if cl == 0:
                # Avoid division by zero issues or zero lift logic if specific models dislike it,
                # though typical polars start at CD0.
                # We'll calculate a very small lift or handle 0 specifically.
                # Let's use a tiny epsilon for L to get CD0
                L_input = 1 * ureg.newton
            else:
                # Calculate required Lift Force L to achieve this CL
                L_input = cl * q * S

            try:
                # 2. Call the provided function
                drag_force = jsbsim_drag_polars.calculate_drag(
                    acft=acft, L=L_input, M=mach, h=altitude
                )

                # 3. Convert back to Coefficients for plotting
                # CD = Drag / (q * S)
                # CL = Lift / (q * S)

                # We recalculate actual CL from input to ensure alignment
                actual_cl = (L_input / (q * S)).to("dimensionless").magnitude
                actual_cd = (drag_force / (q * S)).to("dimensionless").magnitude

                cl_results.append(actual_cl)
                cd_results.append(actual_cd)

            except ValueError:
                # Handle cases where interpolation might fail out of bounds
                continue

        # Add trace for this Mach number
        fig.add_trace(
            go.Scatter(
                x=cd_results,
                y=cl_results,
                mode="lines",
                name=f"M {mach}",
                line=dict(color=colors[i % len(colors)], width=2),
                hovertemplate=(
                    f"<b>Mach {mach}</b><br>"
                    + "C<sub>L</sub>: %{y:.2f}<br>"
                    + "C<sub>D</sub>: %{x:.4f}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        xaxis_title="Drag Coefficient (C<sub>D</sub>)",
        yaxis_title="Lift Coefficient (C<sub>L</sub>)",
        font=dict(family="Arial", size=11),
        legend=dict(
            title="Mach Number",
            yanchor="bottom",
            y=0.05,
            xanchor="right",
            x=0.95,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="LightGrey",
            borderwidth=1,
        ),
        showlegend=True,
        xaxis=dict(
            showgrid=True,
            gridcolor="lightgrey",
            zeroline=True,
            zerolinecolor="grey",
            range=[0, 0.1],  # Focus on the drag bucket area
        ),
        yaxis=dict(
            showgrid=True, gridcolor="lightgrey", zeroline=True, zerolinecolor="grey"
        ),
        plot_bgcolor="white",
        width=600,
        height=400,
    )

    return fig
