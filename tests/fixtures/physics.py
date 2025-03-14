import pytest
from jetfuelburn import ureg


@pytest.fixture(scope="module")
def atmospheric_case_fixture():
    cases = {
        0 * ureg.m: {'density': 1.225 * ureg.kg / ureg.m**3, 'temperature': ureg.Quantity(15, ureg.degC)},
        11000 * ureg.m: {'density': 0.36480 * ureg.kg / ureg.m**3, 'temperature': ureg.Quantity(-56.5, ureg.degC)},
        19000 * ureg.m: {'density': 0.10307 * ureg.kg / ureg.m**3, 'temperature': ureg.Quantity(-56.5, ureg.degC)},
    }
    
    def make_atmospheric_case(altitude):
        if altitude not in cases:
            raise ValueError(f"No expected output defined for altitude={altitude}")
        return altitude, cases[altitude]
    
    return make_atmospheric_case, list(cases.keys())


@pytest.fixture(scope="module")
def mach_speed_case_fixture():
    cases = {
        7000 * ureg.m: {'mach_number': 0.6224, 'speed': 700 * ureg.kph},
        11000 * ureg.m: {'mach_number': 0.7527, 'speed': 800 * ureg.kph},
        15000 * ureg.m: {'mach_number': 0.8469, 'speed': 900 * ureg.kph},
    }
    
    def make_mach_speed_case(altitude):
        if altitude not in cases:
            raise ValueError(f"No expected output defined for altitude={altitude}")
        case = cases[altitude]
        input_data = {'mach_number': case['mach_number'], 'altitude': altitude}
        expected_output = case['speed']
        return input_data, expected_output
    
    return make_mach_speed_case, list(cases.keys())