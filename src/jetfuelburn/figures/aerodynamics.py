# %%
import plotly.graph_objects as go

from jetfuelburn.utility.aerodynamics import openap_drag_polars

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
        
        cd0 = params['CD0']
        k = params['K']
        
        # Calculate Drag Coefficient (CD)
        # Polar Equation: CD = CD0 + K * CL^2
        cd_values = [cd0 + k * (cl ** 2) for cl in cl_values]
        
        fig.add_trace(go.Scatter(
            x=cd_values,
            y=cl_values,
            mode='lines',
            name=f'{acft} (OpenAP)',
            line=dict(color=colors[acft], width=2),
            hovertemplate=(
                f"<b>{acft}</b><br>" +
                "CL: %{y:.2f}<br>" +
                "CD: %{x:.4f}<extra></extra>"
            )
        ))

    fig.update_layout(
        title='Drag Polar Comparison (OpenAP Model)',
        xaxis_title='Drag Coefficient (C<sub>D</sub>)',
        yaxis_title='Lift Coefficient (CL)',
        font=dict(family='Arial', size=11),
        legend=dict(
            yanchor="bottom",
            y=0.05,
            xanchor="right",
            x=0.95,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="LightGrey",
            borderwidth=1
        ),
        showlegend=True,
        xaxis=dict(
            showgrid=True, 
            gridcolor='lightgrey',
            zeroline=True,
            zerolinecolor='grey'
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='lightgrey',
            zeroline=True,
            zerolinecolor='grey'
        ),
        plot_bgcolor='white',
        width=600,
        height=400
    )

    return fig