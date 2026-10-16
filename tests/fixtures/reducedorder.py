import pytest
from jetfuelburn import ureg


@pytest.fixture(scope="module")
def fixture_aim2015_B787():
    """
    Fixture returning a factory function to generate test cases.

    The `cases` dictionary contains:
    - `key`: range [km]
    - `value`: expected value for calculated fuel burn [kg]

    Notes
    -----
    - We assume: "(...) 95 kg for a passenger with luggage and an average of 4500 kg hold freight." - P.97, Dray et al. (2019)
    - We further assume a 200km climb/descent distance.

    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)

    References
    ----------
    [Panel 6 in Figure 4 in Dray et al. (2019)](https://doi.org/10.1016/j.tranpol.2019.04.013)
    """
    base_data = {
        "acft_size_class": 6,
        "D_climb": 200 * ureg.km,
        "D_descent": 200 * ureg.km,
        "PL": (359 * 95 + 4500) * ureg.kg,
    }

    cases = {
        5000 * ureg.km: 25606 * ureg.kg,
        10000 * ureg.km: 53636 * ureg.kg,
        15000 * ureg.km: 84242 * ureg.kg,
    }

    def _make_case(d):
        if d not in cases:
            raise ValueError(f"No expected output defined for d={d}")
        input_data = base_data | {"D_cruise": d - (200 + 200) * ureg.km}
        expected_output = cases[d]
        return input_data, expected_output

    return _make_case, list(cases.keys())


@pytest.fixture(scope="module")
def fixture_seymour_B738():
    """
    Fixture returning a factory function to generate test cases.

    The `cases` dictionary contains:
    - `key`: great-circle distance [km]
    - `value`: expected value for calculated fuel burn [kg]

    Notes
    -----
    Expected values are computed with the published reduced-order model for the `B738`
    (Table M.7 of the Supplementary Information of Seymour et al. (2020)):
    fuel = 7.13e-5 * d^2 + 2.94 * d + 1275, where d is the great-circle distance in km.
    The quadratic term contributes 71.3 kg at 1000 km and 1782.5 kg at 5000 km.
    Both distances lie within the `B738` maximum range of 5803 km (Table L.6).

    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)

    References
    ----------
    [Table M.7 in the Supplementary Information of Seymour et al. (2020)](https://doi.org/10.1016/j.trd.2020.102528)
    """
    base_data = {
        "acft": "B738",
    }

    cases = {
        1000 * ureg.km: 4286.3 * ureg.kg,
        5000 * ureg.km: 17757.5 * ureg.kg,
    }

    def _make_case(r):
        if r not in cases:
            raise ValueError(f"No expected output defined for r={r}")
        input_data = base_data | {"R": r}
        expected_output = cases[r]
        return input_data, expected_output

    return _make_case, list(cases.keys())


@pytest.fixture(scope="module")
def fixture_yanto_B739():
    """
    Fixture returning a factory function to generate test cases.

    The `cases` dictionary contains:
    - `key`: range [km]
    - `value`: expected value for calculated fuel burn [kg]

    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)

    References
    ----------
    [Panel (b) of Figure 5 in Yanto et al. (2017)](https://doi.org/10.2514/6.2017-3338)
    """
    base_data = {
        "acft": "B739",
    }

    cases = {
        (4724 * ureg.km, 17918 * ureg.kg): 15807 * ureg.kg,
        (2943 * ureg.km, 7885 * ureg.kg): 8878 * ureg.kg,
    }

    def _make_case(r, pl):
        key = (r, pl)
        if key not in cases:
            raise ValueError(f"No expected output defined for r={r}, pl={pl}")
        input_data = base_data | {"R": r, "PL": pl}
        expected_output = cases[key]
        return input_data, expected_output

    return _make_case, list(cases.keys())


@pytest.fixture(scope="module")
def fixture_lee_B732():
    """
    Fixture returning a factory function to generate test cases.

    The `cases` dictionary contains:
    - `key`: range [km]
    - `value`: expected value for calculated fuel burn [kg]

    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)

    References
    ----------
    [Table 3 and Figure 6 in Lee et al. (2019)](https://doi.org/10.1016/j.trd.2019.102346)
    """
    base_data = {
        "acft": "B732",
        "W_E": 265825 * ureg.N,
        "W_MPLD": 156476 * ureg.N,
        "W_MTO": 513422 * ureg.N,
        "W_MF": 142365 * ureg.N,
        "S": 91.09 * ureg.m**2,
        "C_D0": 0.0214,
        "C_D2": 0.0462,
        "c": (2.131e-4) / ureg.s,
        "h": 9144 * ureg.m,
        "V": 807.65 * ureg.kph,
    }

    cases = {
        1500 * ureg.nmi: (26288 * ureg.lbs).to("kg"),
        2000 * ureg.nmi: (9500 * ureg.lbs).to("kg"),
    }

    def _make_case(d):
        if d not in cases:
            raise ValueError(f"No expected output defined for d={d}")
        input_data = base_data | {"d": d}
        expected_output = cases[d]
        return input_data, expected_output

    return _make_case, list(cases.keys())


