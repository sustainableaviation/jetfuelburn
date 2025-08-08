from jetfuelburn import ureg
from jetfuelburn.breguet import calculate_fuel_consumption_range_equation


@ureg.check(
    '[mass]', # payload
    '[mass]', # oew
    '[]', # number_of_engines
    '[mass]/[time]', # fuel_flow_per_engine_idle
    '[mass]/[time]', # fuel_flow_per_engine_takeoff
    '[speed]', # speed_cruise
    '[time]/[length]', # tsfc_cruise, [mg/Ns] = s/m
    '[]', # lift_to_drag
    None, # dict_climb_segments_origin_to_destination
    None, # dict_descent_segments_origin_to_destination
    '[length]', # R_cruise_origin_to_destination
    '[time]', # time_taxi
    None, # dict_climb_segments_destination_to_alternate
    None, # dict_descent_segments_destination_to_alternate
    '[length]', # R_cruise_destination_to_alternate
)
def calculate_fuel_consumption_combined_model(
    payload: float,
    oew: float,
    number_of_engines: int,
    fuel_flow_per_engine_idle: float,
    fuel_flow_per_engine_takeoff: float,
    speed_cruise: float,
    tsfc_cruise: float,
    lift_to_drag: float,
    dict_climb_segments_origin_to_destination: dict,
    dict_descent_segments_origin_to_destination: dict,
    R_cruise_origin_to_destination: float,
    time_taxi: float=26*ureg.min,
    dict_climb_segments_destination_to_alternate: dict=None,
    dict_descent_segments_destination_to_alternate: dict=None,
    R_cruise_destination_to_alternate: float=0*ureg.km,
) -> dict:
    r"""
    Given aircraft performance parameters, payload, climb/descent segment information and a flight distances,
    calculates the required fuel mass $m_F$ for a given mission.

    ![Diagram](../_static/combined.svg)

    For `dict_climb_segments`, only 'takeoff' is required; other segments are optional.
    For `dict_descent_segments`, only 'approach' is required; other segments are optional.

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
        'approach': <flight_segment_dict>,
        (...)
    }
    ```

    Each `flight_segment_dict` must contain a time key-value pair and either an absolute
    `fuel_flow_per_engine` value-pair or a relative `fuel_flow_per_engine_relative_to_takeoff` value-pair.

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

    Notes
    -----

    - [ICAO Engine Emissions Databank LTO segments](https://web.archive.org/web/20220725161602/https://www.icao.int/environmental-protection/Documents/EnvironmentalReports/2022/ENVReport2022_Art17.pdf):

    | Segment Name | Duration (official LTO cycle) | Thrust  |
    |--------------|-------------------------------|---------|
    | `taxi`       | 26 minutes                    | 7%      |
    | `takeoff`    | 0.7 minutes                   | 100%    |
    | `climb`      | 2.2 minutes                   | 85%     |
    | `approach`   | 4 minutes                     | 30%     |


    References
    ----------
    - Setion 2.1.3.4 "Reference emissions landing and take-off (LTO) cycle"
    in Annex 16 to the Convention on Civil Aviation, "Environmental Protection", Volume II - Aircraft Engine Emissions, 
    Fourth Edition, July 2017

    Parameters
    ----------
    payload : float
        Aircraft payload [mass]
    oew : float
        Aircraft operating empty weight [mass]
    number_of_engines : int
        Number of engines on the aircraft [unitless]
    fuel_flow_per_engine_idle : float
        Fuel flow during taxi (eg. from ICAO Aircraft Engine Emissions Databank) [mass/time]
    fuel_flow_per_engine_takeoff : float
        Fuel flow during takeoff (eg. from ICAO Aircraft Engine Emissions Databank) [mass/time]
    speed_cruise : float
        Cruise speed [speed]
    tsfc_cruise : float
        Cruise TSFC [time/mass]
    lift_to_drag : float
        Aircraft cruise lift-to-Drag ratio [dimensionless]
    dict_climb_segments_origin_to_destination : dict
        Dictionary of climb segment information (origin to destination)
    dict_descent_segments_origin_to_destination : dict
        Dictionary of descent segment information (origin to destination)
    R_cruise_origin_to_destination : float
        Cruise distance (origin to destination, can be zero) [length]
    time_taxi : float
        Time spent taxiing [time]
    dict_climb_segments_destination_to_alternate : dict
        Dictionary of climb segment information (destination to alternate)
    dict_descent_segments_destination_to_alternate : dict
        Dictionary of descent segment information (destination to alternate)
    R_cruise_destination_to_alternate : float
        Cruise distance (destination to alternate ,can be zero) [length]

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
    
    if not dict_climb_segments_origin_to_destination:
        raise ValueError("Climb segments dictionary (origin to destination) must not be empty.")
    if not dict_descent_segments_origin_to_destination:
        raise ValueError("Descent segments dictionary (origin to destination) must not be empty.")

    def check_segments(dict_segments: dict):
        if dict_segments is None:
            return
        for segment in dict_segments.keys():
            if 'time' not in dict_segments[segment]:
                raise ValueError("Each segment must have a 'time' key-value-pair.")
            if 'fuel_flow_per_engine_relative_to_takeoff' not in dict_segments[segment] and 'fuel_flow_per_engine' not in dict_segments[segment]:
                raise ValueError("Each segment must have either a 'fuel_flow_per_engine_relative_to_takeoff' or 'fuel_flow_per_engine' key-value-pair.")
            if not all(value > 0 for value in dict_segments[segment].values()):
                raise ValueError("All values in the segment dictionary must be greater than 0")

    check_segments(dict_climb_segments_origin_to_destination)
    check_segments(dict_descent_segments_origin_to_destination)
    check_segments(dict_climb_segments_destination_to_alternate)
    check_segments(dict_descent_segments_destination_to_alternate)

    def return_correct_fuel_burn_value_from_dict(dict_segment) -> ureg.Quantity:
        if 'fuel_flow_per_engine' in dict_segment:
            return dict_segment['fuel_flow_per_engine']
        return dict_segment['fuel_flow_per_engine_relative_to_takeoff'] * fuel_flow_per_engine_takeoff

    m_f_taxi = fuel_flow_per_engine_idle * number_of_engines * time_taxi

    m_f_final_reserve = calculate_fuel_consumption_range_equation(
        R=(speed_cruise * 30 * ureg.min).to('km'),
        LD=lift_to_drag,
        m_after_cruise=(oew + payload),
        v_cruise=speed_cruise,
        TSFC_cruise=tsfc_cruise
    )

    if dict_climb_segments_destination_to_alternate is None and dict_descent_segments_destination_to_alternate is None:
        m_f_takeoff_destination_to_alternate = 0*ureg.kg
        m_f_climb_destination_to_alternate = 0*ureg.kg
        m_f_descent_destination_to_alternate = 0*ureg.kg
        m_f_approach_destination_to_alternate = 0*ureg.kg
    else:
        m_f_takeoff_destination_to_alternate = (
            return_correct_fuel_burn_value_from_dict(dict_climb_segments_destination_to_alternate['takeoff']) *
            dict_climb_segments_destination_to_alternate['takeoff']['time'] *
            number_of_engines
        )
        m_f_climb_destination_to_alternate = sum(
            return_correct_fuel_burn_value_from_dict(dict_segment) *
            dict_segment['time'] *
            number_of_engines
            for str_segment, dict_segment in dict_climb_segments_destination_to_alternate.items() 
            if str_segment != 'takeoff'
        )
        m_f_descent_destination_to_alternate = sum(
            return_correct_fuel_burn_value_from_dict(dict_segment) *
            dict_segment['time'] *
            number_of_engines
            for str_segment, dict_segment in dict_descent_segments_destination_to_alternate.items() 
            if str_segment != 'approach'
        )
        m_f_approach_destination_to_alternate = (
            return_correct_fuel_burn_value_from_dict(dict_descent_segments_destination_to_alternate['approach']) *
            dict_descent_segments_destination_to_alternate['approach']['time'] *
            number_of_engines
        )

    m_f_cruise_destination_to_alternate = calculate_fuel_consumption_range_equation(
        R=R_cruise_destination_to_alternate,
        LD=lift_to_drag,
        m_after_cruise=(
            oew + payload + m_f_descent_destination_to_alternate + 
            m_f_approach_destination_to_alternate + m_f_final_reserve + (m_f_taxi / 2)
        ),
        v_cruise=speed_cruise,
        TSFC_cruise=tsfc_cruise
    )

    m_f_destination_to_alternate = (
        m_f_takeoff_destination_to_alternate +
        m_f_climb_destination_to_alternate +
        m_f_descent_destination_to_alternate +
        m_f_cruise_destination_to_alternate
    )

    m_f_takeoff_origin_to_destination = (
        return_correct_fuel_burn_value_from_dict(dict_climb_segments_origin_to_destination['takeoff']) *
        dict_climb_segments_origin_to_destination['takeoff']['time'] *
        number_of_engines
    )
    m_f_climb_origin_to_destination = sum(
        return_correct_fuel_burn_value_from_dict(dict_segment) *
        dict_segment['time'] *
        number_of_engines
        for str_segment, dict_segment in dict_climb_segments_origin_to_destination.items() 
        if str_segment != 'takeoff'
    )
    m_f_descent_origin_to_destination = sum(
        return_correct_fuel_burn_value_from_dict(dict_segment) *
        dict_segment['time'] *
        number_of_engines
        for str_segment, dict_segment in dict_descent_segments_origin_to_destination.items() 
        if 'landing' not in str_segment.lower()
    )
    m_f_approach_origin_to_destination = (
        return_correct_fuel_burn_value_from_dict(dict_descent_segments_origin_to_destination['approach']) *
        dict_descent_segments_origin_to_destination['approach']['time'] *
        number_of_engines
    )

    m_f_cruise_origin_to_destination = calculate_fuel_consumption_range_equation(
        R=R_cruise_origin_to_destination,
        LD=lift_to_drag,
        m_after_cruise=(
            oew + payload + m_f_descent_origin_to_destination + 
            m_f_approach_origin_to_destination + m_f_destination_to_alternate + 
            m_f_final_reserve + (m_f_taxi / 2)
        ),
        v_cruise=speed_cruise,
        TSFC_cruise=tsfc_cruise
    )

    return {
        'mass_fuel_taxi': m_f_taxi.to('kg'),
        'mass_fuel_takeoff': m_f_takeoff_origin_to_destination.to('kg'),
        'mass_fuel_climb': m_f_climb_origin_to_destination.to('kg'),
        'mass_fuel_cruise': m_f_cruise_origin_to_destination.to('kg'),
        'mass_fuel_descent': m_f_descent_origin_to_destination.to('kg'),
        'mass_fuel_approach': m_f_approach_origin_to_destination.to('kg'),
    }