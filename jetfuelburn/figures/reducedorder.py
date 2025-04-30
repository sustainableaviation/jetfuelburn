from jetfuelburn import ureg
from jetfuelburn.reducedorder import lee_etal
from importlib import resources
import plotly.graph_objects as go
import pandas as pd


def figure_lee2010():
    """
    Creates a Plotly figure comparing my implementation of Lee et al. (2010) with the original data
    from the paper. The figure shows the payload vs range for a B732 aircraft.

    References
    ----------
    Lee, H. T., & Chatterji, G. (2010, September).
    Closed-form takeoff weight estimation model for air transportation simulation.
    In _10th AIAA Aviation Technology, Integration, and Operations (ATIO) Conference_ (p. 9156).
    doi:[10.2514/6.2010-9156](https://doi.org/10.2514/6.2010-9156) (Figure 6, data `f_res=0.08`)
    
    Returns:
        go.Figure: Plotly figure object with payload vs range plot
    """
    with resources.open_text("jetfuelburn.data.Lee2010", "data_fig_6_fres_const.csv") as file:
        df_fres_const = pd.read_csv(
            filepath_or_buffer=file,
            header=0,
            index_col=None
        )

    input_data = {
        'acft': 'B732',
        'W_E': 265825 * ureg.N,
        'W_MPLD': 156476 * ureg.N,
        'W_MTO': 513422 * ureg.N,
        'W_MF': 142365 * ureg.N,
        'S': 91.09 * ureg.m ** 2,
        'C_D0': 0.0214,
        'C_D2': 0.0462,
        'c': (2.131E-4) / ureg.s,
        'h': 9144 * ureg.m,
        'V': 807.65 * ureg.kph,
    }

    results = []
    for range in df_fres_const['range']:
        dict_results = lee_etal.calculate_fuel_consumption(
            acft=input_data['acft'],
            W_E=input_data['W_E'],
            W_MPLD=input_data['W_MPLD'],
            W_MTO=input_data['W_MTO'],
            W_MF=input_data['W_MF'],
            S=input_data['S'],
            C_D0=input_data['C_D0'],
            C_D2=input_data['C_D2'],
            c=input_data['c'],
            h=input_data['h'],
            V=input_data['V'],
            d=range * ureg.nmi
        )
        results.append({
            'range': range,
            'payload': dict_results['mass_payload'].to('lbs').magnitude
        })

    df_results = pd.DataFrame(results)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_fres_const['range'],
        y=df_fres_const['payload'],
        mode='lines+markers',
        name='Fig. 6 in Lee et al. (f_res=0.08)',
        line=dict(color='red', width=1),
        marker=dict(symbol='circle', size=6)
    ))

    fig.add_trace(go.Scatter(
        x=df_results['range'],
        y=df_results['payload'],
        mode='lines+markers',
        name='My Implementation (f_res=0.08)',
        line=dict(color='black', width=1),
        marker=dict(symbol='x', size=6)
    ))

    fig.update_layout(
        title='Payload vs Range',
        xaxis_title='Range [nmi]',
        yaxis_title='Payload [lbs]',
        font=dict(family='Arial', size=11),
        legend=dict(
            yanchor="bottom",
            y=0.01,
            xanchor="left",
            x=0.01
        ),
        showlegend=True,
        xaxis=dict(showgrid=True, gridcolor='lightgrey'),
        yaxis=dict(showgrid=True, gridcolor='lightgrey'),
        plot_bgcolor='white',
        width=600,
        height=400
    )

    return fig