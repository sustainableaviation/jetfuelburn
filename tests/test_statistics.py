import pytest
from jetfuelburn import ureg
from jetfuelburn.utility.tests import approx_with_units
from jetfuelburn.statistics import (
    usdot,
    aeromaps
)


def test_usdot():
    assert 2024 in usdot.available_years()
    assert 'B787-800 Dreamliner' in usdot.available_aircraft(2024)

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
        expected_types = ['long_range', 'medium_range', 'short_range']
        
        assert sorted(aircraft) == sorted(expected_types)

    def test_calculate_fuel_consumption_valid(self):
        """Test a standard calculation with valid inputs using custom comparison."""
        year = 2005
        acft = 'medium_range'
        dist = 1000 * ureg('km')
        
        fuel_actual = aeromaps.calculate_fuel_consumption(acft, year, dist)

        expected_val = 1.289274036 * ureg('MJ/km') * 1000 * ureg('km') / 43.15 / ureg('MJ/kg')

        assert approx_with_units(fuel_actual, expected_val, rel=1e-4)

    def test_unit_conversion_consistency(self):
        """Test that the function handles unit conversion (nmi to km) correctly."""
        year = 2005
        acft = 'short_range'
        
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
            aeromaps.calculate_fuel_consumption('short_range', 2005, -100 * ureg.km)

        # 2. Invalid Year
        with pytest.raises(ValueError, match="Year '1800' not found"):
            aeromaps.calculate_fuel_consumption('short_range', 1800, 500 * ureg.km)

        # 3. Invalid Aircraft
        with pytest.raises(ValueError, match="Aircraft type 'ufo' not found"):
            aeromaps.calculate_fuel_consumption('ufo', 2005, 500 * ureg.km)