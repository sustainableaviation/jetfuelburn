import pytest

from jetfuelburn import ureg
from jetfuelburn.aux.tests import approx_with_units
from jetfuelburn.diagrams import calculate_fuel_consumption_based_on_payload_range
from .fixtures.diagrams import make_payload_range_case


@pytest.mark.parametrize(
    argnames="d",
    argvalues=[
        2000 * ureg.nmi,
        7500 * ureg.nmi,
        9000 * ureg.nmi,
    ],
    ids=["range_d_2000nmi", "range_d_7500nmi", "range_d_9000nmi"]
)
def test_calculate_fuel_consumption_based_on_payload_range(d, make_payload_range_case):
    input_data, expected_output = make_payload_range_case(d)
    calculated_output = calculate_fuel_consumption_based_on_payload_range(
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
        value_check=calculated_output['mass_fuel'],
        value_expected=expected_output['mass_fuel'].to('kg'),
        rel=0.1
    )
    assert approx_with_units(
        value_check=calculated_output['mass_payload'],
        value_expected=expected_output['mass_payload'].to('kg'),
        rel=0.1
    )