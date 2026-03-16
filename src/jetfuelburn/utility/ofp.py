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
    perf_data_path: Path,
    aircraft_type: str,
    phase: str,
    alt: float | ureg.Quantity,
):
    """
    Look up the climb or descent rate for a given aircraft type and altitude.

    Given a YAML performance data file, returns the rate of climb (positive)
    or rate of descent (negative) applicable to the supplied altitude, according
    to the altitude-band regime defined for the aircraft and flight phase.

    Performance data must be provided in the following format:
    
    ```yaml
    B123:
        climb:
            - regime: initial_climb
                description: Initial climb to 5000 ft
                min_alt: 0 ft
                max_alt: 4639 ft
                rate: 2979 ft/min
        descent:
            - regime: initial_descent
                description: Initial descent to FL240
                max_alt: 40489 ft
                min_alt: 25323 ft
                rate: -1059 ft/min
    ```

    Parameters
    ----------
    perf_data_path : Path
        Path to the YAML file containing aircraft performance data.
        The file must follow the schema used by the EUROCONTROL APD dataset
        (see `src/jetfuelburn/data/EurocontrolAPD/data.yaml`).
    aircraft_type : str
        ICAO aircraft type designator (e.g. ``'B123'``), matching a top-level
        key in the YAML file.
    phase : str
        Flight phase; must be either ``'climb'`` or ``'descent'``.
    alt : pint.Quantity
        Current altitude with a length dimension (e.g. ``30000 * ureg.ft``).
        The ``@ureg.check`` decorator enforces dimensional correctness.

    Returns
    -------
    pint.Quantity
        Rate of climb or descent in ``ft/min``.  Climb rates are positive;
        descent rates are negative.

    Raises
    ------
    ValueError
        If *phase* is not ``'climb'`` or ``'descent'``.
    ValueError
        If *aircraft_type* is not present in the YAML file.
    ValueError
        If the flight phase is missing for the given *aircraft_type*.
    ValueError
        If a regime in the YAML file has ``min_alt == max_alt`` (degenerate band).
    ValueError
        If *alt* does not fall within any altitude band defined for the aircraft
        and flight phase.

    Warning
    -------
    Climb rates are positive and descent rates are negative numbers!

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    
    jetfuelburn._get_aircraft_performance(
        jetfuelburn.data.EurocontrolAPD.data.yaml,
        "B123",
        "climb",
        30000 * ureg.ft,
    )
    ```
    """
    with open(perf_data_path, "r") as f:
        data = yaml.safe_load(f)

    if phase not in ("climb", "descent"):
        raise ValueError(f"Unknown flight phase: {phase!r}. Use 'climb' or 'descent'.")

    if aircraft_type not in data:
        available = sorted(data.keys()) if data else []
        raise ValueError(f"Aircraft type {aircraft_type!r} not found in {perf_data_path}. Available: {available}")
    
    aircraft_info = data[aircraft_type]
    if aircraft_info is None or phase not in aircraft_info or aircraft_info[phase] is None:
        raise ValueError(f"Flight phase {phase!r} not found for aircraft type {aircraft_type!r} in {perf_data_path}")

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
    raise ValueError(f"Altitude {alt} not found in any altitude band for aircraft type {aircraft_type!r} in {perf_data_path}")


