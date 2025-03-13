# %%

from jetfuelburn import ureg
from jetfuelburn.breguet import calculate_fuel_consumption_based_on_breguet_range_equation

@ureg.check(
    '[mass]', '[mass]', '[]', '[mass]/[time]', '[mass]/[time]', '[speed]', 
    '[time]/[length]', '[]', None, None, '[length]', '[time]', None, None, '[length]'
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

    m_f_final_reserve = calculate_fuel_consumption_based_on_breguet_range_equation(
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

    m_f_cruise_destination_to_alternate = calculate_fuel_consumption_based_on_breguet_range_equation(
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
        return_correct_fuel_burn_value_from_dict(dict_descent_segments_origin_to_destination['descent_10000ft_to_landing']) *
        dict_descent_segments_origin_to_destination['descent_10000ft_to_landing']['time'] *
        number_of_engines
    )

    m_f_cruise_origin_to_destination = calculate_fuel_consumption_based_on_breguet_range_equation(
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

# %%

# Example dictionaries and function call remain unchanged
dict_climb_segments_origin_to_destination = {
    'takeoff': {
        'time': 0.7*ureg.min,
        'fuel_flow_per_engine': 0.205*(ureg.kg/ureg.sec),
    },
    'climb_to_10000ft': {
        'time': 4*ureg.min,
        'fuel_flow_per_engine_relative_to_takeoff': 0.85,
    },
    'climb_10000ft_to_20000ft': {
        'time': 10*ureg.min,
        'fuel_flow_per_engine_relative_to_takeoff': 0.75,
    },
    'climb_20000ft_to_cruise': {
        'time': 15*ureg.min,
        'fuel_flow_per_engine_relative_to_takeoff': 0.7,
    },
}

dict_descent_segments_origin_to_destination = {
    'descent_cruise_to_20000ft': {
        'time': 10*ureg.min,
        'fuel_flow_per_engine_relative_to_takeoff': 0.3,
    },
    'descent_20000ft_to_10000ft': {
        'time': 5*ureg.min,
        'fuel_flow_per_engine_relative_to_takeoff': 0.3,
    },
    'descent_10000ft_to_landing': {
        'time': 5*ureg.min,
        'fuel_flow_per_engine_relative_to_takeoff': 0.3,
    }
}

result = calculate_fuel_consumption_combined_model(
    payload=10*ureg.metric_ton,
    oew=44300*ureg.kg,
    number_of_engines=2,
    fuel_flow_per_engine_idle=0.088*(ureg.kg/ureg.sec),
    fuel_flow_per_engine_takeoff=0.855*(ureg.kg/ureg.sec),
    speed_cruise=833*ureg.kph,
    tsfc_cruise=15*(ureg.mg/(ureg.N*ureg.s)),
    lift_to_drag=17,
    dict_climb_segments_origin_to_destination=dict_climb_segments_origin_to_destination,
    dict_descent_segments_origin_to_destination=dict_descent_segments_origin_to_destination,
    R_cruise_origin_to_destination=2000*ureg.km,
    time_taxi=26*ureg.min,
)
# %%
