import pytest

import pint
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry

import sys
import os
module_path = os.path.abspath("/Users/michaelweinold/github/jetfuelburn")
if module_path not in sys.path:
    sys.path.append(module_path)

from .fixtures.physics import (
    atmospheric_conditions_1,
    atmospheric_conditions_2,
    atmospheric_conditions_3,
    mach_speed_1,
    mach_speed_2,
    mach_speed_3
)

from jetfuelburn.aux.physics import (
    _calculate_atmospheric_conditions,
    _calculate_aircraft_velocity
)


@pytest.mark.parametrize(
    "fixture_name",
    ["atmospheric_conditions_1", "atmospheric_conditions_2", "atmospheric_conditions_3"]
)
def test_calculate_atmospheric_conditions(request, fixture_name):
    fixture = request.getfixturevalue(fixture_name)
    input_data, output_data = fixture

    density, temperature = _calculate_atmospheric_conditions(altitude=input_data)

    assert density.magnitude == pytest.approx(output_data[0].magnitude, rel=1e-2)
    assert temperature.magnitude == pytest.approx(output_data[1].magnitude, rel=1e-2)


@pytest.mark.parametrize(
    "fixture_name",
    ["mach_speed_1", "mach_speed_2", "mach_speed_3"]
)
def test_calculate_aircraft_velocity(request, fixture_name):
    fixture = request.getfixturevalue(fixture_name)
    input_data, output_data = fixture

    velocity = _calculate_aircraft_velocity(
        mach_number=input_data['mach_number'],
        altitude=input_data['altitude']
    )

    assert velocity.magnitude == pytest.approx(output_data.magnitude, rel=1e-2)
    assert velocity.units == output_data.units