import pytest

import pint
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry


@pytest.fixture
def fixture_yanto_etal_B739_heavy():
    # Panel (b) of Figure 5 in Yanto et al. (2017)
    input_data = {
        'acft':'B739',
        'R':4724*ureg.km,
        'PL':17918*ureg.kg,
    }
    output_data = 15807*ureg.kg
    return input_data, output_data


@pytest.fixture
def fixture_yanto_etal_B739_light():
    # Panel (b) of Figure 5 in Yanto et al. (2017)
    input_data = {
        'acft':'B739',
        'R':2943*ureg.km,
        'PL':7885*ureg.kg,
    }
    output_data = 8878*ureg.kg
    return input_data, output_data


@pytest.fixture
def fixture_aim2015_777_light_10k():
    # Figure 4 in Dray et al. (2019) https://doi.org/10.1016/j.tranpol.2019.04.013
    input_data = {
        'acft_size_class':8,
        'D_climb':300*ureg.km,
        'D_cruise':(10000-300-200)*ureg.km,
        'D_descent':200*ureg.km,
        'PL':4.5*ureg.metric_ton
    }
    output_data = 72000*ureg.kg
    return input_data, output_data


@pytest.fixture
def fixture_aim2015_777_light_15k():
    # Figure 4 in Dray et al. (2019) https://doi.org/10.1016/j.tranpol.2019.04.013
    input_data = {
        'acft_size_class':8,
        'D_climb':300*ureg.km,
        'D_cruise':(15000-300-200)*ureg.km,
        'D_descent':200*ureg.km,
        'PL':4.5*ureg.metric_ton
    }
    output_data = 121843*ureg.kg
    return input_data, output_data


@pytest.fixture
def fixture_seymour_a321_5500km():
    # Figure 1 in Reduced_Model_Shape_Exploration.ipynb
    input_data = {
        'acft':'B738',
        'R':5557*ureg.km,
    }
    output_data = 16728*ureg.kg
    return input_data, output_data


@pytest.fixture
def fixture_seymour_a321_1000km():
    # Figure 1 in Reduced_Model_Shape_Exploration.ipynb
    input_data = {
        'acft':'B738',
        'R':902*ureg.km,
    }
    output_data = 4008*ureg.kg
    return input_data, output_data


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

