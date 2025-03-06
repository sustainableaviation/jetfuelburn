# %%

#import numpy as np
#import pandas as pd
import pint
import pint_pandas
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry

import sys
import os

module_path = os.path.abspath("/Users/michaelweinold/github/EcoPyLot")
if module_path not in sys.path:
    sys.path.append(module_path)


from ecopylot.physics import calculate_aircraft_velocity


@ureg.check(
    '[length]', # km
    '[length]/[time]', # ft/min
    '[length]/[time]', # ft/min
    '[length]/[time]', # ft/min
    '[length]/[time]', # ft/min
    '[speed]', # kts
    '[speed]', # kts
    '[speed]', # kts
    '[speed]', # kts
)
def _generate_eurocontrol_climb_segments_complete(
    alt_ceiling_cruise: float,
    rate_initial: float,
    rate_5000_15000: float,
    rate_15000_24000: float,
    rate_mach: float,
    v_ground_initial: float,
    v_ground_5000_15000: float,
    v_ground_15000_24000: float,
    v_ground_mach: float,
) -> dict:
    """
    Given the cruise ceiling and climb performance of an aircraft, generates a dictionary of climb segments.
    Climb segments are defined by their rate of climb (eg. 1000 ft/min) and ground speed (eg. 250 kts).
    
    This function assumes there are UP TO four climb segments, as defined by eurocontrol:

    1. Initial climb (0-5'000 ft)
    2. Climb (5'000-15'000 ft)
    3. Climb (15'000-24'000 ft)
    4. Mach climb (24'000 ft - cruise altitude)

    .. image:: https://raw.githubusercontent.com/sustainableaviation/EcoPyLot/refs/heads/refactoring/ecopylot/diagrams/climb_segments.svg

    See Also
    --------
    - [Eurocontrol Aircraft Performance Database](https://contentzone.eurocontrol.int/aircraftperformance/)

    Warnings
    --------
    Note that the regression coefficients provided in Table M.7 of the Supplementary Information 
    of 

    Parameters
    ----------
    alt_ceiling_cruise : float
        Cruise altitude of the aircraft [length]
    rate_initial : float
        Rate of climb during initial climb (0-5'000 ft) [length/time]
    rate_5000_15000 : float
        Rate of climb during climb (5'000-15'000 ft) [length/time]
    rate_15000_24000 : float
        Rate of climb during climb (15'000-24'000 ft) [length/time]
    rate_mach : float
        Rate of climb during mach climb (24'000 ft - cruise altitude) [length/time]
    v_ground_initial : float
        Ground speed during initial climb (0-5'000 ft) [speed]
    v_ground_5000_15000 : float
        Ground speed during climb (5'000-15'000 ft) [speed]
    v_ground_15000_24000 : float
        Ground speed during climb (15'000-24'000 ft) [speed]
    v_ground_mach : float
        Ground speed during mach climb (24'000 ft - cruise ceiling) [speed]

    Returns
    -------
    dict
        Dictionary of climb segments, of the form:
        ```
        {
            'initial': {
                'alt_bottom': 0,
                'alt_top': 5000,
                'rate': 1000,
                'v_ground': 250,
                'time': 0,
                'distance': 0,
            },
            (...)
        }
        Note that the entries are ordered in ascending order of altitude.
    """

    for rate in [rate_initial, rate_5000_15000, rate_15000_24000, rate_mach]:
        if rate is None:
            rate = 0
    for v_ground in [v_ground_initial, v_ground_5000_15000, v_ground_15000_24000, v_ground_mach]:
        if v_ground is None:
            v_ground = 0

    for rate in [rate_initial, rate_5000_15000, rate_15000_24000]:
        if rate == 0:
            raise ValueError("Rate of climb for climb segments up to 24'000ft cannot be 0.")
    for v_ground in [v_ground_initial, v_ground_5000_15000, v_ground_15000_24000]:
        if v_ground == 0:
            raise ValueError("Ground speed for climb segments up to 24'000ft cannot be 0.")
        
    if (rate_15000_24000 == 0 or rate_15000_24000 == np.nan) and alt_ceiling_cruise > 24000*ureg.ft:
        raise ValueError("Cruise ceiling is above 24'000ft, but rate of climb for 15'000-24'000ft is 0 or NaN.")

    eurocontrol_segment_performance = {
        'initial': {
            'rate': rate_initial,
            'v_ground': v_ground_initial,
        },
        '5000_15000': {
            'rate': rate_5000_15000,
            'v_ground': v_ground_5000_15000,
        },
        '15000_24000': {
            'rate': rate_15000_24000,
            'v_ground': v_ground_15000_24000,
        },
        'mach': {
            'rate': rate_mach,
            'v_ground': v_ground_mach,
        },
    }

    eurocontrol_segment_altitudes = {
        'initial': {
            'bottom': 0*ureg.ft,
            'top': 5000*ureg.ft,
        },
        '5000_15000': {
            'bottom': 5000*ureg.ft,
            'top': 15000*ureg.ft,
        },
        '15000_24000': {
            'bottom': 15000*ureg.ft,
            'top': 24000*ureg.ft,
        },
    }
    if alt_ceiling_cruise < 15000*ureg.ft:
        raise ValueError("Cruise altitude must be above 15'000ft.")
    elif 15000*ureg.ft < alt_ceiling_cruise <= 24000*ureg.ft:
        eurocontrol_segment_altitudes['15000_24000']['top'] = alt_ceiling_cruise
        eurocontrol_segment_altitudes['mach'] = {
            'bottom': np.nan*ureg.ft,
            'top': np.nan*ureg.ft,
        }
    elif 24000*ureg.ft < alt_ceiling_cruise <= 55000*ureg.ft:
        eurocontrol_segment_altitudes['mach'] = {
            'bottom': 24000*ureg.ft,
            'top': alt_ceiling_cruise,
        }
    else:
        raise ValueError("Cruise altitude must be below 55'000ft. We're not going to space today.")
    
    climb_segments: dict = {}

    for segment_name, segment in eurocontrol_segment_performance.items():
        if (segment['rate'] != 0 and ~np.isnan(segment['rate'])) and (segment['v_ground'] != 0 and ~np.isnan(segment['v_ground'])):
            climb_segments[segment_name] = {
                'alt_bottom': eurocontrol_segment_altitudes[segment_name]['bottom'],
                'alt_top': eurocontrol_segment_altitudes[segment_name]['top'],
                'rate': segment['rate'],
                'v_ground': segment['v_ground'],
                'time': 0,
                'distance': 0,
            }
        else:
            break
    
    return climb_segments


