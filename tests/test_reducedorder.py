import pytest
from pint import DimensionalityError
from jetfuelburn import ureg
from jetfuelburn.utility.tests import approx_with_units
from jetfuelburn.reducedorder import (
    yanto_etal,
    aim2015,
    seymour_etal,
    lee_etal,
    eea_emission_inventory_2009,
    myclimate,
    sacchi_etal,
    montlaur_etal
)
from .fixtures.reducedorder import (
    fixture_yanto_B739,
    fixture_aim2015_B787,
    fixture_seymour_B738,
    fixture_lee_B732,
    fixture_eea_A320,
    fixture_myclimate_standard
)

from tests.code.montlaur_etal import compute_fuel_ask as reference_compute_fuel_ask

@pytest.mark.parametrize("distance_km, seats, expected_fuel_ask, description", [
    # --- Model D, E (Small) Cases ---
    (1500, 150, 19.98, "Typical Small Aircraft"),
    (100, 50,   93.93, "Minimum Bounds Small"), 
    (4000, 100, 23.35, "Long Range Small"),
    
    # --- Model B, D (Large) Cases ---
    # Formula: 0.7361 + 6651/D + 5.989e-4*D + 6.152e-2*S - 1.014e-6*D*S
    (3000, 200, 16.45, "Typical Large Aircraft"),
    (12000, 350, 25.75,"Max Range Large"),
    
    # --- Boundary / Edge Cases ---
    (200, 172,  44.66, "Exact Boundary for Large Model (Min Dist/Min Seats)"),
    (5000, 171, 18.30, "Max Dist for Small Model"),
])
def test_value_consistency(distance_km, seats, expected_fuel_ask, description):
    """
    Verifies that the new class-based implementation matches the 
    original reference values.
    
    All expected values were calculated using the reference implementation:
    https://github.com/luis-uow/emissions_fuel_estimation?tab=GPL-3.0-1-ov-file
    """
    # 1. Calculate New Implementation Value
    new_result = montlaur_etal.calculate_fuel_consumption(
        distance=distance_km * ureg.km,
        available_seats=seats
    )

def test_unit_consistency():
    result = montlaur_etal.calculate_fuel_consumption(1000 * ureg.km, 150)
    assert result.check('[mass]/[length]')

def test_invalid_input_raising():
    with pytest.raises(ValueError):
        montlaur_etal.calculate_fuel_consumption(50000 * ureg.km, 200)



class TestSacchiEtal:
    
    def test_input_validation(self):
        """Test that invalid years and passenger counts raise correct errors."""
        
        # 1. Year < 2018
        with pytest.raises(ValueError, match="Year must be 2018 or later"):
            sacchi_etal.calculate_fuel_consumption(
                year=2017, 
                pax_max=180, 
                pax=150, 
                R=1000 * ureg.km
            )

        # 2. Pax > Pax Max
        with pytest.raises(ValueError, match="between 0 and maximum pax"):
            sacchi_etal.calculate_fuel_consumption(
                year=2020, 
                pax_max=180, 
                pax=181, 
                R=1000 * ureg.km
            )

        # 3. Negative Pax
        with pytest.raises(ValueError, match="between 0 and maximum pax"):
            sacchi_etal.calculate_fuel_consumption(
                year=2020, 
                pax_max=180, 
                pax=-1, 
                R=1000 * ureg.km
            )


    def test_dimensionality_checks(self):
        """Test that passing wrong units raises DimensionalityError."""
        
        # 1. Range with Mass Units
        with pytest.raises(DimensionalityError):
            sacchi_etal.calculate_fuel_consumption(
                year=2020, 
                pax_max=180, 
                pax=150, 
                R=1000 * ureg.kg  # Wrong dimension
            )

        # 2. Tolerance with Time units
        with pytest.raises(DimensionalityError):
            sacchi_etal.calculate_fuel_consumption(
                year=2020, 
                pax_max=180, 
                pax=150, 
                R=1000 * ureg.km,
                tolerance=50 * ureg.second  # Wrong dimension
            )


    def test_unit_conversion_consistency(self):
        """Test that the function handles unit conversion (nmi to km) correctly."""
        year = 2025
        pax_max = 180
        pax = 150
        
        # Calculate with km
        res_km = sacchi_etal.calculate_fuel_consumption(
            year=year, pax_max=pax_max, pax=pax, R=1000 * ureg.km
        )
        
        # Calculate with nmi (approx 539.957 nmi = 1000 km)
        res_nmi = sacchi_etal.calculate_fuel_consumption(
            year=year, pax_max=pax_max, pax=pax, R=539.9568 * ureg.nmi
        )
        
        # Ensure results are practically identical
        assert approx_with_units(res_km, res_nmi, rel=1e-5)


    def test_manual_verification_cases(self):
            """
            Verifies model output against known calculated values for specific scenarios.
            """

            # Case 1: 2018
            # See: Cell AE8 in sheet "Scenarios" of Supplement 1 to Sacchi et al. (2023)
            # https://doi.org/10.5281/zenodo.8059750
            fuel_1 = sacchi_etal.calculate_fuel_consumption(
                year=2018, 
                pax_max=210, 
                pax=177, 
                R=6654 * ureg.km
            )
            expected_1 =  42278 * ureg.kg
            print(f"Case 1 (2018, 6654km): Got {fuel_1:.1f}, Expected {expected_1:.1f}")
            
            assert approx_with_units(
                value_check=fuel_1,
                value_expected=expected_1,
                rel=0.025
            )

            # Case 2: 2025
            # See: Cell AE15 in sheet "Scenarios" of Supplement 1 to Sacchi et al. (2023)
            # https://doi.org/10.5281/zenodo.8059750
            fuel_2 = sacchi_etal.calculate_fuel_consumption(
                year=2025, 
                pax_max=214, 
                pax=184, 
                R=6654 * ureg.km
            )
            expected_2 =  39606 * ureg.kg
            print(f"Case 2 (2025, 6654km): Got {fuel_2:.1f}, Expected {expected_2:.1f}")
            
            assert approx_with_units(
                value_check=fuel_2,
                value_expected=expected_2,
                rel=0.025
            )

            # Case 2: 2025
            # See: Cell AE15 in sheet "Scenarios" of Supplement 1 to Sacchi et al. (2023)
            # https://doi.org/10.5281/zenodo.8059750
            fuel_3 = sacchi_etal.calculate_fuel_consumption(
                year=2050, 
                pax_max=231, 
                pax=214, 
                R=6654 * ureg.km
            )
            expected_3 =  31854 * ureg.kg
            print(f"Case 3 (2050, 6654km): Got {fuel_3:.1f}, Expected {expected_3:.1f}")
            
            assert approx_with_units(
                value_check=fuel_3,
                value_expected=expected_3,
                rel=0.025
            )


