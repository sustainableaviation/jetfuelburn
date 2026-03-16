# %%
try:
    import pandas as pd
    import plotly.graph_objects as go
except ImportError as e:
    raise ImportError(
        f"Optional dependency missing: {e}. "
        "Install all required packages with: pip install jetfuelburn[optionaldependencies]"
    ) from e

import math
from pathlib import Path


def plot_ofp_1d(
    ofp_path_or_df: str | Path | pd.DataFrame,
    x_col: str = "timestamp",
    y_col: str = "alt",
    label_col: str | None = None,
    output_html: str | None = None,
) -> go.Figure:
    r"""
    Given an operational flight plan (OFP),
    plots a one-dimensional altitude profile using [Plotly](https://plotly.com/python/).

    Parameters
    ----------
    ofp_path_or_df : str or pandas.DataFrame
        Path to the CSV file (or URL) containing trajectory data, OR a pandas DataFrame.
    x_col : str, optional
        Column name for the x-axis (default: `'timestamp'`).
    y_col : str, optional
        Column name for the y-axis (default: `'alt'`).
    label_col : str, optional
        Column name for the labels to display next to the points (default: `None`).
    output_html : str, optional
        Path to save the generated plot as an HTML file.

    Returns
    -------
    plotly.graph_objects.Figure
        The generated Plotly figure object.

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn.utility.mapping import plot_ofp_1d
    fig = plot_ofp_1d(
        ofp_path_or_df="https://raw.githubusercontent.com/sustainableaviation/jetfuelburn/refs/heads/main/tests/data/ofp/ofp_with_altitude.csv",
    )
    ```

    ```python exec="true" html="true"
    from jetfuelburn.utility.mapping import plot_ofp_1d
    fig = plot_ofp_1d(
        ofp_path_or_df="https://raw.githubusercontent.com/sustainableaviation/jetfuelburn/refs/heads/main/tests/data/ofp/ofp_with_altitude.csv",
    )
    print(fig.to_html(full_html=False, include_plotlyjs="cdn"))
    ```
    """
    if isinstance(ofp_path_or_df, (str, Path)):
        df = pd.read_csv(ofp_path_or_df)
    else:
        df = ofp_path_or_df.copy()

    mode = "lines+markers"
    text = None
    if label_col and label_col in df.columns:
        text = df[label_col]

    fig = go.Figure()
    
    if text is not None:
        hovertemplate = "<b>%{text}</b><br>" + f"{x_col}: %{{x}}<br>{y_col}: %{{y}}<extra></extra>"
    else:
        hovertemplate = f"{x_col}: %{{x}}<br>{y_col}: %{{y}}<extra></extra>"

    fig.add_trace(
        go.Scatter(
            x=df[x_col] if x_col in df.columns else df.index,
            y=df[y_col] if y_col in df.columns else [],
            mode=mode,
            text=text,
            textposition="top center",
            name="Trace",
            line=dict(color="blue"),
            marker=dict(size=6),
            hovertemplate=hovertemplate,
        )
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        showlegend=False,
    )

    if output_html:
        fig.write_html(output_html)

    return fig