@ureg.check(
    '[length]', # km
    '[length]/[time]', # ft/min
    '[length]/[time]', # ft/min
    '[length]/[time]', # ft/min
    '[speed]', # kts
    '[speed]', # kts
    '[speed]', # kts
)
def _generate_eurocontrol_descent_segments_complete(
    alt_ceiling_cruise: float,
    rate_approach: float,
    rate_cruise_to_24000: float,
    rate_24000_to_10000: float,
    v_approach: float,
    v_24000_to_10000: float,
    v_cruise_to_24000: float,
) -> dict:
    """
    Given the cruise ceiling and descent performance of an aircraft, generates a dictionary of descent segments.
    Descent segments are defined by their rate of descent (eg. 1000 ft/min) and ground speed (eg. 250 kts).
    
    This function assumes there are UP TO three descent segments, as defined by eurocontrol:

    1. Initial descent (cruise altitude - 24'000 ft)
    2. Descent (24'000-10'000 ft)
    3. Approach (10'000-0 ft)

    .. image:: https://raw.githubusercontent.com/sustainableaviation/EcoPyLot/refs/heads/refactoring/ecopylot/diagrams/descent_segments.svg

    See Also
    --------
    - [Eurocontrol Aircraft Performance Database](https://contentzone.eurocontrol.int/aircraftperformance/)

    Parameters
    ----------
    alt_ceiling_cruise : float
        Cruise altitude of the aircraft [length]
    rate_approach : float
        Rate of descent during approach (10'000-0 ft) [length/time]
    rate_24000_to_10000 : float
        Rate of descent during descent (24'000-10'000 ft) [length/time]
    rate_cruise_to_24000 : float
        Rate of descent during initial descent (cruise ceiling - 24'000 ft) [length/time]
    v_approach : float
        Ground speed during approach (10'000-0 ft) [speed]
    v_24000_to_10000 : float
        Ground speed during descent (24'000-10'000 ft) [speed]
    v_cruise_to_24000 : float
        Ground speed during initial descent (cruise ceiling - 24'000 ft) [speed]

    Returns
    -------
    dict
        Dictionary of climb segments, of the form:
        ```
        {
            'approach': {
                'alt_bottom': 0,
                'alt_top': 5000,
                'rate': 1000,
                'v_ground': 250,
                'time': 0,
                'distance': 0,
            },
            (...)
        }
        Note that the entries are ordered in ascending order of altitude.
    """
    
    eurocontrol_segment_performance = {
        'approach': {
            'rate': rate_approach,
            'v_ground': v_approach,
        },
        '24000_to_10000': {
            'rate': rate_24000_to_10000,
            'v_ground': v_24000_to_10000,
        },
        'cruise_to_24000': {
            'rate': rate_cruise_to_24000,
            'v_ground': v_cruise_to_24000,
        },
    }

    eurocontrol_segment_altitudes = {}

    if alt_ceiling_cruise < 15000*ureg.ft:
        return ValueError("Cruise altitude must be above 15'000ft.")
    elif 15000*ureg.ft <= alt_ceiling_cruise <= 24000*ureg.ft:
        eurocontrol_segment_altitudes['cruise_to_24000'] = {
            'bottom': np.nan*ureg.ft,
            'top': np.nan*ureg.ft,
        }
        eurocontrol_segment_altitudes['24000_to_10000'] = {
            'bottom': 10000*ureg.ft,
            'top': alt_ceiling_cruise,
        }
    elif 24000*ureg.ft < alt_ceiling_cruise <= 55000*ureg.ft:
        eurocontrol_segment_altitudes['cruise_to_24000'] = {
            'bottom': 24000*ureg.ft,
            'top': alt_ceiling_cruise,
        }
        eurocontrol_segment_altitudes['24000_to_10000'] = {
            'bottom': 10000*ureg.ft,
            'top': 24000*ureg.ft,
        }
    else:
        return ValueError("Cruise altitude must be below 55'000ft. We're not going to space today.")
    
    eurocontrol_segment_altitudes['approach'] = {
        'bottom': 0*ureg.ft,
        'top': 10000*ureg.ft,
    }

    descent_segments: dict = {}

    for segment_name, segment in eurocontrol_segment_performance.items():
        if (segment['rate'] != 0 and ~np.isnan(segment['rate'])) and (segment['v_ground'] != 0 and ~np.isnan(segment['v_ground'])):
            descent_segments[segment_name] = {
                'alt_bottom': eurocontrol_segment_altitudes[segment_name]['bottom'],
                'alt_top': eurocontrol_segment_altitudes[segment_name]['top'],
                'rate': segment['rate'],
                'v_ground': segment['v_ground'],
                'time': 0,
                'distance': 0,
            }
        else:
            pass
    
    return descent_segments


