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
    perf_data: dict, 
    resolution_min: float = 1.0, 
    strategy: str = "leveloff", 
    colname_wp: str = "waypoint",
    colname_timeto: str = "timeto",
    colname_alt: str = "alt",
    colname_lat: str = "lat",
    colname_lon: str = "lon",
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

    Returns
    -------
    polars.DataFrame

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
    if strategy != "leveloff":
        raise ValueError(f"Only strategy 'leveloff' implemented at the moment.")
    for col in [colname_wp, colname_timeto, colname_alt, colname_lat, colname_lon]:
        if col not in df_ofp.columns:
            raise ValueError(f"DataFrame is missing required column: {col}")


    # Extract lists to iterate and mutate missing times
    lats = df_ofp[colname_lat].to_list()
    lons = df_ofp[colname_lon].to_list()
    times = df_ofp[colname_timeto].to_list()
    alts = df_ofp[colname_alt].to_list()
    
    # Helper to calculate time required to traverse from start_alt to end_alt
    def calculate_transit_time(start_alt, end_alt):
        if start_alt == end_alt:
            return 0.0
            
        is_climb = end_alt > start_alt
        brackets = perf_data.get('climb', []) if is_climb else perf_data.get('descent', [])
        
        # Sort brackets by min_alt ascending for climb, descending max_alt for descent
        if is_climb:
            brackets = sorted(brackets, key=lambda x: x['min_alt'])
        else:
            brackets = sorted(brackets, key=lambda x: x['max_alt'], reverse=True)
            
        total_time = 0.0
        current_alt = start_alt
        
        for bracket in brackets:
            b_min = bracket['min_alt']
            b_max = bracket['max_alt']
            rate = bracket['rate']
            
            if is_climb:
                if current_alt >= end_alt:
                    break
                if current_alt < b_max and end_alt > b_min:
                    # Segment within this bracket
                    seg_start = max(current_alt, b_min)
                    seg_end = min(end_alt, b_max)
                    if seg_end > seg_start:
                        total_time += (seg_end - seg_start) / rate
                        current_alt = seg_end
            else:
                if current_alt <= end_alt:
                    break
                if current_alt > b_min and end_alt < b_max:
                    # Segment within this bracket
                    seg_start = min(current_alt, b_max)
                    seg_end = max(end_alt, b_min)
                    if seg_start > seg_end:
                        total_time += (seg_start - seg_end) / rate
                        current_alt = seg_end
                        
        # If we couldn't cover the full altitude difference (missing brackets), use last bracket's rate
        if is_climb and current_alt < end_alt and len(brackets) > 0:
            total_time += (end_alt - current_alt) / brackets[-1]['rate']
        elif not is_climb and current_alt > end_alt and len(brackets) > 0:
            total_time += (current_alt - end_alt) / brackets[-1]['rate']
            
        return total_time

    # First pass: fill missing `timeto` values based on altitude changes
    n = len(times)
    # Ensure first point has time 0 if missing
    if times[0] is None or (isinstance(times[0], float) and math.isnan(times[0])):
        times[0] = 0.0

    # Fill forwards
    for i in range(1, n):
        if times[i] is None or (isinstance(times[i], float) and math.isnan(times[i])):
            prev_time = times[i-1]
            prev_alt = alts[i-1]
            curr_alt = alts[i]
            
            # Use ROC/ROD to determine time needed
            transit_time = calculate_transit_time(prev_alt, curr_alt)
            times[i] = prev_time + transit_time

    # Now define the high resolution time axis
    min_time = min(times)
    max_time = max(times)
    
    # generate high-res timestamps
    high_res_time = []
    curr_t = min_time
    while curr_t <= max_time:
        high_res_time.append(curr_t)
        curr_t += resolution_min
        
    if not math.isclose(high_res_time[-1], max_time, abs_tol=1e-9) and high_res_time[-1] < max_time:
        high_res_time.append(max_time)
        
    df_high_res = pl.DataFrame({"timestamp": high_res_time})
    df_waypoints = pl.DataFrame({
        "timestamp": times,
        "lat": lats,
        "lon": lons,
        "wp_alt": alts
    })
    
    # Outer join to align waypoints with high-res grid
    df_merged = df_high_res.join(df_waypoints, on="timestamp", how="full", coalesce=True).sort("timestamp")
    
    # Interpolate lat and lon linearly
    df_merged = df_merged.with_columns([
        pl.col('lat').interpolate(),
        pl.col('lon').interpolate()
    ])
    
    # Second pass: compute altitude ensuring level-off behavior
    # Instead of linearly interpolating alt from waypoint to waypoint over time,
    # we simulate the climb/descent at each timestamp.
    
    merged_times = df_merged['timestamp'].to_list()
    merged_alts = [None] * len(merged_times)
    
    wp_idx = 0
    current_alt = alts[0]
    merged_alts[0] = current_alt
    
    # Iterate through high-res grid and simulate aircraft vertical state
    for i in range(1, len(merged_times)):
        t_curr = merged_times[i]
        dt = t_curr - merged_times[i-1]
        
        # Advance to next target waypoint
        while wp_idx < len(times) - 1 and t_curr > times[wp_idx + 1] + 1e-9:
            wp_idx += 1
            
        if wp_idx >= len(times) - 1:
            merged_alts[i] = alts[-1]
            continue
            
        target_alt = alts[wp_idx + 1]
        
        if current_alt == target_alt:
             merged_alts[i] = current_alt
             continue
             
        is_climb = target_alt > current_alt
        brackets = perf_data.get('climb', []) if is_climb else perf_data.get('descent', [])
        
        # Find applicable rate for current_alt
        applicable_rate = 0
        for bracket in brackets:
            if bracket['min_alt'] <= current_alt <= bracket['max_alt']:
                applicable_rate = bracket['rate']
                break
                
        if applicable_rate == 0 and len(brackets) > 0:
             # Fallback
             applicable_rate = brackets[-1]['rate'] if is_climb else brackets[0]['rate']
             
        # Calculate altitude change
        alt_change = applicable_rate * dt
        
        if is_climb:
            proposed_alt = current_alt + alt_change
            current_alt = min(proposed_alt, target_alt) # clamp at target
        else:
            proposed_alt = current_alt - alt_change
            current_alt = max(proposed_alt, target_alt) # clamp at target
            
        merged_alts[i] = current_alt

    df_merged = df_merged.with_columns(pl.Series("alt", merged_alts))
    
    # Return correct schema
    return df_merged.select(['timestamp', 'lat', 'lon', 'alt']).drop_nulls()

