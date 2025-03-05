import pytest

import pint
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry


@pytest.fixture
def atmospheric_conditions_1():
    # Data from the "U.S. Standard Atmosphere, 1976" (https://ntrs.nasa.gov/api/citations/19770009539/downloads/19770009539.pdf)
    input_data = 0 * ureg.m
    output_data = (1.225*ureg.kg/ureg.m**3, ureg.Quantity(15, ureg.degC)) # P.53 (Table 1)
    return input_data, output_data


@pytest.fixture
def atmospheric_conditions_2():
    # Data from the "U.S. Standard Atmosphere, 1976" (https://ntrs.nasa.gov/api/citations/19770009539/downloads/19770009539.pdf)
    input_data = 11000 * ureg.m
    output_data = (0.36480*ureg.kg/ureg.m**3, ureg.Quantity(-56.5, ureg.degC)) # P.55 (Table 1)
    return input_data, output_data


@pytest.fixture
def atmospheric_conditions_3():
    # Data from the "U.S. Standard Atmosphere, 1976" (https://ntrs.nasa.gov/api/citations/19770009539/downloads/19770009539.pdf)
    input_data = 19000 * ureg.m
    output_data = (0.10307*ureg.kg/ureg.m**3, ureg.Quantity(-56.5, ureg.degC)) # P.60 (Table 1)
    return input_data, output_data


@pytest.fixture
def mach_speed_1():
    # Data from the E6B Mach Speed Calculator (https://e6bx.com/mach-speed/)
    input_data = {
        'mach_number': 0.6224,
        'altitude': 7000*ureg.m
    }
    output_data = 700*ureg.kph
    return input_data, output_data


@pytest.fixture
def mach_speed_2():
    # Data from the E6B Mach Speed Calculator (https://e6bx.com/mach-speed/)
    input_data = {
        'mach_number': 0.7527,
        'altitude': 11000*ureg.m
    }
    output_data = 800*ureg.kph
    return input_data, output_data


@pytest.fixture
def mach_speed_3():
    # Data from the E6B Mach Speed Calculator (https://e6bx.com/mach-speed/)
    input_data = {
        'mach_number': 0.8469,
        'altitude': 15000*ureg.m
    }
    output_data = 900*ureg.kph
    return input_data, output_data
