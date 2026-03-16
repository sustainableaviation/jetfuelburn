# %%
try:
    import pandas as pd
    import plotly.graph_objects as go
except ImportError as e:
    raise ImportError(
        f"Optional dependency missing: {e}. "
        "Install all required packages with: pip install jetfuelburn[optionaldependencies]"
    ) from e

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
        ofp_path_or_df="../tests/data/ofp_with_altitude.csv",
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
        mode = "lines+markers+text"
        text = df[label_col]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[x_col] if x_col in df.columns else df.index,
            y=df[y_col] if y_col in df.columns else [],
            mode=mode,
            text=text,
            textposition="top center",
            name="Altitude",
            line=dict(color="blue"),
            marker=dict(size=6),
        )
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
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
        ofp_path_or_df="../tests/data/ofp.csv",
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
        mean_lat, mean_lon = 0, 0
    else:
        mean_lat = df[lat_col].mean()
        mean_lon = df[lon_col].mean()

    fig = go.Figure()

    fig.add_trace(
        go.Scattermap(
            lat=df[lat_col],
            lon=df[lon_col],
            mode="lines",
            line=dict(width=3, color="blue"),
            name="Flight Path",
            hoverinfo="none",
        )
    )

    for idx, row in df.reset_index(drop=True).iterrows():
        is_start = idx == 0
        is_end = idx == len(df) - 1
        label = str(row[label_col]) if label_col in df.columns else ""

        if is_start or is_end:
            marker_symbol = "marker"
            marker_size = 12
            marker_color = "red"
        else:
            marker_symbol = "circle"
            marker_size = 8
            marker_color = "blue"

        fig.add_trace(
            go.Scattermap(
                lat=[row[lat_col]],
                lon=[row[lon_col]],
                mode="markers+text",
                marker=dict(size=marker_size, color=marker_color),
                text=[label],
                textposition="top right",
                name=label if label else ("Start" if is_start else "End"),
                hoverinfo="text",
                showlegend=False,
            )
        )

    fig.update_layout(
        map=dict(
            style="open-street-map",
            center=dict(lat=mean_lat, lon=mean_lon),
            zoom=3,
        ),
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        title="Flight Trajectory",
    )

    if output_html:
        fig.write_html(output_html)

    return fig
