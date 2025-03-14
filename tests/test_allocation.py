import pytest

from .fixtures.allocation import (
    allocation_two_classes,
    allocation_all_classes
)

from jetfuelburn.aux.allocation import footprint_allocation_by_area

@pytest.mark.parametrize(
    "fixture_name",
    ["allocation_two_classes", "allocation_all_classes"]
)
def test_footprint_allocation_by_area(request, fixture_name):
    fixture = request.getfixturevalue(fixture_name)
    input_data = fixture

    dict_calculated_fuel = footprint_allocation_by_area(
        fuel_per_flight=input_data['fuel_per_flight'],
        size_factor_eco=input_data['size_factor_eco'],
        size_factor_premiumeco=input_data['size_factor_premiumeco'],
        size_factor_business=input_data['size_factor_business'],
        size_factor_first=input_data['size_factor_first'],
        seats_eco=input_data['seats_eco'],
        seats_premiumeco=input_data['seats_premiumeco'],
        seats_business=input_data['seats_business'],
        seats_first=input_data['seats_first'],
        load_factor_eco=input_data['load_factor_eco'],
        load_factor_premiumeco=input_data['load_factor_premiumeco'],
        load_factor_business=input_data['load_factor_business'],
        load_factor_first=input_data['load_factor_first'],
    )

    assert (
        dict_calculated_fuel['fuel_eco'] * input_data['seats_eco'] * input_data['load_factor_eco'] +
        dict_calculated_fuel['fuel_premiumeco'] * input_data['seats_premiumeco'] * input_data['load_factor_premiumeco'] +
        dict_calculated_fuel['fuel_business'] * input_data['seats_business'] * input_data['load_factor_business'] +
        dict_calculated_fuel['fuel_first'] * input_data['seats_first'] * input_data['load_factor_first']
    ) == pytest.approx(
        expected = input_data['fuel_per_flight'],
        rel=0.01
    )