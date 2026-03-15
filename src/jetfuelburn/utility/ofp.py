# %%
try:
    import polars as pl
except ImportError as e:
    raise ImportError(
        f"Optional dependency missing: {e}. "
        "Install all required packages with: pip install jetfuelburn[optionaldependencies]"
    ) from e
import math


def generate_4d_trajectory(
    df_ofp: pl.DataFrame,
    perf_data: pl.DataFrame = None,
    resolution_min: float = 1.0,
    strategy: str = "leveloff",
    colname_wp: str = "waypoint",
    colname_timeto: str = "timeto",
    colname_alt: str = "alt",
    colname_lat: str = "lat",
    colname_lon: str = "lon",
    timestamp_start: pd.Timestamp = pd.Timestamp('2025-01-01 00:00:00'),
) -> pl.DataFrame:
    r"""
    Generate a four-dimensional (4D) trajectory from a flight plan.

    The function interpolates positions (lat/lon) and altitudes (alt) mapping to a high-resolution timestamp
    given the times to arrive at specific waypoints. Missing `timeto` values are inferred primarily by utilizing
    the vertical rates defined in `perf_data` to calculate the required time to bridge altitude changes between
    known points.

    If an aircraft climbs or descends and reaches the altitude of the next waypoint before arriving at the waypoint's
    target time (inferred or given), it will level off at that target altitude until the waypoint is reached.

    ??? info "Data Pipeline"

        | waypoint | timeto | alt    | ...   |
        |----------|--------|--------|-------|
        | WP1      | 5      | 0      | ...   |
        | WP2      | 5      | CLB    | ...   |
        | WP3      | 3      | 10000  | ...   |
        | WP4      | ...    | 10000  | ...   |

        gives two separate flight segments, one with a climb:

        | flight segment | waypoint | timeto | alt    | ... |
        |----------------|----------|--------|--------|-----|
        | segment 1      | WP1      | 5      | 0      | ... |
        | segment 1      | WP2      | 5      | CLB    | ... |
        | segment 1      | WP3      | ...    | 10000  | ... |

        and one with constant altitude:

        | flight segment | waypoint | timeto | alt    | ... |
        |----------------|----------|--------|--------|-----|
        | segment 2      | WP3      | 3      | 10000  | ... |
        | segment 2      | WP4      | ...    | 10000  | ... |

        With the aircraft performance data:

        | climb regime      | min_alt | max_alt | rate |
        |-------------------|---------|---------|------|
        | initial climb     | 0       | 5000    | 2000 |
        | final climb       | 5000    | 15000   | 1000 |

        The function determines first performs a linear interpolation between the waypoint:

        | timestamp           | alt    | flight segment | ... |
        |---------------------|--------|----------------|-----|
        | 2025-01-01 00:00:00 | 0      | segment 1      | ... |
        | 2025-01-01 00:01:00 | CLB    | segment 1      | ... |
        | 2025-01-01 00:02:00 | CLB    | segment 1      | ... |
        | 2025-01-01 00:03:00 | CLB    | segment 1      | ... |
        | 2025-01-01 00:04:00 | CLB    | segment 1      | ... |
        | 2025-01-01 00:05:00 | CLB    | segment 1      | ... |
        | 2025-01-01 00:06:00 | CLB    | segment 1      | ... |
        | 2025-01-01 00:07:00 | CLB    | segment 1      | ... |
        | 2025-01-01 00:08:00 | CLB    | segment 1      | ... |
        | 2025-01-01 00:09:00 | CLB    | segment 1      | ... |
        | 2025-01-01 00:10:00 | 10000  | segment 1      | ... |
        | 2025-01-01 00:11:00 | 10000  | segment 2      | ... |
        | 2025-01-01 00:12:00 | 10000  | segment 2      | ... |
        | 2025-01-01 00:13:00 | 10000  | segment 2      | ... |
        
        Next, the function determines the rate of climb (ROC) or rate of descent (ROD) for each segment
        based on the aircraft performance data and the altitude change between the waypoints.

        | timestamp           | alt    | flight segment | ... | comment                             |
        |---------------------|--------|----------------|-----|-------------------------------------|
        | 2025-01-01 00:00:00 | 0      | segment 1      | ... | initial altitude                    |
        | 2025-01-01 00:01:00 | 2000   | segment 1      | ... | initial climb regime (2000 ft/min)  |
        | 2025-01-01 00:02:00 | 4000   | segment 1      | ... | initial climb regime (2000 ft/min)  |
        | 2025-01-01 00:03:00 | 6000   | segment 1      | ... | initial climb regime (2000 ft/min)  |
        | 2025-01-01 00:04:00 | 7000   | segment 1      | ... | final climb regime (1000 ft/min)    |
        | 2025-01-01 00:05:00 | 8000   | segment 1      | ... | final climb regime (1000 ft/min)    |
        | 2025-01-01 00:06:00 | 9000   | segment 1      | ... | final climb regime (1000 ft/min)    |
        | 2025-01-01 00:07:00 | 1000   | segment 1      | ... | level-off (reached target altitude) |
        | 2025-01-01 00:08:00 | 10000  | segment 1      | ... | level-off (reached target altitude) |
        | 2025-01-01 00:09:00 | 10000  | segment 1      | ... | level-off (reached target altitude) |
        | 2025-01-01 00:10:00 | 10000  | segment 1      | ... | level-off (reached target altitude) |
        | 2025-01-01 00:11:00 | 10000  | segment 2      | ... | level cruise                        |
        | 2025-01-01 00:12:00 | 10000  | segment 2      | ... | level cruise                        | 
        | 2025-01-01 00:13:00 | 10000  | segment 2      | ... | level cruise                        |

    Parameters
    ----------
    df_ofp : polars.DataFrame
        Flight plan dataframe with columns corresponding to `colname_wp`, `colname_timeto`, corresponding
        to time to navigate to the *next* waypoint, `colname_alt`, `colname_lat`, and `colname_lon`.
    perf_data : polars.DataFrame
        Aircraft performance dataframe with columns `state` (e.g., 'CLB', 'DES'), `min_alt`, `max_alt`, 
        and `rate`.
    resolution_min : float, default 1.0
        The minimum time resolution in minutes for the generated trajectory.
    strategy : str, default 'leveloff'
        The altitude strategy to employ when arriving at altitude early.
    colname_wp : str, default 'waypoint'
    colname_timeto : str, default 'timeto'
    colname_alt : str, default 'alt'
    colname_lat : str, default 'lat'
    colname_lon : str, default 'lon'

    Returns
    -------
    polars.DataFrame
        A DataFrame with columns ``["timestamp", "lat", "lon", "alt"]`` at the requested
        time resolution, with all null rows dropped.

    Warnings
    --------
    This utility function is not intended for production use.
    The four-dimensional trajectory generated is a very crude approximation of the actual trajectory.

    Notes
    -----
    The function implements a `leveloff` strategy by default:
    If the aircraft reaches the altitude of the next waypoint before arriving at the waypoint's
    target time (or distance), it will level off at that target altitude until the waypoint is reached.

    ![Flight Plan Diagram](../_static/ofp_1.svg)

    **Figure 1:** Diagrammatic representation of the `leveloff` strategy. 
    Shown are two different _climb regimes_, which describe the altitude-dependent 
    rate of climb (ROC) and rate of descent (ROD) of an aircraft. This could, for instance, 
    be infered from the [EUROCONTROL Aircraft Performance Database](https://learningzone.eurocontrol.int/ilp/customs/ATCPFDB/details.aspx?ICAO=A359). 
    In this representation, the angle of the trajectory corresponds to the rate of climb (ROC). 
    If the rate of climb is such that the aircraft would reach the altitude defined at the next waypoint 
    before reaching the actual waypoint, the aircraft will level off at that altitude until the waypoint is reached.
    """
    if len(df_ofp) == 0:
        raise ValueError("Empty flight plan provided.")
    for col in [colname_wp, colname_timeto, colname_alt, colname_lat, colname_lon]:
        if col not in df_ofp.columns:
            raise ValueError(f"Flight plan must contain column {col}.")

    df = df_ofp.copy()

    """
    add example here later    
    """

    df['timecum'] = df['timeto'].cumsum()
    df['timestamp'] = timestamp_start + pd.to_timedelta(df['timecum'], unit="min")
    
    df_resampled = df[['timestamp', colname_lat, colname_lon]].set_index("timestamp").resample("1min").mean()
    df_resampled[[colname_lat, colname_lon]] = df_resampled[[colname_lat, colname_lon]].interpolate(method="time")
    
    df_merged = df_resampled.merge(
        right = df,
        left_on = df_resampled.index,
        right_on = "timestamp",
        how = "left"
    )

    """
    | alt  |
    |------|
    | 0    |
    | CLB  |
    | 1000 |
    | 1000 |
    | NaN  |
    | DSC  |
    | 500  |

    | alt | alt_min | alt_max |
    |-----|---------|---------|
    | 0   | 0       | 1000    |
    | CLB | 0       | 1000    |
    | 1000| 0       | 1000    |
    | 1000| 1000    | 1000    |
    | NaN | 1000    | 500     |
    | DSC | 500     | 500     |
    | 500 | 500     | 500     |
    
    """

    col_alt = pd.to_numeric(df_merged[colname_alt], errors='coerce')
    prev_num = col_alt.ffill().shift(1)
    next_num = col_alt.bfill().shift(-1)
    df_merged['alt_min'] = prev_num.fillna(col_alt)
    df_merged['alt_max'] = next_num.fillna(col_alt)

    # df_merged.remove_columns(['timecum', 'alt_min', 'alt_max'])

    return df_merged