import pytest

import pint
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry

import sys
import os
module_path = os.path.abspath("/Users/michaelweinold/github/jetfuelburn")
if module_path not in sys.path:
    sys.path.append(module_path)

from jetfuelburn.aux.tests import approx_with_units
from jetfuelburn.diagrams import calculate_fuel_consumption_based_on_payload_range

from .fixtures.diagrams import (
    range_between_A_and_B,
    range_between_B_and_C,
    range_between_C_and_D,
)

@pytest.mark.parametrize(
    "fixture_range_segment",
    ["range_between_A_and_B", "range_between_B_and_C", "range_between_C_and_D"]
)
def test_calculate_fuel_consumption_based_on_payload_range(request, fixture_range_segment):
    input_data, output_data_expected = request.getfixturevalue(fixture_range_segment)
    result = calculate_fuel_consumption_based_on_payload_range(
        d=input_data['d'],
        oew=input_data['oew'],
        mtow=input_data['mtow'],
        range_point_A=input_data['range_point_A'],
        payload_point_B=input_data['payload_point_B'],
        range_point_B=input_data['range_point_B'],
        payload_point_C=input_data['payload_point_C'],
        range_point_C=input_data['range_point_C'],
        range_point_D=input_data['range_point_D'],
    )
    assert approx_with_units(
        value_check=result[0],
        value_expected=output_data_expected['m_fuel'].to('kg'),
        rel=0.1
    )
    assert approx_with_units(
        value_check=result[1],
        value_expected=output_data_expected['m_payload'].to('kg'),
        rel=0.1
    )