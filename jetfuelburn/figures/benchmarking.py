# %%
from jetfuelburn import ureg
from jetfuelburn.statistics import myclimate
from jetfuelburn.reducedorder import seymour_etal
from importlib import resources
import plotly.graph_objects as go
import pandas as pd


def figure_benchmarking():
    """
    Creates a Plotly figure comparing (...)
    
    Returns:
        go.Figure: Plotly figure object with payload vs range plot
    """
    pass

range_points = list(range(0, 10001, 250))

results = []
for current_range in range_points:
    fuelburn = myclimate.calculate_fuel_consumption(
        acft='standard aircraft',
        x=current_range * ureg.km
    )
    # Assuming fuelburn is a pint Quantity, store its magnitude
    results.append({
        'range': current_range,
        'fuelburn': fuelburn.magnitude
    })
df_myclimate_standard = pd.DataFrame(results)

results = []
for current_range in range_points:
    fuelburn = seymour_etal.calculate_fuel_consumption(
        acft='A321',
        R=current_range * ureg.km
    )
    # Assuming fuelburn is a pint Quantity, store its magnitude
    results.append({
        'range': current_range,
        'fuelburn': fuelburn.magnitude
    })
df_seymour_a321 = pd.DataFrame(results)

results = []
for current_range in range_points:
    fuelburn = seymour_etal.calculate_fuel_consumption(
        acft='B722',
        R=current_range * ureg.km
    )
    # Assuming fuelburn is a pint Quantity, store its magnitude
    results.append({
        'range': current_range,
        'fuelburn': fuelburn.magnitude
    })
df_seymour_b727 = pd.DataFrame(results)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_myclimate_standard['range'],
    y=df_myclimate_standard['fuelburn'],
    mode='lines+markers',
    name='MyClimate "standard aircraft"',
    line=dict(color='blue', width=1),
    marker=dict(symbol='x', size=6)
))

fig.add_trace(go.Scatter(
    x=df_seymour_a321['range'],
    y=df_seymour_a321['fuelburn'],
    mode='lines+markers',
    name='Seymour et al. A321',
    line=dict(color='red', width=1),
    marker=dict(symbol='x', size=6)
))

fig.add_trace(go.Scatter(
    x=df_seymour_b727['range'],
    y=df_seymour_b727['fuelburn'],
    mode='lines+markers',
    name='Seymour et al. B727',
    line=dict(color='green', width=1),
    marker=dict(symbol='x', size=6)
))

fig.update_layout(
    xaxis_title='Range [km]',
    yaxis_title='Fuel Burn [kg]',
    font=dict(family='Arial', size=11),
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ),
    showlegend=True,
    xaxis=dict(
        showgrid=True,
        gridcolor='lightgrey',
        range=[0, 5000],  # Set x-axis limits
        minor=dict(
            showgrid=True,
            gridcolor='rgba(211, 211, 211, 0.5)', # Lighter grey for minor grid
            gridwidth=0.5
        )
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='lightgrey',
        range=[0, 35000], # Set y-axis limits (e.g., 0 to max value + 10%)
        minor=dict(
            showgrid=True,
            gridcolor='rgba(211, 211, 211, 0.5)', # Lighter grey for minor grid
            gridwidth=0.5
        )
    ),
    plot_bgcolor='white',
    width=600,
    height=400
)