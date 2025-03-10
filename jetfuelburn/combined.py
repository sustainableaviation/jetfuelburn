from jetfuelburn import ureg


@ureg.check(
    '[mass]',
    '[dimensionless]',
    '[mass]'/'[time]',
    '[dimensionless]',
    '[]',
    '[]',
    '[length]',
    '[length]',
)
def climb_descent_extrapolation_and_range_equation(
    payload: float,
    number_of_engines: int,
    fuel_flow_per_engine_idle: float,
    fuel_flow_per_engine_takeoff: float,
    lift_to_drag: float,
    dict_climb_segment: dict,
    dict_descent_segment: dict,
    R_cruise_origin_to_destination: float,
    R_cruise_destination_to_alternate: float,
) -> dict:
    r"""
    Computes fuel consumption UPDATE DESCRIPTION

    _extended_summary_

    ![Diagram](../../_static/combined.svg)

    The `dict_climb_segment` and `dict_descent_segment`
    contain information about the fuel consumption during each segment of the flight.
    The dictionary should be structured as follows:

    ```python
    dict_climb_segment = {
        'takeoff': {
            'time': 110*ureg.s,
            'fuel_flow_per_engine': 0.205*(ureg.kg/ureg.sec),
        },
        'climb_to_10000ft': {
            'time': 5*ureg.min,
            'fuel_flow_per_engine_relative_to_takeoff': 0.82
        },
        'climb_10000ft_to_20000ft': {
            'time': 5*ureg.min,
            'fuel_flow_per_engine': 0.181*(ureg.kg/ureg.sec),
        },
        (...)
    }
    ```

    Data dictionaries can contain either 

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



    return {
        'mass_fuel_taxi': m_f_taxi.to('kg'),
        'mass_fuel_takeoff': m_f_takeoff_origin_to_destination.to('kg'),
        'mass_fuel_climb': m_f_climb_origin_to_destination.to('kg'),
        'mass_fuel_cruise': m_f_cruise_origin_to_destination.to('kg'),
        'mass_fuel_descent': m_f_descent_origin_to_destination.to('kg'),
        'mass_fuel_approach': m_f_approach_origin_to_destination.to('kg'),
    }
