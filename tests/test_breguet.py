import pytest

from jetfuelburn import ureg
from jetfuelburn.aux.tests import approx_with_units
from jetfuelburn.breguet import calculate_fuel_consumption_range_equation
from .fixtures.breguet import breguet_range_fuel_calculation_data_1


def test_scalculate_fuel_consumption_range_equation(breguet_range_fuel_calculation_data_1):
    input_data, expected_data = breguet_range_fuel_calculation_data_1
    calculated_data = calculate_fuel_consumption_range_equation(
        R=input_data['R'],
        LD=input_data['LD'],
        m_after_cruise=input_data['m_after_cruise'],
        v_cruise=input_data['v_cruise'],
        TSFC_cruise=input_data['TSFC'],
    )
    assert approx_with_units(
        value_check=calculated_data,
        value_expected=expected_data,
        rel=1e-2
    )
