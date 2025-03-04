# %%
import pytest

import sys
import os

module_path = os.path.abspath("/Users/michaelweinold/github/EcoPyLot")
if module_path not in sys.path:
    sys.path.append(module_path)

from .fixtures.route import (
    climb_segment_1,
    climb_segment_2,
    descent_segment_1,
    descent_segment_2,
    distance_and_time_based_on_alt_cruise_1,
    distance_and_time_based_on_alt_cruise_2,
    distance_and_time_based_on_distance_1,
    distance_and_time_based_on_distance_2,
    segments_for_function,
    top_of_climb,
    segments_for_dataframe
)

from ecopylot.route import (
    _generate_eurocontrol_climb_segments_complete,
    _generate_eurocontrol_descent_segments_complete,
    _compute_segments_distance_and_time_based_on_alt_cruise,
    _compute_segments_distance_and_time_based_on_route_distance,
    _segments_function,
    _compute_top_of_climb_distance,
    _generate_flight_profile_dataframe_from_segments
)

from ecopylot.tests import approx_with_units, approx_dict_of_dict

@pytest.mark.parametrize(
    "fixture_climb_segment_name",
    ["climb_segment_1", "climb_segment_2"]
)
def test_generate_eurocontrol_climb_segments_complete(request, fixture_climb_segment_name):
    input_data, output_data_expected = request.getfixturevalue(fixture_climb_segment_name)
    output_data_test = _generate_eurocontrol_climb_segments_complete(
        alt_ceiling_cruise=input_data['alt_ceiling_cruise'],
        rate_initial=input_data['rate_initial'],
        rate_5000_15000=input_data['rate_5000_15000'],
        rate_15000_24000=input_data['rate_15000_24000'],
        rate_mach=input_data['rate_mach'],
        v_ground_initial=input_data['v_ground_initial'],
        v_ground_5000_15000=input_data['v_ground_5000_15000'],
        v_ground_15000_24000=input_data['v_ground_15000_24000'],
        v_ground_mach=input_data['v_ground_mach'],
    )
    assert output_data_test == output_data_expected


@pytest.mark.parametrize(
    "fixture_descent_segment_name",
    ["descent_segment_1", "descent_segment_2"]
)
def test_generate_eurocontrol_descent_segments_complete(request, fixture_descent_segment_name):
    input_data, output_data_expected = request.getfixturevalue(fixture_descent_segment_name)
    output_data_test = _generate_eurocontrol_descent_segments_complete(
        alt_ceiling_cruise=input_data['alt_ceiling_cruise'],
        rate_cruise_to_24000=input_data['rate_cruise_to_24000'],
        rate_24000_to_10000=input_data['rate_24000_to_10000'],
        rate_approach=input_data['rate_approach'],
        v_cruise_to_24000=input_data['v_cruise_to_24000'],
        v_24000_to_10000=input_data['v_24000_to_10000'],
        v_approach=input_data['v_approach'],
    )
    assert output_data_test == output_data_expected

@pytest.mark.parametrize(
    "distance_and_time_based_on_alt_cruise",
    ["distance_and_time_based_on_alt_cruise_1", "distance_and_time_based_on_alt_cruise_2"]
)
def test_compute_segments_distance_and_time_based_on_alt_cruise(request, distance_and_time_based_on_alt_cruise):
    input_data, output_data_expected = request.getfixturevalue(distance_and_time_based_on_alt_cruise)
    output_data_test = _compute_segments_distance_and_time_based_on_alt_cruise(
        alt_cruise=input_data['alt_cruise'],
        segments=input_data['segments'],
    )
    assert output_data_test == output_data_expected


@pytest.mark.parametrize(
    "distance_and_time_based_on_distance",
    ["distance_and_time_based_on_distance_1", "distance_and_time_based_on_distance_2"]
)
def test_compute_segments_distance_and_time_based_on_route_distance(request, distance_and_time_based_on_distance):
    input_data, output_data_expected = request.getfixturevalue(distance_and_time_based_on_distance)
    output_data_test = _compute_segments_distance_and_time_based_on_route_distance(
        distance_traveled=input_data['distance_traveled'],
        segments=input_data['segments'],
    )
    assert approx_dict_of_dict(
        dict_of_dict_check=output_data_test,
        dict_of_dict_expected=output_data_expected,
        rel=0.02
    )


def test_segments_function(segments_for_function):
    input_data, output_data_expected = segments_for_function
    output_data_test = _segments_function(
        x=input_data['x'],
        segments=input_data['segments'],
    )
    assert output_data_test == output_data_expected

    
def test_top_of_climb(top_of_climb):
    input_data, output_data_expected = top_of_climb
    output_data_test = _compute_top_of_climb_distance(
        flight_distance=input_data['flight_distance'],
        climb_segments=input_data['climb_segments'],
        descent_segments=input_data['descent_segments'],
    )
    assert approx_with_units(
        value_check=output_data_test,
        value_expected=output_data_expected,
        abs=1
    )


def test_generate_flight_profile_dataframe_from_segments(segments_for_dataframe):
    input_data, output_data_expected = segments_for_dataframe
    output_data_test = _generate_flight_profile_dataframe_from_segments(
        distance_route=input_data['distance_route'],
        climb_segments=input_data['climb_segments'],
        descent_segments=input_data['descent_segments'],
    )
    for key in output_data_expected.keys():
        assert approx_with_units(
            value_check=output_data_test['Altitude'].iloc[int(key.magnitude)],
            value_expected=output_data_expected[key],
            rel=0.05,
        )