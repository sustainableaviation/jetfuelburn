import pytest
from jetfuelburn import ureg


@pytest.fixture(scope="module")
def fixture_aim2015_B787():
    """
    Fixture returning a factory function to generate test cases.

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
        'acft_size_class': 6,
        'D_climb': 200 * ureg.km,
        'D_descent': 200 * ureg.km,
        'PL': (359*95+4500) * ureg.kg,
    }

    def _make_case(d):
        input_data = base_data | {'D_cruise': d - (200+200) * ureg.km}
        if d==5000*ureg.km:
            expected_output = 25606 * ureg.kg
        elif d == 10000 * ureg.km:
            expected_output = 53636 * ureg.kg
        elif d == 15000 * ureg.km:
            expected_output = 84242 * ureg.kg
        else:
            raise ValueError(f"No expected output defined for d={d}")
        
        return input_data, expected_output
    
    return _make_case


@pytest.fixture(scope="module")
def fixture_seymour_B738():
    """
    Fixture returning a factory function to generate test cases.
    
    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)

    References
    ----------
    [Figure 1 in Jupyter Notebook `Reduced_Model_Shape_Exploration.ipynb`](https://github.com/kwdseymour/FEAT/blob/master/Reduced_Model_Shape_Exploration.ipynb)
    """
    base_data = {
        'acft': 'B738',
    }

    def _make_case(r):
        input_data = base_data | {'R': r}
        if r == 5557 * ureg.km:
            expected_output = 16728 * ureg.kg
        elif r == 902 * ureg.km:
            expected_output = 4008 * ureg.kg
        else:
            raise ValueError(f"No expected output defined for r={r}")
        return input_data, expected_output
    
    return _make_case


@pytest.fixture(scope="module")
def fixture_yanto_B739():
    """
    Fixture returning a factory function to generate test cases.
    
    See Also
    --------
    [Pytest Documentation "Factories as Fixtures"](https://docs.pytest.org/en/stable/how-to/fixtures.html#factories-as-fixtures)

    References
    ----------
    [Panel (b) of Figure 5 in Yanto et al. (2017)](https://doi.org/10.2514/6.2017-3338)
    """
    base_data = {
        'acft': 'B739',
    }

    def _make_case(r, pl):
        input_data = base_data | {'R': r, 'PL': pl}
        if r == 4724 * ureg.km and pl == 17918 * ureg.kg:
            expected_output = 15807 * ureg.kg
        elif r == 2943 * ureg.km and pl == 7885 * ureg.kg:
            expected_output = 8878 * ureg.kg
        else:
            raise ValueError(f"No expected output defined for r={r}, pl={pl}")
        return input_data, expected_output
    
    return _make_case


@pytest.fixture
def fixture_lee_B732_1500nmi():
    # Table 3 and Figure 6 in Lee et al. (2019) https://doi.org/10.1016/j.trd.2019.102346
    input_data = {
        'acft':'B732',
        'W_E': 265825*ureg.N,
        'W_MPLD': 156476*ureg.N,
        'W_MTO': 513422*ureg.N,
        'W_MF': 142365*ureg.N,
        'S': 91.09*ureg.m ** 2,
        'C_D0': 0.0214,
        'C_D2': 0.0462,
        'c': (2.131E-4)/ureg.s,
        'h': 9144*ureg.m,
        'V': 807.65*ureg.kph,
        'd': 1500*ureg.nmi
    }
    output_data = (26288*ureg.lbs).to('kg')
    return input_data, output_data


@pytest.fixture
def fixture_lee_B732_2000nmi():
    # Table 3 and Figure 6 in Lee et al. (2019) https://doi.org/10.1016/j.trd.2019.102346
    input_data = {
        'acft':'B732',
        'W_E': 265825*ureg.N,
        'W_MPLD': 156476*ureg.N,
        'W_MTO': 513422*ureg.N,
        'W_MF': 142365*ureg.N,
        'S': 91.09*ureg.m ** 2,
        'C_D0': 0.0214,
        'C_D2': 0.0462,
        'c': (2.131E-4)/ureg.s,
        'h': 9144*ureg.m,
        'V': 807.65*ureg.kph,
        'd': 2000*ureg.nmi
    }
    output_data = (9500*ureg.lbs).to('kg')
    return input_data, output_data

