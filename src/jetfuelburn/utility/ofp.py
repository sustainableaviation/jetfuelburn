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
        raise ValueError(
            f"Aircraft type {aircraft_type!r} not found in {perf_data_path}. Available: {available}"
        )

    aircraft_info = data[aircraft_type]
    if (
        aircraft_info is None
        or phase not in aircraft_info
        or aircraft_info[phase] is None
    ):
        raise ValueError(
            f"Flight phase {phase!r} not found for aircraft type {aircraft_type!r} in {perf_data_path}"
        )

    regimes = aircraft_info[phase]

    processed = []
    for r in regimes:
        min_alt = ureg(str(r["min_alt"])).to("ft")
        max_alt = ureg(str(r["max_alt"])).to("ft")
        rate = ureg(str(r["rate"])).to("ft/min")

        if min_alt == max_alt:
            raise ValueError(
                f"Degenerate altitude band (min == max) in regime {r.get('regime')!r}: {min_alt}"
            )

        processed.append(
            {
                "regime": r.get("regime"),
                "min_alt": min(min_alt, max_alt).to("ft"),
                "max_alt": max(min_alt, max_alt).to("ft"),
                "rate": rate.to("ft/min"),
            }
        )

    for p in processed:
        if p["min_alt"] <= alt <= p["max_alt"]:
            return p["rate"]
    raise ValueError(
        f"Altitude {alt} not found in any altitude band for aircraft type {aircraft_type!r} in {perf_data_path}"
    )


def generate_4d_trajectory(
    df_ofp: pd.DataFrame | str | Path,
    aircraft_type: str,
    perf_data_path: Path | str,
    time_resolution: ureg.Quantity = 1.0 * ureg.minute,
    strategy: str = "leveloff",
    colname_wp: str = "waypoint",
    colname_timecum: str = "timecum",
    colname_lat: str = "lat",
    colname_lon: str = "lon",
    colname_alt: str = "alt",
    unit_alt: str = "ft",
    timestamp_start: pd.Timestamp = pd.Timestamp("2025-01-01 00:00:00"),
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

    - **Climb**: the aircraft begins climbing immediately and levels off at the target altitude,
      holding it until the waypoint is reached.
    - **Descent**: the aircraft holds its current altitude for as long as possible, then begins
      descending at the applicable rate so as to arrive at the target altitude exactly at the
      next waypoint (Top of Descent / TOD back-calculation). The TOD is estimated using the
      descent rate at the current altitude; as the aircraft descends through multiple regimes
      the rate is re-evaluated at each time step.

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
    if isinstance(df_ofp, (str, Path)):
        df_ofp = pd.read_csv(df_ofp)

    if len(df_ofp) == 0:
        raise ValueError("Empty flight plan provided.")
    for col in [colname_wp, colname_timecum, colname_alt, colname_lat, colname_lon]:
        if col not in df_ofp.columns:
            raise ValueError(f"Flight plan must contain column {col}.")

    df = df_ofp.copy()

    df["timestamp"] = timestamp_start + pd.to_timedelta(df[colname_timecum], unit="min")

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
    df["alt_filled"] = pd.to_numeric(df[colname_alt], errors="coerce").astype("float64")
    next_num = df["alt_filled"].bfill().shift(-1)
    df["next_alt"] = next_num.fillna(df["alt_filled"].ffill())

    # Simulation logic to generate high-resolution 4D trajectory
    trajectory_points = []

    curr_t = df.at[0, "timestamp"]
    curr_alt = (
        float(df.at[0, "alt_filled"]) if not pd.isna(df.at[0, "alt_filled"]) else 0.0
    )
    curr_lat = df.at[0, colname_lat]
    curr_lon = df.at[0, colname_lon]

    dt_min = time_resolution.to("min").magnitude

    for idx in range(1, len(df)):
        target_t = df.at[idx, "timestamp"]
        leveloff_target = df.at[idx, "next_alt"]

        target_lat = df.at[idx, colname_lat]
        target_lon = df.at[idx, colname_lon]

        seg_start_t = curr_t
        seg_start_lat = curr_lat
        seg_start_lon = curr_lon
        duration_s = (target_t - seg_start_t).total_seconds()

        while curr_t < target_t:
            trajectory_points.append(
                {
                    "timestamp": curr_t,
                    "alt_filled": float(curr_alt),
                    colname_lat: float(curr_lat),
                    colname_lon: float(curr_lon),
                }
            )

            rem_s = (target_t - curr_t).total_seconds()
            step_s = min(dt_min * 60.0, rem_s)

            if strategy == "leveloff":
                if not math.isclose(curr_alt, leveloff_target, abs_tol=1e-3):
                    if curr_alt < leveloff_target:
                        rate = _get_aircraft_performance(
                            perf_data_path=perf_data_path,
                            aircraft_type=aircraft_type,
                            phase="climb",
                            alt=curr_alt * ureg(unit_alt),
                        )
                        r_val = rate.to(f"{unit_alt}/min").magnitude
                        curr_alt += r_val * (step_s / 60.0)
                        if curr_alt > leveloff_target:
                            curr_alt = leveloff_target
                    else:  # descent: hold altitude until TOD, then descend
                        rate = _get_aircraft_performance(
                            perf_data_path=perf_data_path,
                            aircraft_type=aircraft_type,
                            phase="descent",
                            alt=curr_alt * ureg(unit_alt),
                        )
                        r_val = rate.to(f"{unit_alt}/min").magnitude  # negative
                        alt_to_lose = curr_alt - leveloff_target
                        time_needed_s = (alt_to_lose / abs(r_val)) * 60.0
                        if rem_s <= time_needed_s:
                            curr_alt += r_val * (step_s / 60.0)
                            if curr_alt < leveloff_target:
                                curr_alt = leveloff_target

            curr_t += pd.Timedelta(seconds=step_s)
            if duration_s > 0:
                frac = (curr_t - seg_start_t).total_seconds() / duration_s
                curr_lat = seg_start_lat + (target_lat - seg_start_lat) * frac
                curr_lon = seg_start_lon + (target_lon - seg_start_lon) * frac

    trajectory_points.append(
        {
            "timestamp": curr_t,
            "alt_filled": float(curr_alt),
            colname_lat: float(curr_lat),
            colname_lon: float(curr_lon),
        }
    )

    df_res = pd.DataFrame(trajectory_points)

    # Final resampling to ensure perfectly regular grid and include waypoint names
    resample_rule = f"{int(time_resolution.to('min').magnitude)}min"
    df_resampled = df_res.set_index("timestamp").resample(resample_rule).mean()
    df_resampled = df_resampled.interpolate(method="time")

    # Merge back waypoint names and other original metadata
    df_waypoint_labels = df[[colname_wp, "timestamp"]].drop_duplicates(
        subset="timestamp"
    )
    df_merged = df_resampled.reset_index().merge(
        df_waypoint_labels, on="timestamp", how="left"
    )

    return df_merged