def plot_ofp_2d(
    ofp_path_or_df: str | Path | pd.DataFrame,
    label_col: str = "waypoint",
    lat_col: str = "lat",
    lon_col: str = "lon",
    output_html: str | None = None,
) -> go.Figure:
    r"""
    Plots flight trajectory data from operational flight plans (OFP) on an
    interactive [Plotly Map](https://plotly.com/python/map-layers/) map.

    Parameters
    ----------
    ofp_path_or_df : str or pandas.DataFrame
        Path to the CSV file (or URL) containing trajectory data, OR a pandas DataFrame
        already containing the data.
        The data must contain at least the following columns:

        | Column     | Type    | Description                                      |
        |------------|---------|--------------------------------------------------|
        | `lat`      | `float` | Latitude of the waypoint (decimal degrees).      |
        | `lon`      | `float` | Longitude of the waypoint (decimal degrees).     |
        | `waypoint` | `str`   | Short name or designator for the waypoint.       |

    label_col : str, optional
        The name of the CSV column to use for labeling the waypoints on the map (default: `'waypoint'`).

    lat_col : str, optional
        The name of the CSV column containing latitude values (default: `'lat'`).

    lon_col : str, optional
        The name of the CSV column containing longitude values (default: `'lon'`).

    output_html : str, optional
        Path to save the generated map as an HTML file.

    Returns
    -------
    plotly.graph_objects.Figure
        The generated Plotly Figure object.

    Warnings
    -----
    Rows with missing or invalid lat/lon values are automatically skipped.

    Notes
    -----
    The map uses the OpenStreetMap style by default and is centered at the mean position
    of all valid waypoints.

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn.utility.mapping import plot_ofp_2d
    fig = plot_ofp_2d(
        ofp_path_or_df="https://raw.githubusercontent.com/sustainableaviation/jetfuelburn/refs/heads/main/tests/data/ofp/ofp_basic.csv",
        label_col="waypoint",
        lat_col="lat",
        lon_col="lon",
    )
    fig.show()
    ```

    ```python exec="true" html="true"
    from jetfuelburn.utility.mapping import plot_ofp_2d
    fig = plot_ofp_2d(
        ofp_path_or_df="https://raw.githubusercontent.com/sustainableaviation/jetfuelburn/refs/heads/main/tests/data/ofp/ofp_basic.csv",
    )
    print(fig.to_html(full_html=False, include_plotlyjs="cdn"))
    ```
    """
    if isinstance(ofp_path_or_df, (str, Path)):
        df = pd.read_csv(ofp_path_or_df)
    else:
        df = ofp_path_or_df.copy()

    if lat_col in df.columns and lon_col in df.columns:
        df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
        df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
        df = df.dropna(subset=[lat_col, lon_col])
    else:
        df = pd.DataFrame(columns=[lat_col, lon_col])

    if df.empty:
        center = dict(lat=0, lon=0)
        zoom = 1
        bounds = None
    else:
        min_lat, max_lat = df[lat_col].min(), df[lat_col].max()
        min_lon, max_lon = df[lon_col].min(), df[lon_col].max()
        
        center = dict(
            lat=(min_lat + max_lat) / 2,
            lon=(min_lon + max_lon) / 2
        )
        
        lat_span = max_lat - min_lat
        lon_span = max_lon - min_lon
        max_span = max(lat_span, lon_span, 0.1)
        
        zoom = max(0, min(18, math.log2(360 / max_span) - 0.5))

        bounds = dict(
            west=min_lon - lon_span * 0.2,
            east=max_lon + lon_span * 0.2,
            south=min_lat - lat_span * 0.2,
            north=max_lat + lat_span * 0.2,
        )

    fig = go.Figure()

    # 1. Background Path Line
    fig.add_trace(
        go.Scattermap(
            lat=df[lat_col],
            lon=df[lon_col],
            mode="lines",
            line=dict(width=3, color="blue"),
            hoverinfo="none",
            showlegend=False,
        )
    )

    if not df.empty:
        # 2. Intermediate Waypoints
        if len(df) > 2:
            intermediate = df.iloc[1:-1]
            fig.add_trace(
                go.Scattermap(
                    lat=intermediate[lat_col],
                    lon=intermediate[lon_col],
                    mode="markers",
                    marker=dict(size=8, color="blue"),
                    text=intermediate[label_col] if label_col in df.columns else None,
                    textposition="top right",
                    name="Waypoints",
                    hoverinfo="text",
                    showlegend=False,
                )
            )

        # 3. Start Point
        fig.add_trace(
            go.Scattermap(
                lat=[df.iloc[0][lat_col]],
                lon=[df.iloc[0][lon_col]],
                mode="markers",
                marker=dict(size=14, color="green", symbol="circle"),
                text=[str(df.iloc[0][label_col])] if label_col in df.columns else ["Start"],
                textposition="top right",
                name="Start",
                hoverinfo="text",
                showlegend=False,
            )
        )

        # 4. End Point
        if len(df) > 1:
            fig.add_trace(
                go.Scattermap(
                    lat=[df.iloc[-1][lat_col]],
                    lon=[df.iloc[-1][lon_col]],
                    mode="markers",
                    marker=dict(size=14, color="red", symbol="circle"),
                    text=[str(df.iloc[-1][label_col])] if label_col in df.columns else ["End"],
                    textposition="top right",
                    name="End",
                    hoverinfo="text",
                    showlegend=False,
                )
            )

    fig.update_layout(
        map=dict(
            style="open-street-map",
            center=center,
            zoom=zoom,
            bounds=bounds,
        ),
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        showlegend=False,
    )

    if output_html:
        fig.write_html(output_html)

    return fig
