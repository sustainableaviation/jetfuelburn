import pytest

import pint
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry


@pytest.fixture
def fixture_yanto_etal_B739_heavy():
    input_data = {
        'acft':'B739',
        'R':4724*ureg.km,
        'PL':17918*ureg.kg,
    }
    output_data = 15807*ureg.kg
    return input_data, output_data


@pytest.fixture
def fixture_yanto_etal_B739_light():
    input_data = {
        'acft':'B739',
        'R':2943*ureg.km,
        'PL':7885*ureg.kg,
    }
    output_data = 8878*ureg.kg
    return input_data, output_data