import pytest
from jetfuelburn import ureg

@pytest.fixture(scope="module")
def fixture_myclimate_standard():
    """
    Fixture returning a factory function to generate test cases for myclimate A320.

    The `cases` dictionary contains:
    - `key`: distance [km]
    - `value`: expected value for calculated fuel burn [kg]

    Notes
    -----
    Expected values are computed using the myclimate formula for A320:
    fuel = 0.00016 * x^2 + 1.454 * x + 1531.722, where x is in km.
    Fuel burn includes both cruise and LTO phases.
    Distances are limited to <= 2500 km for A320, as per the method's restrictions.

    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)

    xeferences
    ----------
    [myClimate Flight Emissions Calculator Calculation Principles](https://www.myclimate.org/en/information/about-myclimate/downloads/flight-emission-calculator/)
    """
    base_data = {
        'acft': 'A320',
    }

    cases = {
        1000 * ureg.km: 4040 * ureg.kg,
        2000 * ureg.km: 9100 * ureg.kg,
        2500 * ureg.km: 13750 * ureg.kg,
    }

    def _make_case(x):
        if x not in cases:
            raise ValueError(f"No expected output defined for x={x}")
        input_data = base_data | {'x': x}
        expected_output = cases[x]
        return input_data, expected_output

    return _make_case, list(cases.keys())