@ureg.check(
    '[length]', # ft
    None, # dictionary
)
def _compute_segments_distance_and_time_based_on_alt_cruise(
    alt_cruise: float,
    segments: dict,
) -> dict:
    """
    Given a dictionary of climb or descent segments and a target cruise altitude,
    computes the distance traveled and time spent in each segment.
    Segments outside the target range or altitude are removed from the segments dictionary.

    If the target cruise altitude is below the top of a segment,
    the distance and time for that segment are computed up to the target cruise altitude.

    .. image:: https://raw.githubusercontent.com/sustainableaviation/EcoPyLot/refs/heads/refactoring/ecopylot/diagrams/climb_segment_time_distance.svg

    Parameters
    ----------
    alt_cruise : float
        Target cruise altitude [length]
    segments : dict
        Dictionary of climb or descent segments

    Returns
    -------
    dict
        Dictionary of climb or descent segments with updated distance and time.
    """
    if alt_cruise < 0 * ureg.ft:
        raise ValueError("Cruise altitude must be greater than 0 (d-uh).")
    if alt_cruise > 55000*ureg.ft:
        raise ValueError("Cruise altitude must be less than 55'000 ft. We're not going to space today.")
    
    alt_top_previous = 0
    for segment in segments.values():
        if segment['alt_top'] < alt_top_previous:
            raise ValueError("Segment altitudes must be in ascending order of altitude.")
        else:
            alt_top_previous = segment['alt_top']
    
    segments_to_retain = []

    for segment_name, segment in segments.items():
        if alt_cruise <= segment['alt_top']:
            segment['time'] = ((alt_cruise - segment['alt_bottom']) / segment['rate']).to(ureg.minute)
            segment['distance'] = (segment['time'] * segment['v_ground']).to(ureg.km)
            segment['alt_top'] = alt_cruise
            segments_to_retain.append(segment_name)
            break
        else:
            segment['time'] = ((segment['alt_top'] - segment['alt_bottom']) / segment['rate']).to(ureg.minute)
            segment['distance'] = (segment['time'] * segment['v_ground']).to(ureg.km)
            segments_to_retain.append(segment_name)
    
    return {key: segments[key] for key in segments_to_retain}


