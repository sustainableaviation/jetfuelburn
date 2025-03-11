from jetfuelburn import ureg


@ureg.check(
    '[mass]',
    '[dimensionless]',
    '[mass]'/'[time]',
    '[dimensionless]',
    '[time]',
    '[]',
    '[]',
    '[]',
    '[length]',
    '[length]',
)
def calculate_fuel_consumption_combined_model(
    payload: float,
    number_of_engines: int,
    fuel_flow_per_engine_idle: float,
    fuel_flow_per_engine_takeoff: float,
    lift_to_drag: float,
    time_taxi: float,
    dict_climb_segments: dict,
    dict_descent_segments: dict,
    dict_reserve_segment: float,
    R_cruise_origin_to_destination: float,
    R_cruise_destination_to_alternate: float,
) -> dict:
    r"""
    Given aircraft performance parameters, payload, climb/descent segment information and a flight distances,
    calculates the required fuel mass $m_F$ for a given mission.

    _extended_summary_

    ![Diagram](../_static/combined.svg)

    The `dict_climb_segments` and `dict_descent_segments` are nested dictionaries
    containing information about the fuel consumption during each segment of the flight.
    The dictionary should be structured as follows:

    ```python
    dict_climb_segments = {
        'takeoff': <flight_segment_dict>,
        'climb_to_10000ft': <flight_segment_dict>,
        'climb_10000ft_to_20000ft': <flight_segment_dict>,
        (...)
    }
    dict_descent_segments = {
        'descent_cruise_to_10000ft': <flight_segment_dict>,
        'descent_10000ft_to_5000ft': <flight_segment_dict>,
        (...)
    }
    ```

    With each `flight_segment_dict` containing a `time` value-pair
    and _either_ an absolute `fuel_flow_per_engine` value-pair
    or a relative `fuel_flow_per_engine_relative_to_takeoff` value-pair.

    ```python
    flight_segment_dict_absolute = {
        'time': 5*ureg.min,
        'fuel_flow_per_engine': 0.205*(ureg.kg/ureg.sec),
    }
    flight_segment_dict_relative = {
        'time': 180*ureg.s,
        'fuel_flow_per_engine_relative_to_takeoff': 0.82
    }
    ```


    References
    ----------
    - P.26 in Poll, D. I. A., & Schumann, U. (2025).
    An estimation method for the fuel burn and other performance characteristics of civil transport aircraft; part 3 full flight profile when the trajectory is specified.
    _The Aeronautical Journal_, 1-37.
    doi:[10.1017/aer.2024.141](https://doi.org/10.1017/aer.2024.141)


    Parameters
    ----------
    payload : float
        Aircraft payload [mass]
    fuel_flow_takeoff : float
        Fuel flow during takeoff (eg. from ICAO Aircraft Engine Emissions Databank) [mass/time]
    lift_to_drag : float
        Aircraft cruise lift-to-Drag ratio [dimensionless]
    climb_segment_dict : dict
        Dictionary of climb segment information
    descent_segment_dict : dict
        Dictionary of descent segment information
    R_cruise_origin_to_destination : float
        Cruise distance from origin to destination (can be zero) [length]
    R_cruise_destination_to_alternate : float
        Cruise distance from destination to alternate (can be zero) [length]

    Returns
    -------
    dict
        'mass_fuel_taxi' : ureg.Quantity
            Fuel mass for taxi [kg],
        'mass_fuel_takeoff' : ureg.Quantity
            Fuel mass for takeoff [kg],
        'mass_fuel_climb' : ureg.Quantity
            Fuel mass for climb [kg],
        'mass_fuel_cruise' : ureg.Quantity
            Fuel mass for cruise [kg],
        'mass_fuel_descent' : ureg.Quantity
            Fuel mass for descent [kg],
        'mass_fuel_approach' : ureg.Quantity
            Fuel mass for approach [kg]
    """

    if payload < 0:
        raise ValueError("Payload must be greater than zero.")
    if number_of_engines < 0:
        raise ValueError("Number of engines must be greater than zero.")
    if fuel_flow_per_engine_idle < 0:
        raise ValueError("Fuel flow during idle must be greater than zero.")
    if fuel_flow_per_engine_takeoff < 0:
        raise ValueError("Fuel flow during takeoff must be greater than zero.")
    if lift_to_drag < 0:
        raise ValueError("Lift-to-drag ratio must be greater than zero.")
    if R_cruise_origin_to_destination < 0:
        raise ValueError("Cruise distance from origin to destination must be greater than zero.")
    if R_cruise_destination_to_alternate < 0:
        raise ValueError("Cruise distance from destination to alternate must be greater than zero.")
    
    if not dict_climb_segments:
        raise ValueError("Climb segments dictionary must not be empty.")
    if not dict_descent_segments:
        raise ValueError("Descent segments dictionary must not be empty.")

    for segment in dict_climb_segments:
        if 'time' not in dict_climb_segments[segment]:
            raise ValueError("Each climb segment must have a 'time' key-value-pair.")
        if 'fuel_flow_per_engine_relative_to_takeoff' not in dict_climb_segments[segment] and 'fuel_flow_per_engine' not in dict_climb_segments[segment]:
            raise ValueError("Each climb segment must have either a 'fuel_flow_per_engine_relative_to_takeoff' or 'fuel_flow_per_engine' key-value-pair.")
        if not all(value > 0 for value in d.values()):
            raise ValueError("All values in the dictionary must be greater than 0")

    for segment in dict_descent_segments:
        if 'time' not in dict_descent_segments[segment]:
            raise ValueError("Each descent segment must have a 'time' key-value-pair.")
        if 'fuel_flow_per_engine_relative_to_takeoff' not in dict_descent_segments[segment] and 'fuel_flow_per_engine' not in dict_descent_segments[segment]:
            raise ValueError("Each descent segment must have either a 'fuel_flow_per_engine_relative_to_takeoff' or 'fuel_flow_per_engine' key-value-pair.")
        if not all(value > 0 for value in d.values()):
            raise ValueError("All values in the dictionary must be greater than 0")

    return {
        'mass_fuel_taxi': m_f_taxi.to('kg'),
        'mass_fuel_takeoff': m_f_takeoff_origin_to_destination.to('kg'),
        'mass_fuel_climb': m_f_climb_origin_to_destination.to('kg'),
        'mass_fuel_cruise': m_f_cruise_origin_to_destination.to('kg'),
        'mass_fuel_descent': m_f_descent_origin_to_destination.to('kg'),
        'mass_fuel_approach': m_f_approach_origin_to_destination.to('kg'),
    }
