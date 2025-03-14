import pytest

from jetfuelburn.aux.tests import approx_with_units
from jetfuelburn.aux.physics import _calculate_atmospheric_conditions, _calculate_aircraft_velocity
from .fixtures.physics import atmospheric_case_fixture, mach_speed_case_fixture


def test_calculate_atmospheric_conditions(atmospheric_case_fixture):
    make_atmospheric_case, altitudes = atmospheric_case_fixture
    
    for altitude in altitudes:
        input_data, expected_output = make_atmospheric_case(altitude)
        calculated_output = _calculate_atmospheric_conditions(altitude=input_data)

        assert approx_with_units(
            value_check=calculated_output['density'],
            value_expected=expected_output['density'],
            rel=1e-2
        )


def test_calculate_aircraft_velocity(mach_speed_case_fixture):
    make_mach_speed_case, altitudes = mach_speed_case_fixture
    
    for altitude in altitudes:
        input_data, expected_output = make_mach_speed_case(altitude)
        output = _calculate_aircraft_velocity(
            mach_number=input_data['mach_number'],
            altitude=input_data['altitude']
        )
        
        assert approx_with_units(
            value_check=output,
            value_expected=expected_output,
            rel=1e-2
        )