@ureg.check(
    '[length]', # ft
    None, # dictionary
)
def _compute_segments_distance_and_time_based_on_route_distance(
    distance_traveled: float,
    segments: dict,
) -> dict:
    """
    Given a dictionary of climb or descent segments and a target distance traveled,
    re-computes the distance traveled and time spent in each segment.
    Segments outside the target range or altitude are removed from the segments dictionary.

    If the target distance traveled within a segment is smaller than the distance of that segment,
    the distance and time for that segment are computed up to the target distance traveled.

    .. image:: https://raw.githubusercontent.com/sustainableaviation/EcoPyLot/refs/heads/refactoring/ecopylot/diagrams/climb_segment_time_distance.svg

    Parameters
    ----------
    distance_traveled : float
        Target distance traveled [length]
    segments : dict
        Dictionary of climb or descent segments

    Returns
    -------
    dict
        Dictionary of climb or descent segments with updated distance and time.
    """

    distance_cumulative = 0
    segments_to_retain = []

    for segment_name, segment in segments.items():
        if segment['distance'] == 0:
            raise ValueError("Segment distance must be greater than 0.")
        
        distance_cumulative += segment['distance']
        distance_segment_start = distance_cumulative - segment['distance']
        distance_segment_end = distance_cumulative
        
        if distance_traveled > distance_segment_end:
            segments_to_retain.append(segment_name)
        elif distance_segment_start <= distance_traveled <= distance_segment_end:
            segment['distance'] = distance_traveled - distance_segment_start
            segment['time'] = (segment['distance'] / segment['v_ground']).to(ureg.minute)
            segment['alt_top'] = segment['rate'] * segment['time'] + segment['alt_bottom']
            segments_to_retain.append(segment_name)

    return {key: segments[key] for key in segments_to_retain}


@ureg.check(
    '[length]', # km
    None, # dictionary
)
def _segments_function(
    x: float,
    segments: dict,
) -> pint.Quantity:
    """
    Given a distance `x` from a point of reference and a dictionary of climb or descent segments,
    returns the altitude of the aircraft.
    
    Note that the segments dictionary must be in ascending order of altitude.
    If climb segments are passed, the distance is from the origin.
    If descent segments are passed, the distance is from the destination.
    
    If the distance `x` is greater than the total climb or descent distance,
    the cruise altitude of the aircraft is returned.

    Parameters
    ----------
    x : float
        Distance from the point of reference [length]
    segments : dict
        Dictionary of climb or descent segments

    Returns
    -------
    float
        Altitude of the aircraft [length], in feet
    """
    if x < 0:
        return ValueError("Distance from origin must be greater than or equal to 0.")
    
    alt_top_previous = 0
    for segment in segments.values():
        if segment['alt_top'] < alt_top_previous:
            raise ValueError("Segment altitudes must be in ascending order of altitude.")
        else:
            alt_top_previous = segment['alt_top']

    current_segment_distance_from_ref = 0
    previous_segment_distance_from_ref = 0
    
    for segment in segments.values():
        current_segment_distance_from_ref += segment['distance']
        if previous_segment_distance_from_ref <= x <= current_segment_distance_from_ref:
            k = segment['rate'] / segment['v_ground']
            d = segment['alt_bottom']
            return (k * (x - previous_segment_distance_from_ref) + d).to(ureg.ft)
        previous_segment_distance_from_ref = current_segment_distance_from_ref
    
    if x > current_segment_distance_from_ref:
        return segments[list(segments.keys())[-1]]['alt_top'].to(ureg.ft)


