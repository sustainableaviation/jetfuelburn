import pytest
from jetfuelburn import ureg
import pint
from jetfuelburn.rangeequation import (
    calculate_fuel_consumption_breguet,
    calculate_fuel_consumption_breguet_improved
)
from jetfuelburn.utility.tests import approx_with_units

from .fixtures.rangeequation import breguet_range_fuel_calculation_data_1

class TestCalculateFuelConsumptionBreguet:
    
    def test_valid_input_units(self):
        """
        Test that the function accepts valid units and returns a mass in kg.
        """
        R = 3000 * ureg.kilometer
        LD = 18
        m_after = 60 * ureg.metric_ton
        V = 850 * ureg.kph
        TSFC = 0.6 * (ureg.lb / ureg.lbf / ureg.hour)

        result = calculate_fuel_consumption_breguet(R, LD, m_after, V, TSFC)
        
        assert result.check('[mass]')
        assert result.units == ureg.kg
        assert result.magnitude > 0

    def test_zero_range(self):
        """
        Test that zero range results in zero fuel consumption.
        """
        R = 0 * ureg.meter
        LD = 18
        m_after = 60000 * ureg.kg
        V = 200 * ureg.meter / ureg.second
        TSFC = 15 * (ureg.mg / ureg.N / ureg.second)

        result = calculate_fuel_consumption_breguet(R, LD, m_after, V, TSFC)
        
        assert result.magnitude == 0
        assert result.units == ureg.kg

    @pytest.mark.parametrize("invalid_input", [
        {"R": -100 * ureg.km, "msg": "Range must be greater than zero"},
        {"LD": 0.5, "msg": "Lift-to-Drag ratio must be greater than 1"},
        {"m_after_cruise": -50 * ureg.kg, "msg": "Mass after cruise must be greater than zero"},
        {"V": 0 * ureg.kph, "msg": "Cruise speed must be greater than zero"},
        {"TSFC": -5 * (ureg.mg / ureg.N / ureg.s), "msg": "Thrust Specific Fuel Consumption must be greater than zero"},
    ])
    def test_raises_value_error_on_invalid_magnitudes(self, invalid_input):
        """
        Test that specific value errors are raised for physically impossible inputs.
        """
        # Default valid values
        params = {
            "R": 2000 * ureg.nmi,
            "LD": 18,
            "m_after_cruise": 100 * ureg.metric_ton,
            "V": 800 * ureg.kph,
            "TSFC": 17 * (ureg.mg / ureg.N / ureg.s)
        }
        
        expected_msg = invalid_input.pop("msg")
        params.update(invalid_input)

        with pytest.raises(ValueError, match=expected_msg):
            calculate_fuel_consumption_breguet(**params)

    def test_raises_dimensionality_error(self):
        """
        Test that passing incorrect units (e.g., time instead of length) raises an error
        via the @ureg.check decorator.
        """
        with pytest.raises((ValueError, pint.errors.DimensionalityError)):
            calculate_fuel_consumption_breguet(
                R=500 * ureg.second, # Invalid: Time instead of Length
                LD=18,
                m_after_cruise=50000 * ureg.kg,
                V=200 * ureg.mps,
                TSFC=0.0001 * (ureg.sec / ureg.meter)
            )

    def test_calculate_fuel_consumption_breguet_from_fixture(self, breguet_range_fuel_calculation_data_1):
        """
        Test using a data fixture.
        """
        input_data, expected_data = breguet_range_fuel_calculation_data_1
        
        # Call the function using the keys from your fixture input_data
        calculated_data = calculate_fuel_consumption_breguet(
            R=input_data['R'],
            LD=input_data['LD'],
            m_after_cruise=input_data['m_after_cruise'],
            V=input_data['v_cruise'],  # Map fixture key 'v_cruise' to function arg 'V'
            TSFC=input_data['TSFC'],   # Map fixture key 'TSFC' to function arg 'TSFC'
        )
        
        assert approx_with_units(
            value_check=calculated_data,
            value_expected=expected_data,
            rel=1e-2
        )

class TestCalculateFuelConsumptionBreguetImproved:
    
    def test_valid_input_units(self):
        """
        Test that the improved function runs with standard inputs and extra improved parameters.
        """
        R = 2500 * ureg.nmi
        LD = 16
        m_after = 80000 * ureg.kg
        V = 450 * ureg.knot
        V_hw = 20 * ureg.knot
        TSFC = 0.55 * (ureg.lb / ureg.lbf / ureg.hour)
        
        result = calculate_fuel_consumption_breguet_improved(
            R, LD, m_after, V, V_hw, TSFC
        )
        
        assert result.check('[mass]')
        assert result.units == ureg.kg
        assert result.magnitude > 0

    def test_zero_range(self):
        """Test zero range returns zero mass."""
        result = calculate_fuel_consumption_breguet_improved(
            R=0 * ureg.km,
            LD=18,
            m_after_cruise=50000*ureg.kg,
            V=800*ureg.kph,
            V_headwind=0*ureg.kph,
            TSFC=17*(ureg.mg/ureg.N/ureg.s)
        )
        assert result.magnitude == 0

    def test_equivalence_to_standard_breguet(self):
        """
        Verify that the improved function returns the same result as the standard function
        when there is no wind, no lost fuel, and no recovered fuel.
        """
        # Shared Parameters
        R = 3000 * ureg.km
        LD = 19.5
        m_after = 120 * ureg.metric_ton
        V = 230 * ureg.meter / ureg.second
        TSFC = 16 * (ureg.mg / ureg.N / ureg.second)

        # 1. Standard Calculation
        val_standard = calculate_fuel_consumption_breguet(
            R=R, LD=LD, m_after_cruise=m_after, V=V, TSFC=TSFC
        )

        # 2. Improved Calculation (with effects nullified)
        val_improved = calculate_fuel_consumption_breguet_improved(
            R=R, 
            LD=LD, 
            m_after_cruise=m_after, 
            V=V,
            V_headwind=0 * ureg.mps,     # No Wind
            TSFC=TSFC,
            lost_fuel_fraction=0.0,      # No lost fuel
            recovered_fuel_fraction=0.0  # No recovered fuel
        )

        # 3. Assert Approximately Equal using helper
        assert approx_with_units(val_improved, val_standard)

    def test_raises_dimensionality_error(self):
        """
        Test that the improved function also checks dimensions via @ureg.check.
        """
        with pytest.raises((ValueError, pint.errors.DimensionalityError)):
            calculate_fuel_consumption_breguet_improved(
                R=2000 * ureg.nmi,
                LD=18,
                m_after_cruise=100 * ureg.kg,
                V=800 * ureg.kph,
                V_headwind=50 * ureg.gram, # Invalid: Mass instead of Speed
                TSFC=17 * (ureg.mg / ureg.N / ureg.s)
            )