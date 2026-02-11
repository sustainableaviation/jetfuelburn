import pytest

from .fixtures.allocation import (
    allocation_one_class,
    allocation_two_classes,
    allocation_all_classes,
)

from jetfuelburn.utility.allocation import footprint_allocation_by_area


class TestFootprintAllocationByArea:

    def test_footprint_allocation_by_area_input_validation(self):
        """Tests that invalid inputs raise ValueError."""
        with pytest.raises(ValueError, match="Fuel burn per flight must be >0."):
            footprint_allocation_by_area(
                fuel_per_flight=-1000,
                size_factor_eco=1,
                size_factor_premiumeco=0,
                size_factor_business=1.5,
                size_factor_first=0,
                seats_eco=154,
                seats_premiumeco=0,
                seats_business=24,
                seats_first=0,
                load_factor_eco=0.9,
                load_factor_premiumeco=0,
                load_factor_business=0.5,
                load_factor_first=0,
            )

    def test_invalid_load_factor(self):
        """Tests that invalid load factors raise ValueError."""
        with pytest.raises(
            ValueError, match="Load factor \\(economy class\\) must be between 0 and 1."
        ):
            footprint_allocation_by_area(
                fuel_per_flight=14000,
                size_factor_eco=1,
                size_factor_premiumeco=0,
                size_factor_business=1.5,
                size_factor_first=0,
                seats_eco=154,
                seats_premiumeco=0,
                seats_business=24,
                seats_first=0,
                load_factor_eco=1.1,
                load_factor_premiumeco=0,
                load_factor_business=0.5,
                load_factor_first=0,
            )

    def test_invalid_size_factor_eco(self):
        """Tests that an invalid size_factor_eco raises a ValueError."""
        with pytest.raises(
            ValueError,
            match="Economy class must have size factor 1 and at least one seat.",
        ):
            footprint_allocation_by_area(
                fuel_per_flight=14000,
                size_factor_eco=1.1,
                size_factor_premiumeco=0,
                size_factor_business=1.5,
                size_factor_first=0,
                seats_eco=154,
                seats_premiumeco=0,
                seats_business=24,
                seats_first=0,
                load_factor_eco=0.9,
                load_factor_premiumeco=0,
                load_factor_business=0.5,
                load_factor_first=0,
            )

    def test_zero_seats_eco(self):
        """Tests that zero seats in economy class raises a ValueError."""
        with pytest.raises(
            ValueError,
            match="Economy class must have size factor 1 and at least one seat.",
        ):
            footprint_allocation_by_area(
                fuel_per_flight=14000,
                size_factor_eco=1,
                size_factor_premiumeco=0,
                size_factor_business=1.5,
                size_factor_first=0,
                seats_eco=0,
                seats_premiumeco=0,
                seats_business=24,
                seats_first=0,
                load_factor_eco=0.9,
                load_factor_premiumeco=0,
                load_factor_business=0.5,
                load_factor_first=0,
            )

    @pytest.mark.parametrize(
        "fixture_name", [
            "allocation_one_class",
            "allocation_two_classes",
            "allocation_all_classes",
        ]
    )
    def test_footprint_allocation_by_area_consistency(self, request, fixture_name):
        fixture = request.getfixturevalue(fixture_name)
        input_data = fixture

        dict_calculated_fuel = footprint_allocation_by_area(
            fuel_per_flight=input_data["fuel_per_flight"],
            size_factor_eco=input_data["size_factor_eco"],
            size_factor_premiumeco=input_data["size_factor_premiumeco"],
            size_factor_business=input_data["size_factor_business"],
            size_factor_first=input_data["size_factor_first"],
            seats_eco=input_data["seats_eco"],
            seats_premiumeco=input_data["seats_premiumeco"],
            seats_business=input_data["seats_business"],
            seats_first=input_data["seats_first"],
            load_factor_eco=input_data["load_factor_eco"],
            load_factor_premiumeco=input_data["load_factor_premiumeco"],
            load_factor_business=input_data["load_factor_business"],
            load_factor_first=input_data["load_factor_first"],
        )

        assert (
            dict_calculated_fuel["fuel_eco"]
            * input_data["seats_eco"]
            * input_data["load_factor_eco"]
            + dict_calculated_fuel["fuel_premiumeco"]
            * input_data["seats_premiumeco"]
            * input_data["load_factor_premiumeco"]
            + dict_calculated_fuel["fuel_business"]
            * input_data["seats_business"]
            * input_data["load_factor_business"]
            + dict_calculated_fuel["fuel_first"]
            * input_data["seats_first"]
            * input_data["load_factor_first"]
        ) == pytest.approx(expected=input_data["fuel_per_flight"], rel=0.01)