@ureg.check(
    '[length]', # km
    None, # dictionary
    None, # dictionary
)
def _compute_top_of_climb_distance(
    flight_distance: float,
    climb_segments: dict,
    descent_segments: dict,
) -> float:
    """
    Given the flight distance between origin and destination airports and a dictionary of climb and descent segments,
    determines the distance of the top-of-climb point from the origin airport.

    Note that this is useful only the top-of-climb point is reached before target cruise altitude is reached.
    This can be the case for shorter flights.

    .. image:: https://raw.githubusercontent.com/sustainableaviation/EcoPyLot/refs/heads/refactoring/ecopylot/diagrams/climb_descent_segment_intersection.svg

    Parameters
    ----------
    flight_distance : float
        Total flight distance [length]
    climb_segments : dict
        Dictionary of climb segments
    descent_segments : dict
        Dictionary of descent segments

    Returns
    -------
    float
        Distance from the origin to the top-of-climb point [length]
    """
    array_climb_segments_altitudes = []
    array_descent_segments_altitudes = []
    distance_unit: pint.Unit = flight_distance.units

    for x in range(0, int(flight_distance.magnitude + 1), 1):
        array_climb_segments_altitudes.append(_segments_function(x * distance_unit, climb_segments))
        array_descent_segments_altitudes.append(_segments_function((flight_distance - x * distance_unit), descent_segments))

    differences = [
        abs(climb - descent) 
        for climb, descent in zip(array_climb_segments_altitudes, array_descent_segments_altitudes)
    ]

    return differences.index(min(differences)) * distance_unit


@ureg.check(
    None, # dictionary
    None, # dictionary
    None, # float
)
def _generate_flight_profile_dataframe_from_segments(
    distance_route: float,
    climb_segments: dict,
    descent_segments: dict,
) -> pd.DataFrame:
    """_summary_

    _extended_summary_

    Parameters
    ----------
    distance_route : float
        _description_
    climb_segments : dict
        _description_
    descent_segments : dict
        _description_

    Returns
    -------
    pd.DataFrame
        _description_
    """
    
    total_distance_climb = 0
    total_distance_descent = 0

    for segment in climb_segments.values():
        total_distance_climb += segment['distance']
    for segment in descent_segments.values():
        total_distance_descent += segment['distance']

    distance_cruise = distance_route - total_distance_climb - total_distance_descent
    alt_cruise = climb_segments[list(climb_segments.keys())[-1]]['alt_top']

    altitude = []
    distance = []

    for x in range(0, int(distance_route.magnitude)+1, 1):
        x = x * distance_route.units
        if 0 <= x <= total_distance_climb:
            distance.append(x)
            altitude.append(
                _segments_function(
                    x=x,
                    segments=climb_segments,
                )
            )
        elif total_distance_climb < x <= total_distance_climb + distance_cruise:
            distance.append(x)
            altitude.append(alt_cruise)
        elif total_distance_climb + distance_cruise < x <= distance_route:
            distance.append(x)
            altitude.append(
                _segments_function(
                    x=distance_route - x,
                    segments=descent_segments,
                )
            )

    df = pd.DataFrame({
        'Distance': distance,
        'Altitude': altitude,
    }).pint.convert_object_dtype()

    return df

@ureg.check(
    None, # pd.DataFrame
    '[length]', # float
    '[length]', # float
)
def sanity_checks_flight_profile(
    selected_aircraft: pd.Series,
    altitude_cruise: float,
    distance_route: float,
) -> None:
    """_summary_

    _extended_summary_

    Parameters
    ----------
    df_aircraft : _type_
        _description_
    dict : _type_
        _description_
    float : _type_
        _description_
    """

    if distance_route < 0 * ureg.ft:
        raise ValueError(f"Target route distance ({distance_route}) must not be smaller than 0.")
    if distance_route > selected_aircraft['Range Cruise']:
        raise ValueError(f"Target route distance ({distance_route}) must not be greater than aircraft range ({selected_aircraft['Range Cruise']}).")
    if distance_route < 30 * ureg.km:
        raise ValueError(f"Target route distance ({distance_route}) is very small. Why not take the train?")
    if altitude_cruise < 0 * ureg.ft:
        raise ValueError(f"Target cruise altitude ({altitude_cruise}) must not be smaller than 0.")
    if altitude_cruise > selected_aircraft['Ceiling Cruise'] * 100 * ureg.ft:
        raise ValueError(f"Target cruise altitude ({altitude_cruise}) must not be greater than flight ceiling ({selected_aircraft['Ceiling Cruise'] * 100 * ureg.ft}).")


