import pytest

import pint
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry


@pytest.fixture
def breguet_range_fuel_calculation_data_1() -> tuple[dict, float]:
    """
    Generates testing data and correct result for the fuel consumption calculation.

    Note that in the textbook example from which the data is taken,
    the aircraft mass _includes_ the fuel:

    "A jet transport aircraft _with a mass of 100,000 kg_, a fuel mass of 30,000 kg (...)"

    This is because equation (5.71) used by the author uses the mass _before_ cruise,
    not the mass _after_ cruise. Note also that the variables of the author are 
    in units of weight [N], not mass [kg].

    See Also
    --------
    - [Example 5.6 in Sadraey (2023)](https://doi.org/10.1201/9781003279068)

    Returns
    -------
    tuple[dict, float]
        A tuple containing the input data and the correct result for the fuel consumption calculation.
    """
    g = 9.81 * (ureg.m / ureg.s**2) # acceleration due to gravity

    input_data = {
        'LD': 15.4 * ureg.dimensionless,
        'TSFC': ((0.8 * ureg.N / g) / ureg.h) / (1 * ureg.N), # .to('(g/s)/kN') for sanity check
        'm_after_cruise': 70000 * ureg.kg, # nota bene, Sadraey assumes that 100t includes fuel
        'v_cruise': 603.4 * ureg.kph,
        'R': 4143 * ureg.km,
    }
    output_data = 30000 * ureg.kg
    return input_data, output_data
