import pytest

import pint
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry

import sys
import os
module_path = os.path.abspath("/Users/michaelweinold/github/EcoPyLot")
if module_path not in sys.path:
    sys.path.append(module_path)

from .fixtures.breguet import breguet_range_fuel_calculation_data_1

from jetfuelburn.breguet import calculate_fuel_consumption_based_on_breguet_range_equation

def test_scalculate_fuel_consumption_based_on_breguet_range_equation(breguet_range_fuel_calculation_data_1):
    input_data, output_data = breguet_range_fuel_calculation_data_1
    fuel_mass = calculate_fuel_consumption_based_on_breguet_range_equation(
        R=input_data['R'],
        LD=input_data['LD'],
        m_after_cruise=input_data['m_after_cruise'],
        v_cruise=input_data['v_cruise'],
        TSFC_cruise=input_data['TSFC'],
    )
    assert fuel_mass.magnitude == pytest.approx(output_data.magnitude, rel=1e-2)
