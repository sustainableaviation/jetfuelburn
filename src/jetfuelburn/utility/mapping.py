try:
    import polars as pl
    import ipyleaflet
    import ipywidgets
except ImportError as e:
    raise ImportError(
        f"Optional dependency missing: {e}. "
        "Install all required packages with: pip install jetfuelburn[optionaldependencies]"
    ) from e


def plot_ofp(
    csv_path: str,
    label_column: str = "waypoint",
    lat_col: str = "lat",
    lon_col: str = "lon",
    output_html: str | None = None,
) -> ipyleaflet.Map:
    r"""
    Reads a CSV file containing flight trajectory data from operational flight plans
    (OFP) and plots it on an interactive [ipyleaflet](https://ipyleaflet.readthedocs.io/) map.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file or URL containing trajectory data.
        The CSV must contain at least the following columns:

        | Column     | Type    | Description                                      |
        |------------|---------|--------------------------------------------------|
        | `lat`      | `float` | Latitude of the waypoint (decimal degrees).      |
        | `lon`      | `float` | Longitude of the waypoint (decimal degrees).     |
        | `waypoint` | `str`   | Short name or designator for the waypoint.       |

    label_column : str, optional
        The name of the CSV column to use for labeling the waypoints on the map (default: `'waypoint'`).

    lat_col : str, optional
        The name of the CSV column containing latitude values (default: `'lat'`).

    lon_col : str, optional
        The name of the CSV column containing longitude values (default: `'lon'`).

    output_html : str, optional
        Path to save the generated map as an HTML file. If omitted, the map is not saved to disk.
        *Note: ipyleaflet HTML export requires separate handling compared to Folium.*

    Returns
    -------
    ipyleaflet.Map
        The generated ipyleaflet Map object.

    Warnings
    -----
    Rows with missing or invalid lat/lon values are automatically skipped.

    Notes
    -----
    The map is centered at the mean position of all valid waypoints.

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn.utility.mapping import plot_ofp
    plot_ofp(
        csv_path="https://raw.githubusercontent.com/sustainableaviation/jetfuelburn/refs/heads/main/tests/data/ofp.csv",
        label_column="waypoint",
        lat_col="lat",
        lon_col="lon",
    )
    ```

    ```python exec="true" html="true"
    from jetfuelburn.utility.mapping import plot_ofp
    m = plot_ofp(
        csv_path="../tests/data/ofp.csv",
    )
    ```
    """
    df = pl.read_csv(csv_path)
    if lat_col in df.columns and lon_col in df.columns:
        df = df.with_columns(
            pl.col(lat_col).cast(pl.Float64, strict=False),
            pl.col(lon_col).cast(pl.Float64, strict=False),
        ).drop_nulls(subset=[lat_col, lon_col])
    else:
        df = pl.DataFrame(schema={lat_col: pl.Float64, lon_col: pl.Float64})

    coords = df.select([lat_col, lon_col]).rows()

    if not df.is_empty():
        mean_lat = df[lat_col].mean()
        mean_lon = df[lon_col].mean()
    else:
        mean_lat, mean_lon = 0, 0

    rows = df.to_dicts()

    m = ipyleaflet.Map(center=(mean_lat, mean_lon), zoom=3, scroll_wheel_zoom=True)

    polyline = ipyleaflet.Polyline(locations=coords, color="blue", fill=False, weight=3)
    m.add(polyline)

    for idx, r in enumerate(rows):
        lat = r[lat_col]
        lon = r[lon_col]
        label_val = r.get(label_column)
        label = str(label_val) if label_val is not None else ""

        is_start = idx == 0
        is_end = idx == len(rows) - 1

        if is_start or is_end:
            endpoint_marker = ipyleaflet.Marker(
                location=(lat, lon),
                draggable=False,
            )
            endpoint_marker.tooltip = ipywidgets.HTML(value=label if label else ("Start" if is_start else "End"))
            m.add(endpoint_marker)
        else:
            circle = ipyleaflet.CircleMarker(
                location=(lat, lon),
                radius=3,
                color="blue",
                fill_color="blue",
                fill_opacity=0.6,
                weight=1,
            )
            m.add(circle)

        if label:
            label_icon = ipyleaflet.DivIcon(
                html=(
                    f'<div style="font-size:10px;font-family:sans-serif;'
                    f'white-space:nowrap;color:#222;'
                    f'text-shadow:0 0 3px #fff,0 0 3px #fff;'
                    f'margin-left:8px;margin-top:-6px;">'
                    f'{label}</div>'
                ),
                icon_size=[1, 1],
                icon_anchor=[0, 0],
            )
            label_marker = ipyleaflet.Marker(
                location=(lat, lon),
                icon=label_icon,
                draggable=False,
            )
            m.add(label_marker)

    if output_html:
        m.save(output_html, title="Flight Trajectory")
        print(f"Map saved to {output_html}")

    return m