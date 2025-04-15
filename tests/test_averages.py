import pytest

from jetfuelburn.aux.tests import approx_with_units
from jetfuelburn.averages import (
    myclimate
)
    
from .fixtures.averages import (
    fixture_myclimate_standard
)

def test_myclimate_standard(fixture_myclimate_standard):
    make_case, params = fixture_myclimate_standard

    for x in params:
        input_data, expected_output = make_case(x)
        calculated_output = myclimate.calculate_fuel_consumption(
            acft='standard aircraft',
            x=input_data['x'],
        )
        assert approx_with_units(
            value_check=calculated_output,
            value_expected=expected_output.to('kg'),
            rel=0.075
        )