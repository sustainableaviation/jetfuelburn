import pytest

import pint
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry

import sys
import os
module_path = os.path.abspath("/Users/michaelweinold/github/jetfuelburn")
if module_path not in sys.path:
    sys.path.append(module_path)

from jetfuelburn.aux.tests import approx_with_units

from .fixtures.reducedorder import (
    fixture_yanto_etal_B739_heavy,
    fixture_yanto_etal_B739_light,
)

from jetfuelburn.reducedorder import (
    yanto_etal,
)


@pytest.mark.parametrize(
    "fixture_name",
    ["fixture_yanto_etal_B739_heavy", "fixture_yanto_etal_B739_light"]
)
def test_calculate_atmospheric_conditions(request, fixture_name):
    fixture = request.getfixturevalue(fixture_name)
    input_data, output_data = fixture

    weight_fuel = yanto_etal.calculate_fuel_consumption(
        acft=input_data['acft'],
        R=input_data['R'],
        PL=input_data['PL']
    )

    assert approx_with_units(
        value_check=weight_fuel,
        value_expected=output_data,
        rel=0.05
    )
