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
    fixture_aim2015_777_light_10k,
    fixture_aim2015_777_light_15k,
    fixture_seymour_a321_5500km,
    fixture_seymour_a321_1000km,
)

from jetfuelburn.reducedorder import (
    yanto_etal,
    aim2015,
    seymour_etal,
)


@pytest.mark.parametrize(
    "fixture_name",
    ["fixture_yanto_etal_B739_heavy", "fixture_yanto_etal_B739_light"]
)
def test_yanto_etal(request, fixture_name):
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


@pytest.mark.parametrize(
    "fixture_name",
    ["fixture_aim2015_777_light_10k", "fixture_aim2015_777_light_15k"]
)
def test_aim2015(request, fixture_name):
    fixture = request.getfixturevalue(fixture_name)
    input_data, output_data = fixture

    weight_fuel = aim2015(
        acft_size_class=input_data['acft_size_class'],
        D_climb=input_data['D_climb'],
        D_cruise=input_data['D_cruise'],
        D_descent=input_data['D_descent'],
        PL=input_data['PL']
    )
    assert approx_with_units(
        value_check=weight_fuel,
        value_expected=output_data,
        rel=0.075
    )


@pytest.mark.parametrize(
    "fixture_name",
    ["fixture_seymour_a321_1000km", "fixture_seymour_a321_5500km"]
)
def test_seymour_etal(request, fixture_name):
    fixture = request.getfixturevalue(fixture_name)
    input_data, output_data = fixture

    weight_fuel = seymour_etal.calculate_fuel(
        acft=input_data['acft'],
        R=input_data['R']
    )
    assert approx_with_units(
        value_check=weight_fuel,
        value_expected=output_data,
        rel=0.05
    )