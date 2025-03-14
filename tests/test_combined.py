import pytest
from jetfuelburn import ureg

from jetfuelburn.aux.tests import approx_with_units
from jetfuelburn.combined import calculate_fuel_consumption_combined_model
from .fixtures.combined import make_combined_model_case

def test_calculate_fuel_consumption_combined_model_runs(make_combined_model_case):
    make_case, cruise_ranges = make_combined_model_case
    
    for r_cruise in cruise_ranges:
        input_data, _ = make_case(r_cruise)
        result = calculate_fuel_consumption_combined_model(
            payload=input_data['payload'],
            oew=input_data['oew'],
            number_of_engines=input_data['number_of_engines'],
            fuel_flow_per_engine_idle=input_data['fuel_flow_per_engine_idle'],
            fuel_flow_per_engine_takeoff=input_data['fuel_flow_per_engine_takeoff'],
            speed_cruise=input_data['speed_cruise'],
            tsfc_cruise=input_data['tsfc_cruise'],
            lift_to_drag=input_data['lift_to_drag'],
            dict_climb_segments_origin_to_destination=input_data['dict_climb_segments_origin_to_destination'],
            dict_descent_segments_origin_to_destination=input_data['dict_descent_segments_origin_to_destination'],
            R_cruise_origin_to_destination=input_data['R_cruise_origin_to_destination'],
            time_taxi=input_data['time_taxi'],
        )
        assert isinstance(result, dict)
        assert set(result.keys()) == {
            'mass_fuel_taxi',
            'mass_fuel_takeoff',
            'mass_fuel_climb',
            'mass_fuel_cruise',
            'mass_fuel_descent',
            'mass_fuel_approach'
        }

def test_calculate_fuel_consumption_combined_model_positive_values(make_combined_model_case):
    make_case, cruise_ranges = make_combined_model_case
    
    for r_cruise in cruise_ranges:
        input_data, _ = make_case(r_cruise)
        result = calculate_fuel_consumption_combined_model(
            payload=input_data['payload'],
            oew=input_data['oew'],
            number_of_engines=input_data['number_of_engines'],
            fuel_flow_per_engine_idle=input_data['fuel_flow_per_engine_idle'],
            fuel_flow_per_engine_takeoff=input_data['fuel_flow_per_engine_takeoff'],
            speed_cruise=input_data['speed_cruise'],
            tsfc_cruise=input_data['tsfc_cruise'],
            lift_to_drag=input_data['lift_to_drag'],
            dict_climb_segments_origin_to_destination=input_data['dict_climb_segments_origin_to_destination'],
            dict_descent_segments_origin_to_destination=input_data['dict_descent_segments_origin_to_destination'],
            R_cruise_origin_to_destination=input_data['R_cruise_origin_to_destination'],
            time_taxi=input_data['time_taxi'],
        )
        for key, value in result.items():
            assert value.magnitude > 0, f"{key} should be positive, got {value}"
            assert value.units == ureg.kg, f"{key} should be in kg, got {value.units}"