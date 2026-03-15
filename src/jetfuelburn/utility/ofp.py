# %%
try:
    import pandas as pd
except ImportError as e:
    raise ImportError(
        f"Optional dependency missing: {e}. "
        "Install all required packages with: pip install jetfuelburn[optionaldependencies]"
    ) from e

import math
import yaml
from pathlib import Path
from jetfuelburn import ureg


@ureg.check(
    None,
    None,
    None,
    "[length]",
)    
def _get_aircraft_performance(
    filepath_perf_data: Path,
    aircraft_type: str,
    phase: str,
    alt: float | ureg.Quantity,
):
    with open(filepath_perf_data, "r") as f:
        data = yaml.safe_load(f)

    if phase not in ("climb", "descent"):
        raise ValueError(f"Unknown flight phase: {phase!r}. Use 'climb' or 'descent'.")

    if aircraft_type not in data:
        available = sorted(data.keys()) if data else []
        raise ValueError(f"Aircraft type {aircraft_type!r} not found in {filepath_perf_data}. Available: {available}")
    
    aircraft_info = data[aircraft_type]
    if aircraft_info is None or phase not in aircraft_info or aircraft_info[phase] is None:
        raise ValueError(f"Flight phase {phase!r} not found for aircraft type {aircraft_type!r} in {filepath_perf_data}")

    regimes = aircraft_info[phase]

    processed = []
    for r in regimes:
        min_alt = ureg(str(r["min_alt"])).to("ft")
        max_alt = ureg(str(r["max_alt"])).to("ft")
        rate = ureg(str(r["rate"])).to("ft/min")
        
        if min_alt == max_alt:
            raise ValueError(f"Degenerate altitude band (min == max) in regime {r.get('regime')!r}: {min_alt}")

        processed.append({
            "regime": r.get("regime"),
            "min_alt": min(min_alt, max_alt).to("ft"),
            "max_alt": max(min_alt, max_alt).to("ft"),
            "rate": rate.to("ft/min")
        })
        
    for p in processed:
        if p["min_alt"] <= alt <= p["max_alt"]:
            return p["rate"]
    raise ValueError(f"Altitude {alt} not found in any altitude band for aircraft type {aircraft_type!r} in {filepath_perf_data}")


def generate_4d_trajectory(
    df_ofp: pd.DataFrame,
    aircraft_type: str,
    filepath_perf_data: Path,
    resolution_min: float = 1.0,
    strategy: str = "leveloff",
    colname_wp: str = "waypoint",
    colname_timecum: str = "timecum",
    colname_alt: str = "alt",
    colname_lat: str = "lat",
    colname_lon: str = "lon",
    timestamp_start: pd.Timestamp = pd.Timestamp('2025-01-01 00:00:00'),
) -> pd.DataFrame:
    r"""
    Generate a four-dimensional (4D) trajectory from a flight plan.

    If an aircraft climbs or descends and reaches the altitude of the next waypoint before arriving at the waypoint's
    target time (inferred or given), it will level off at that target altitude until the waypoint is reached.

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
    for col in [colname_wp, colname_timecum, colname_alt, colname_lat, colname_lon]:
        if col not in df_ofp.columns:
            raise ValueError(f"Flight plan must contain column {col}.")

    df = df_ofp.copy()

    """
    add example here later
    """

    df['timestamp'] = timestamp_start + pd.to_timedelta(df[colname_timecum], unit="min")

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

    | alt  | next_alt |
    |------|----------|
    | 0    | 1000     |
    | CLB  | 1000     |
    | 1000 | 1000     |
    | 1000 | 500      |
    | DSC  | 500      |
    | 500  | 500      |
    """
    df['alt_filled'] = pd.to_numeric(df[colname_alt], errors='coerce')
    next_num = df['alt_filled'].bfill().shift(-1)
    df['next_alt'] = next_num.fillna(df['alt_filled'].ffill())

    for idx, row in df.iterrows():
        if idx == 0:
            continue

        segment_initial_alt = df.at[idx - 1, 'alt_filled']
        segment_time = (df.at[idx, 'timestamp'] - df.at[idx - 1, 'timestamp']).total_seconds() / 60

        if pd.isnull(row['alt_filled']):
            if segment_initial_alt < row['next_alt']: # climb segment
                if segment_initial_alt >= row['next_alt']: # level-off
                    df.at[idx, 'alt_filled'] = row['next_alt']
                else: # continued climb
                    rate_of_climb = _get_aircraft_performance(
                        filepath_perf_data=filepath_perf_data,
                        aircraft_type=aircraft_type,
                        phase="climb",
                        alt=segment_initial_alt * ureg.ft,
                    ).magnitude
                    segment_final_alt = segment_initial_alt + rate_of_climb * segment_time
                    if segment_final_alt > row['next_alt']: # level-off
                        df.at[idx, 'alt_filled'] = row['next_alt']
                    else:
                        df.at[idx, 'alt_filled'] = segment_final_alt
            elif segment_initial_alt > row['next_alt']: # descent segment
                if segment_initial_alt <= row['next_alt']: # level-off
                    df.at[idx, 'alt_filled'] = row['next_alt']
                else: # continued descent
                    rate_of_descent = _get_aircraft_performance(
                        filepath_perf_data=filepath_perf_data,
                        aircraft_type=aircraft_type,
                        phase="descent",
                        alt=segment_initial_alt * ureg.ft,
                    ).magnitude
                    segment_final_alt = segment_initial_alt + rate_of_descent * segment_time
                    if segment_final_alt < row['next_alt']: # level-off
                        df.at[idx, 'alt_filled'] = row['next_alt']
                    else:
                        df.at[idx, 'alt_filled'] = segment_final_alt
            else: # level flight
                df.at[idx, 'alt_filled'] = row['next_alt']
    
    list_interpolation_columns = ['alt_filled', colname_lat, colname_lon]
    df_resampled = df[['timestamp'] + list_interpolation_columns].set_index("timestamp").resample("1min").mean()
    df_resampled[list_interpolation_columns] = df_resampled[list_interpolation_columns].interpolate(method="time")
    
    df.drop(columns=list_interpolation_columns, inplace=True)
    df_merged = df_resampled.merge(
        right = df,
        left_on = df_resampled.index,
        right_on = "timestamp",
        how = "left"
    )

    return df_merged