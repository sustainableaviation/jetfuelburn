import pytest
from jetfuelburn import ureg


@pytest.fixture(scope="module")
def make_payload_range_case():
    """
    Fixture returning a factory function to generate test cases.

    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)

    References
    ----------
    [Figure 3-2-0-991-001-A01 in Airbus A350 Aircraft Characteristics Document](https://web.archive.org/web/20211129144142/https://www.airbus.com/sites/g/files/jlcbta136/files/2021-11/Airbus-Commercial-Aircraft-AC-A350-900-1000.pdf)
    """
    base_data = {
        "oew": 142.4 * ureg.metric_ton,
        "mtow": 280 * ureg.metric_ton,
        "range_point_A": 500 * ureg.nmi,
        "payload_point_B": 54 * ureg.metric_ton,
        "range_point_B": 5830 * ureg.nmi,
        "payload_point_C": 25 * ureg.metric_ton,
        "range_point_C": 8575 * ureg.nmi,
        "range_point_D": 9620 * ureg.nmi,
    }

    cases = {
        2000
        * ureg.nmi: {
            "mass_fuel": (220 - (142.4 + 54)) * ureg.metric_ton,
            "mass_payload": 54 * ureg.metric_ton,
        },
        7500
        * ureg.nmi: {
            "mass_fuel": (280 - 179.14) * ureg.metric_ton,
            "mass_payload": (179.14 - 142.4) * ureg.metric_ton,
        },
        9000
        * ureg.nmi: {
            "mass_fuel": (280 - (142.4 + 25)) * ureg.metric_ton,
            "mass_payload": (157 - 142.4) * ureg.metric_ton,
        },
    }

    def _make_case(d):
        if d not in cases:
            raise ValueError(f"No expected output defined for d={d}")
        input_data = base_data | {"d": d}
        expected_output = cases[d]
        return input_data, expected_output

    return _make_case, list(cases.keys())