def generate_4d_trajectory(
    df_ofp: pd.DataFrame,
    aircraft_type: str,
    perf_data_path: Path,
    time_resolution: ureg.Quantity = 1.0 * ureg.minute,
    strategy: str = "leveloff",
    colname_wp: str = "waypoint",
    colname_timecum: str = "timecum",
    colname_lat: str = "lat",
    colname_lon: str = "lon",
    colname_alt: str = "alt",
    unit_alt: str = "ft",
    timestamp_start: pd.Timestamp = pd.Timestamp('2025-01-01 00:00:00'),
) -> pd.DataFrame:
    r"""
    Generate a four-dimensional (4D) trajectory from a flight plan.

    If an aircraft climbs or descends and reaches the altitude of the next waypoint before arriving at the waypoint's
    target time (inferred or given), it will level off at that target altitude until the waypoint is reached.

    Parameters
    ----------
    df_ofp : pd.DataFrame
        Operational flight plan (OFP) as a :class:`pandas.DataFrame`.
        Must contain at minimum the columns named by *colname_wp*,
        *colname_timecum*, *colname_alt*, *colname_lat*, and *colname_lon*.
        The altitude column may contain numeric values (in feet) **or** the
        string tokens ``'CLB'`` / ``'DSC'`` for climb/descent waypoints whose
        exact altitude is not yet known.
    aircraft_type : str
        ICAO aircraft type designator (e.g. ``'B123'``), passed directly to
        :func:`_get_aircraft_performance`.
    perf_data_path : Path
        Path to the YAML performance data file; forwarded to
        :func:`_get_aircraft_performance`.
    time_resolution : pint.Quantity, optional
        Resampling resolution as a Pint time quantity (e.g. ``1 * ureg.minute``).
        The output trajectory is resampled to this resolution using linear
        interpolation. Default is ``1 * ureg.minute``.
    strategy : str, optional
        Altitude interpolation strategy. Currently only ``'leveloff'`` is
        implemented (default). With this strategy the aircraft levels off at
        the target altitude of the next waypoint if it would otherwise
        overshoot.
    colname_wp : str, optional
        Name of the waypoint-identifier column in *df_ofp*. Default ``'waypoint'``.
    colname_timecum : str, optional
        Name of the cumulative flight time column (in minutes) in *df_ofp*.
        Default ``'timecum'``.
    colname_alt : str, optional
        Name of the altitude column (in feet, or ``'CLB'``/``'DSC'`` tokens)
        in *df_ofp*. Default ``'alt'``.
    colname_lat : str, optional
        Name of the latitude column in *df_ofp*. Default ``'lat'``.
    colname_lon : str, optional
        Name of the longitude column in *df_ofp*. Default ``'lon'``.
    unit_alt : str, optional
        Pint-compatible unit string for altitude values in *df_ofp* and in the
        output (e.g. ``'ft'``, ``'m'``). Altitude columns are read and written
        as plain :class:`float` in this unit. Default is ``'ft'``.
    timestamp_start : pd.Timestamp, optional
        UTC departure timestamp. Cumulative flight times from *colname_timecum*
        are added as :class:`pandas.Timedelta` offsets to this value to produce
        absolute timestamps. Default is ``pd.Timestamp('2025-01-01 00:00:00')``.

    Returns
    -------
    pd.DataFrame
        Resampled 4-D trajectory merged with the original OFP data.
        The DataFrame is indexed by the resampling timestamps and contains
        (at minimum) the interpolated columns ``alt_filled``, *colname_lat*,
        and *colname_lon*.

    Raises
    ------
    ValueError
        If *df_ofp* is empty.
    ValueError
        If any of the required columns (*colname_wp*, *colname_timecum*,
        *colname_alt*, *colname_lat*, *colname_lon*) is missing from *df_ofp*.

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

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    df_ofp = pd.DataFrame({
        "waypoint": ["DEP", "MID", "ARR"],
        "alt": [0, "CLB", 5000],
        "timecum": [0, 60, 120],
        "lat": [47.0, 47.5, 48.0],
        "lon": [8.0, 8.5, 9.0],
    })
    result = jetfuelburn.generate_4d_trajectory(
        df_ofp,
        "B123",
        jetfuelburn.DATA_YAML,
        time_resolution=1 * ureg.minute,
        timestamp_start=pd.Timestamp("2025-01-01 00:00:00"),
    )
    ```
    """
    if len(df_ofp) == 0:
        raise ValueError("Empty flight plan provided.")
    for col in [colname_wp, colname_timecum, colname_alt, colname_lat, colname_lon]:
        if col not in df_ofp.columns:
            raise ValueError(f"Flight plan must contain column {col}.")

    df = df_ofp.copy()

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
    df['alt_filled'] = pd.to_numeric(df[colname_alt], errors='coerce').astype('float64')
    next_num = df['alt_filled'].bfill().shift(-1)
    df['next_alt'] = next_num.fillna(df['alt_filled'].ffill())

    for idx, row in df.iterrows():
        if idx == 0:
            continue

        segment_initial_alt = df.at[idx - 1, 'alt_filled']
        segment_time = (df.at[idx, 'timestamp'] - df.at[idx - 1, 'timestamp']).total_seconds() / 60 * ureg.minute

        if pd.isnull(row['alt_filled']):
            if segment_initial_alt < row['next_alt']: # climb segment
                if segment_initial_alt >= row['next_alt']: # level-off
                    df.at[idx, 'alt_filled'] = row['next_alt']
                else: # continued climb
                    rate_of_climb = _get_aircraft_performance(
                        perf_data_path=perf_data_path,
                        aircraft_type=aircraft_type,
                        phase="climb",
                        alt=segment_initial_alt * ureg(unit_alt),
                    )
                    segment_final_alt = (segment_initial_alt * ureg(unit_alt) + rate_of_climb * segment_time).to(unit_alt).magnitude
                    if segment_final_alt > row['next_alt']: # level-off
                        df.at[idx, 'alt_filled'] = row['next_alt']
                    else:
                        df.at[idx, 'alt_filled'] = segment_final_alt
            elif segment_initial_alt > row['next_alt']: # descent segment
                if segment_initial_alt <= row['next_alt']: # level-off
                    df.at[idx, 'alt_filled'] = row['next_alt']
                else: # continued descent
                    rate_of_descent = _get_aircraft_performance(
                        perf_data_path=perf_data_path,
                        aircraft_type=aircraft_type,
                        phase="descent",
                        alt=segment_initial_alt * ureg(unit_alt),
                    )
                    segment_final_alt = (segment_initial_alt * ureg(unit_alt) + rate_of_descent * segment_time).to(unit_alt).magnitude
                    if segment_final_alt < row['next_alt']: # level-off
                        df.at[idx, 'alt_filled'] = row['next_alt']
                    else:
                        df.at[idx, 'alt_filled'] = segment_final_alt
            else: # level flight
                df.at[idx, 'alt_filled'] = row['next_alt']
    
    list_interpolation_columns = ['alt_filled', colname_lat, colname_lon]
    resample_rule = f"{int(time_resolution.to('min').magnitude)}min"
    df_resampled = df[['timestamp'] + list_interpolation_columns].set_index("timestamp").resample(resample_rule).mean()
    df_resampled[list_interpolation_columns] = df_resampled[list_interpolation_columns].interpolate(method="time")
    
    df.drop(columns=list_interpolation_columns + ['next_alt'], inplace=True)
    df_merged = df_resampled.merge(
        right = df,
        left_on = df_resampled.index,
        right_on = "timestamp",
        how = "left"
    )

    return df_merged