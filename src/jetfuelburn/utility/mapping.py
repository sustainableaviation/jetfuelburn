import csv
import io
import urllib.request
from ipyleaflet import Map, Polyline, CircleMarker
from ipywidgets import HTML


def plot_ofp(
    csv_path: str,
    label_column: str = "waypoint",
    output_html: str | None = None,
) -> Map:
    r"""
    Reads a CSV file containing flight trajectory data from operational flight plans
    (OFP) and plots it on an interactive [ipyleaflet](https://ipyleaflet.readthedocs.io/) map.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file or URL containing trajectory data.
        The CSV must contain at least the following columns:

        | Column    | Type    | Description                                      |
        |-----------|---------|--------------------------------------------------|
        | `lat`     | `float` | Latitude of the waypoint (decimal degrees).      |
        | `lon`     | `float` | Longitude of the waypoint (decimal degrees).     |
        | `waypoint`| `str`   | Short name or designator for the waypoint.       |

    label_column : str, optional
        The name of the CSV column to use for labeling the waypoints (default: 'waypoint').

    output_html : str, optional
        Path to save the generated map as an HTML file. If omitted, the map is not saved to disk.
        *Note: ipyleaflet HTML export requires separate handling compared to Folium.*

    Returns
    -------
    ipyleaflet.Map
        The generated ipyleaflet Map object.

    Warnings
    -----
    Rows with missing or invalid `lat` or `lon` values are automatically skipped.

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
    )
    ```

    ```python exec="true" html="true"
    from jetfuelburn.utility.mapping import plot_ofp
    m = plot_ofp(
        csv_path="../tests/data/ofp.csv",
    )
    ```
    """
    if csv_path.startswith(("http://", "https://")):
        with urllib.request.urlopen(csv_path) as response:
            content = response.read().decode("utf-8")
        f = io.StringIO(content)
    else:
        f = open(csv_path, mode="r", encoding="utf-8")

    try:
        rows = []
        reader = csv.DictReader(f)
        for row in reader:
            lat_str = row.get("lat")
            lon_str = row.get("lon")
            if lat_str and lon_str:
                try:
                    row["lat"] = float(lat_str)
                    row["lon"] = float(lon_str)
                    rows.append(row)
                except ValueError:
                    continue
    finally:
        f.close()

    coords = [(r["lat"], r["lon"]) for r in rows]

    if rows:
        mean_lat = sum(r["lat"] for r in rows) / len(rows)
        mean_lon = sum(r["lon"] for r in rows) / len(rows)
    else:
        mean_lat, mean_lon = 0, 0

    m = Map(center=(mean_lat, mean_lon), zoom=3, scroll_wheel_zoom=True)

    polyline = Polyline(locations=coords, color="blue", fill=False, weight=3)
    m.add(polyline)

    for r in rows:
        label = str(r.get(label_column, ""))
        circle = CircleMarker(
            location=(r["lat"], r["lon"]),
            radius=3,
            color="blue",
            fill_color="blue",
            fill_opacity=0.6,
            weight=1,
            name=label,
            tooltip=HTML(value=label),
        )
        m.add(circle)

    if output_html:
        m.save(output_html, title="Flight Trajectory")
        print(f"Map saved to {output_html}")

    return m