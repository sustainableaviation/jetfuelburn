import pytest
from jetfuelburn import ureg
from jetfuelburn.utility.tests import approx_with_units
from jetfuelburn.statistics import usdot, aeromaps


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
        with pytest.raises(ValueError, match="Range and/or weight must not be negative."):
            usdot.calculate_fuel_consumption_per_weight(2024, "B787-800 Dreamliner", -100 * ureg.km, 1000 * ureg.kg)
            
        with pytest.raises(ValueError, match="Range and/or weight must not be negative."):
            usdot.calculate_fuel_consumption_per_weight(2024, "B787-800 Dreamliner", 100 * ureg.km, -1000 * ureg.kg)

        with pytest.raises(ValueError, match="No data available for year '1800'."):
            usdot.calculate_fuel_consumption_per_weight(1800, "B787-800 Dreamliner", 100 * ureg.km, 1000 * ureg.kg)

        with pytest.raises(ValueError, match="US DOT Aircraft Designator 'ufo' not found in model data."):
            usdot.calculate_fuel_consumption_per_weight(2024, "ufo", 100 * ureg.km, 1000 * ureg.kg)

    def test_fuel_consumption_per_seat_error_handling(self):
        """Test error handling for fuel consumption per seat."""
        with pytest.raises(ValueError, match="Range must not be negative."):
            usdot.calculate_fuel_consumption_per_seat(2024, "B787-800 Dreamliner", -100 * ureg.km)

        with pytest.raises(ValueError, match="No data available for year '1800'."):
            usdot.calculate_fuel_consumption_per_seat(1800, "B787-800 Dreamliner", 100 * ureg.km)

        with pytest.raises(ValueError, match="US DOT Aircraft Designator 'ufo' not found in model data."):
            usdot.calculate_fuel_consumption_per_seat(2024, "ufo", 100 * ureg.km)



class TestAeroMaps:

    def test_available_years_returns_data(self):
        """Test that years are loaded correctly."""
        years = aeromaps.available_years()
        assert len(years) > 0
        assert isinstance(years[0], int)
        assert 2005 in years

    def test_available_aircraft_returns_correct_types(self):
        """Test that aircraft types are loaded correctly for a valid year."""
        aircraft = aeromaps.available_aircraft(2005)
        expected_types = ["long_range", "medium_range", "short_range"]

        assert sorted(aircraft) == sorted(expected_types)

    def test_calculate_fuel_consumption_valid(self):
        """Test a standard calculation with valid inputs using custom comparison."""
        year = 2005
        acft = "medium_range"
        dist = 1000 * ureg("km")

        fuel_actual = aeromaps.calculate_fuel_consumption(acft, year, dist)

        expected_val = (
            1.289274036 * ureg("MJ/km") * 1000 * ureg("km") / 43.15 / ureg("MJ/kg")
        )

        assert approx_with_units(fuel_actual, expected_val, rel=1e-4)

    def test_unit_conversion_consistency(self):
        """Test that the function handles unit conversion (nmi to km) correctly."""
        year = 2005
        acft = "short_range"

        # Calculate with km
        res_km = aeromaps.calculate_fuel_consumption(acft, year, 1000 * ureg.km)

        # Calculate with nmi (approx 539.957 nmi = 1000 km)
        res_nmi = aeromaps.calculate_fuel_consumption(acft, year, 539.9568 * ureg.nmi)

        # Use your custom helper
        assert approx_with_units(res_km, res_nmi, rel=1e-3)

    def test_error_handling(self):
        """Test that all invalid inputs raise correct errors."""

        # 1. Negative Range
        with pytest.raises(ValueError, match="Range must not be negative"):
            aeromaps.calculate_fuel_consumption("short_range", 2005, -100 * ureg.km)

        # 2. Invalid Year
        with pytest.raises(ValueError, match="Year '1800' not found"):
            aeromaps.calculate_fuel_consumption("short_range", 1800, 500 * ureg.km)

        # 3. Invalid Aircraft
        with pytest.raises(ValueError, match="Aircraft type 'ufo' not found"):
            aeromaps.calculate_fuel_consumption("ufo", 2005, 500 * ureg.km)