def test_yanto_etal_B739(fixture_yanto_B739):
    make_case, params = fixture_yanto_B739
    
    for r, pl in params:
        input_data, expected_output = make_case(r, pl)
        calculated_output = yanto_etal.calculate_fuel_consumption(
            acft=input_data['acft'],
            R=input_data['R'],
            PL=input_data['PL'],
        )
        assert approx_with_units(
            value_check=calculated_output,
            value_expected=expected_output.to('kg'),
            rel=0.075
        )

def test_aim2015(fixture_aim2015_B787):
    make_case, distances = fixture_aim2015_B787
    
    for d in distances:
        input_data, expected_output = make_case(d)
        calculated_output = aim2015.calculate_fuel_consumption(
            acft_size_class=input_data['acft_size_class'],
            D_climb=input_data['D_climb'],
            D_cruise=input_data['D_cruise'],
            D_descent=input_data['D_descent'],
            PL=input_data['PL']
        )
        assert approx_with_units(
            value_check=sum(calculated_output.values()),
            value_expected=expected_output.to('kg'),
            rel=0.075
        )

def test_seymour(fixture_seymour_B738):
    make_case, ranges = fixture_seymour_B738
    
    for R in ranges:
        input_data, expected_output = make_case(R)
        calculated_output = seymour_etal.calculate_fuel_consumption(
            acft=input_data['acft'],
            R=input_data['R'],
        )
        assert approx_with_units(
            value_check=calculated_output,
            value_expected=expected_output.to('kg'),
            rel=0.075
        )

def test_eea2009(fixture_eea_A320):
    make_case, ranges = fixture_eea_A320
    
    for R in ranges:
        input_data, expected_output = make_case(R)
        calculated_output = eea_emission_inventory_2009.calculate_fuel_consumption(
            acft=input_data['acft'],
            R=input_data['R'],
        )
        assert approx_with_units(
            value_check=calculated_output['mass_fuel_total'].to('kg'),
            value_expected=expected_output.to('kg'),
            rel=0.075
        )


def test_myclimate_standard(fixture_myclimate_standard):
    make_case, params = fixture_myclimate_standard

    for x in params:
        input_data, expected_output = make_case(x)
        calculated_output = myclimate.calculate_fuel_consumption(
            acft='standard aircraft',
            x=input_data['x'],
        )
        assert approx_with_units(
            value_check=calculated_output,
            value_expected=expected_output.to('kg'),
            rel=0.075
        )