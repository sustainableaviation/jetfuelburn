import pytest
from jetfuelburn import ureg
from jetfuelburn.utility.tests import approx_with_units
from jetfuelburn.statistics import usdot


class TestUsdot:

    def test_available_years(self):
        """Test that available_years returns a list of integers."""
        years = usdot.available_years()
        assert isinstance(years, list)
        assert all(isinstance(y, int) for y in years)
        assert 2024 in years

    def test_available_aircraft(self):
        """Test that available_aircraft returns a list of strings for a valid year."""
        aircraft = usdot.available_aircraft(2024)
        assert isinstance(aircraft, list)
        assert all(isinstance(a, str) for a in aircraft)
        assert "B787-800 Dreamliner" in aircraft

    def test_calculate_fuel_consumption_per_weight_valid(self):
        """Test a standard calculation for fuel consumption per weight."""
        year = 2024
        acft = "B787-800 Dreamliner"
        R = 1000 * ureg.nmi
        W = 1000 * ureg.kg

        fuel = usdot.calculate_fuel_consumption_per_weight(year, acft, R, W)

        assert fuel.magnitude > 0
        assert fuel.units == ureg.kg

    def test_calculate_fuel_consumption_per_seat_valid(self):
        """Test a standard calculation for fuel consumption per seat."""
        year = 2024
        acft = "B787-800 Dreamliner"
        R = 1000 * ureg.nmi

        fuel = usdot.calculate_fuel_consumption_per_seat(year, acft, R)

        assert fuel.magnitude > 0
        assert fuel.units == ureg.kg

    def test_fuel_consumption_per_weight_error_handling(self):
        """Test error handling for fuel consumption per weight."""
        with pytest.raises(
            ValueError, match="Range and/or weight must not be negative."
        ):
            usdot.calculate_fuel_consumption_per_weight(
                2024, "B787-800 Dreamliner", -100 * ureg.km, 1000 * ureg.kg
            )

        with pytest.raises(
            ValueError, match="Range and/or weight must not be negative."
        ):
            usdot.calculate_fuel_consumption_per_weight(
                2024, "B787-800 Dreamliner", 100 * ureg.km, -1000 * ureg.kg
            )

        with pytest.raises(ValueError, match="No data available for year '1800'."):
            usdot.calculate_fuel_consumption_per_weight(
                1800, "B787-800 Dreamliner", 100 * ureg.km, 1000 * ureg.kg
            )

        with pytest.raises(
            ValueError,
            match="US DOT Aircraft Designator 'ufo' not found in model data.",
        ):
            usdot.calculate_fuel_consumption_per_weight(
                2024, "ufo", 100 * ureg.km, 1000 * ureg.kg
            )

    def test_fuel_consumption_per_seat_error_handling(self):
        """Test error handling for fuel consumption per seat."""
        with pytest.raises(ValueError, match="Range must not be negative."):
            usdot.calculate_fuel_consumption_per_seat(
                2024, "B787-800 Dreamliner", -100 * ureg.km
            )

        with pytest.raises(ValueError, match="No data available for year '1800'."):
            usdot.calculate_fuel_consumption_per_seat(
                1800, "B787-800 Dreamliner", 100 * ureg.km
            )

        with pytest.raises(
            ValueError,
            match="US DOT Aircraft Designator 'ufo' not found in model data.",
        ):
            usdot.calculate_fuel_consumption_per_seat(2024, "ufo", 100 * ureg.km)