@ureg.check(
    None, # pd.DataFrame
    '[length]', # ft
    '[length]', # km
)
def compute_flight_profile(
    selected_aircraft: pd.Series,
    altitude_cruise: float,
    distance_route: float,
) -> (dict, dict, float):
    """_summary_

    _extended_summary_

    Parameters
    ----------
    df_aircraft : _type_
        _description_
    dict : _type_
        _description_
    float : _type_
        _description_
    """

    sanity_checks_flight_profile(
        selected_aircraft=selected_aircraft,
        altitude_cruise=altitude_cruise,
        distance_route=distance_route,
    )

    climb_segments_complete = _generate_eurocontrol_climb_segments_complete(
        alt_ceiling_cruise=selected_aircraft['Ceiling Cruise'] * 100 * ureg.ft,
        rate_initial=selected_aircraft['ROC Initial Climb (to 5000ft)'],
        rate_5000_15000=selected_aircraft['ROC Climb (to FL150)'],
        rate_15000_24000=selected_aircraft['ROC Climb (to FL240)'],
        rate_mach=selected_aircraft['ROC Mach Climb'],
        v_ground_initial=selected_aircraft['IAS Initial Climb (to 5000ft)'],
        v_ground_5000_15000=selected_aircraft['IAS Climb (to FL150)'],
        v_ground_15000_24000=selected_aircraft['IAS Climb (to FL240)'],
        v_ground_mach=calculate_aircraft_velocity(
            mach_number=selected_aircraft['Mach Climb'],
            altitude=24000*ureg.ft
        )
    )

    descent_segments_complete = _generate_eurocontrol_descent_segments_complete(
        alt_ceiling_cruise=selected_aircraft['Ceiling Cruise'] * 100 * ureg.ft,
        rate_cruise_to_24000=selected_aircraft['ROD Initial Descent (to FL240)'],
        rate_24000_to_10000=selected_aircraft['ROD Descent (to FL100)'],
        rate_approach=selected_aircraft['ROD Approach'],
        v_cruise_to_24000=selected_aircraft['Mach Initial Descent (to FL240)'],
        v_24000_to_10000=selected_aircraft['IAS Descent (to FL100)'],
        v_approach=selected_aircraft['IAS Approach'],
    )

    climb_segments_to_cruise_altitude = _compute_segments_distance_and_time_based_on_alt_cruise(
        alt_cruise=altitude_cruise,
        segments=climb_segments_complete
    )

    descent_segments_from_cruise_altitude = _compute_segments_distance_and_time_based_on_alt_cruise(
        alt_cruise=altitude_cruise,
        segments=descent_segments_complete
    )

    total_non_cruise_distance = 0*ureg.km

    for segment in climb_segments_to_cruise_altitude.values():
        total_non_cruise_distance += segment['distance']
    for segment in descent_segments_from_cruise_altitude.values():
        total_non_cruise_distance += segment['distance']
    
    if total_non_cruise_distance > distance_route:
        distance_top_of_climb = _compute_top_of_climb_distance(
            flight_distance=distance_route,
            climb_segments=climb_segments_to_cruise_altitude,
            descent_segments=descent_segments_from_cruise_altitude,
        )
        climb_segments_shortened = _compute_segments_distance_and_time_based_on_route_distance(
            distance_traveled=distance_top_of_climb,
            segments=climb_segments_to_cruise_altitude
        )
        descent_segments_shortened = _compute_segments_distance_and_time_based_on_route_distance(
            distance_traveled=distance_route - distance_top_of_climb,
            segments=descent_segments_from_cruise_altitude
        )
        return (
            climb_segments_shortened, 
            descent_segments_shortened,
            0 * ureg.km,
            _generate_flight_profile_dataframe_from_segments(
                climb_segments=climb_segments_shortened,
                descent_segments=descent_segments_shortened,
                distance_route=distance_route
            )
        )
    else:
        return (
            climb_segments_to_cruise_altitude,
            descent_segments_from_cruise_altitude,
            distance_route - total_non_cruise_distance,
            _generate_flight_profile_dataframe_from_segments(
                climb_segments=climb_segments_to_cruise_altitude,
                descent_segments=descent_segments_from_cruise_altitude,
                distance_route=distance_route
            )
        )