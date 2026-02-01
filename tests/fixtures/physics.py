import pytest
from jetfuelburn import ureg


@pytest.fixture(scope="module")
def atmospheric_case_fixture():
    """
    Fixture providing expected ISA atmospheric conditions (Density and Temperature).
    Data extracted directly from Table A.1 International Standard Atmosphere[cite: 3].
    """
    cases = {
        # Sea Level: Standard Day [cite: 4]
        0 * ureg.ft: {
            'density': 1.2250 * ureg.kg / ureg.m**3,
            'temperature': ureg.Quantity(15.00, ureg.degC)
        },
        # 10,000 ft (3,048 m): Mid-Troposphere [cite: 4]
        10000 * ureg.ft: {
            'density': 0.9046 * ureg.kg / ureg.m**3,
            'temperature': ureg.Quantity(-4.81, ureg.degC)
        },
        # 20,000 ft (6,096 m): Upper Troposphere [cite: 36]
        20000 * ureg.ft: {
            'density': 0.6527 * ureg.kg / ureg.m**3,
            'temperature': ureg.Quantity(-24.62, ureg.degC)
        },
        # 40,000 ft (12,192 m): Stratosphere (Isothermal region) [cite: 54]
        40000 * ureg.ft: {
            'density': 0.3016 * ureg.kg / ureg.m**3,
            'temperature': ureg.Quantity(-56.50, ureg.degC)
        },
    }
    
    def make_atmospheric_case(altitude):
        if altitude not in cases:
            raise ValueError(f"No expected output defined for altitude={altitude}")
        return altitude, cases[altitude]
    
    return make_atmospheric_case, list(cases.keys())


@pytest.fixture(scope="module")
def mach_speed_case_fixture():
    """
    Fixture providing expected True Airspeed (TAS) for given Mach numbers.
    Calculated using Speed of Sound (a) data from Table A.1[cite: 3].
    """
    cases = {
        # 10,000 ft: a = 638.3 kt [cite: 4]
        10000 * ureg.ft: {
            'mach_number': 1.0, 
            'speed': 638.3 * ureg.knot
        },
        # 20,000 ft: a = 614.3 kt [cite: 36]
        # Test arbitrary Mach 0.8 -> 0.8 * 614.3 = 491.44 kt
        20000 * ureg.ft: {
            'mach_number': 0.8, 
            'speed': 491.44 * ureg.knot 
        },
        # 40,000 ft: a = 573.6 kt [cite: 54]
        # Test arbitrary Mach 0.85 -> 0.85 * 573.6 = 487.56 kt
        40000 * ureg.ft: {
            'mach_number': 0.85, 
            'speed': 487.56 * ureg.knot
        },
    }
    
    def make_mach_speed_case(altitude):
        if altitude not in cases:
            raise ValueError(f"No expected output defined for altitude={altitude}")
        case = cases[altitude]
        input_data = {'mach_number': case['mach_number'], 'altitude': altitude}
        
        # Convert expected speed to kph to match function output
        expected_output = case['speed'].to(ureg.kph)
        
        return input_data, expected_output
    
    return make_mach_speed_case, list(cases.keys())