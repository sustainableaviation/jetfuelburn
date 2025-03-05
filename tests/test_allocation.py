import pytest

import sys
import os
module_path = os.path.abspath("/Users/michaelweinold/github/jetfuelburn")
if module_path not in sys.path:
    sys.path.append(module_path)

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

    tuple_fuel_per_seat = footprint_allocation_by_area(
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
        tuple_fuel_per_seat[0] * input_data['seats_eco'] +
        tuple_fuel_per_seat[1] * input_data['seats_premiumeco'] +
        tuple_fuel_per_seat[2] * input_data['seats_business'] +
        tuple_fuel_per_seat[3] * input_data['seats_first']
    ) == pytest.approx(input_data['fuel_per_flight'])