@pytest.fixture(scope="module")
def fixture_eea_A320():
    """
    Fixture returning a factory function to generate test cases.

    The `cases` dictionary contains:
    - `key`: range [km]
    - `value`: expected value for calculated fuel burn [kg] ("total" segment only!)

    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)

    References
    ----------
    [EMEP/EEA air pollutant emission inventory guidebook - 2009, Part B, Section 1 (Energy), Subsection 1.A.3.a (`Aviation_annex.zip`)](https://www.eea.europa.eu/en/analysis/publications/emep-eea-emission-inventory-guidebook-2009)
    """
    base_data = {
        "acft": "A320",
    }

    cases = {
        1000 * ureg.nmi: 6027.22755694583 * ureg.kg,
        1300 * ureg.nmi: 7547.557937 * ureg.kg,
    }

    def _make_case(R):
        if R not in cases:
            raise ValueError(f"No expected output defined for R={R}")
        input_data = base_data | {"R": R}
        expected_output = cases[R]
        return input_data, expected_output

    return _make_case, list(cases.keys())


@pytest.fixture(scope="module")
def fixture_myclimate_standard():
    """
    Fixture returning a factory function to generate test cases for the myclimate "standard aircraft".

    The `cases` dictionary contains:
    - `key`: distance [km]
    - `value`: expected value for calculated fuel burn [kg]

    Notes
    -----
    Expected values are computed using the myclimate formula fuel = a * x^2 + b * x + c, where x is in km,
    with the coefficients of the "standard short-haul flight" (x < 1500 km) and the "standard long-haul flight"
    (x > 2500 km), linearly interpolated in between.
    Fuel burn includes both cruise and LTO phases.

    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)

    References
    ----------
    [myClimate Flight Emissions Calculator Calculation Principles](https://www.myclimate.org/en/information/about-myclimate/downloads/flight-emission-calculator/)
    """
    base_data = {
        "acft": "standard aircraft",
    }

    cases = {
        1000 * ureg.km: 4040 * ureg.kg,
        2000 * ureg.km: 9100 * ureg.kg,
        2500 * ureg.km: 13750 * ureg.kg,
    }

    def _make_case(x):
        if x not in cases:
            raise ValueError(f"No expected output defined for x={x}")
        input_data = base_data | {"x": x}
        expected_output = cases[x]
        return input_data, expected_output

    return _make_case, list(cases.keys())


@pytest.fixture(scope="module")
def fixture_myclimate_aircraft():
    """
    Fixture returning a factory function to generate test cases for the myclimate aircraft types.

    The `cases` dictionary contains:
    - `key`: (aircraft type, distance [km])
    - `value`: expected value for calculated fuel burn [kg]

    Notes
    -----
    Expected values are computed by hand as fuel = a * x^2 + b * x + c, with the coefficients
    of the parameter tables in section 11 ("Formula") of the myclimate Calculation Principles page:

    | Aircraft | a        | b     | c        |
    |----------|----------|-------|----------|
    | B737     | 0.00016  | 1.454 | 1531.722 |
    | A320     | 0.000032 | 2.588 | 1212.084 |
    | B777     | 0.00034  | 6.112 | 3403.041 |
    | A330     | 0.00034  | 4.384 | 2457.737 |

    Short-haul types are evaluated at 1000 km, long-haul types at 5000 km.

    References
    ----------
    [myClimate Flight Emissions Calculator Calculation Principles](https://www.myclimate.org/en/information/about-myclimate/downloads/flight-emission-calculator/)
    """
    cases = {
        ("B737", 1000 * ureg.km): 3145.722 * ureg.kg,
        ("A320", 1000 * ureg.km): 3832.084 * ureg.kg,
        ("B777", 5000 * ureg.km): 42463.041 * ureg.kg,
        ("A330", 5000 * ureg.km): 32877.737 * ureg.kg,
    }

    def _make_case(acft, x):
        if (acft, x) not in cases:
            raise ValueError(f"No expected output defined for acft={acft}, x={x}")
        input_data = {"acft": acft, "x": x}
        expected_output = cases[(acft, x)]
        return input_data, expected_output

    return _make_case, list(cases.keys())
