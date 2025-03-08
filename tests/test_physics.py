import pytest

from jetfuelburn import ureg

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

    assert density.magnitude == pytest.approx(output_data['density'].magnitude, rel=1e-2)
    assert temperature.magnitude == pytest.approx(output_data['temperature'].magnitude, rel=1e-2)


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