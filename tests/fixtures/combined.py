import pytest
from jetfuelburn import ureg

@pytest.fixture(scope="module")
def make_combined_model_case():
    """
    Fixture returning a factory function to generate a test case for combined fuel consumption model.

    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)
    """
    climb_segments = {
        'takeoff': {
            'time': 0.7 * ureg.min,
            'fuel_flow_per_engine': 0.205 * (ureg.kg / ureg.sec),
        },
        'climb_to_10000ft': {
            'time': 4 * ureg.min,
            'fuel_flow_per_engine_relative_to_takeoff': 0.85,
        },
        'climb_10000ft_to_20000ft': {
            'time': 10 * ureg.min,
            'fuel_flow_per_engine_relative_to_takeoff': 0.75,
        },
        'climb_20000ft_to_cruise': {
            'time': 15 * ureg.min,
            'fuel_flow_per_engine_relative_to_takeoff': 0.7,
        },
    }

    descent_segments = {
        'descent_cruise_to_20000ft': {
            'time': 10 * ureg.min,
            'fuel_flow_per_engine_relative_to_takeoff': 0.3,
        },
        'descent_20000ft_to_10000ft': {
            'time': 5 * ureg.min,
            'fuel_flow_per_engine_relative_to_takeoff': 0.3,
        },
        'approach': {
            'time': 5 * ureg.min,
            'fuel_flow_per_engine_relative_to_takeoff': 0.3,
        }
    }

    cases = {
        2000 * ureg.km: {
            'payload': 10 * ureg.metric_ton,
            'oew': 44300 * ureg.kg,
            'number_of_engines': 2,
            'fuel_flow_per_engine_idle': 0.088 * (ureg.kg / ureg.sec),
            'fuel_flow_per_engine_takeoff': 0.855 * (ureg.kg / ureg.sec),
            'speed_cruise': 833 * ureg.kph,
            'tsfc_cruise': 15 * (ureg.mg / (ureg.N * ureg.s)),
            'lift_to_drag': 17,
            'dict_climb_segments_origin_to_destination': climb_segments,
            'dict_descent_segments_origin_to_destination': descent_segments,
            'R_cruise_origin_to_destination': 2000 * ureg.km,
            'time_taxi': 26 * ureg.min,
        },
    }

    def _make_case(r_cruise):
        if r_cruise not in cases:
            raise ValueError(f"No expected output defined for R_cruise={r_cruise}")
        input_data = cases[r_cruise]
        # No specific expected output dictionary since we're not checking values
        return input_data, None
    
    return _make_case, list(cases.keys())