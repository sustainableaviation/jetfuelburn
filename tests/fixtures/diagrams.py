import pytest

import pandas as pd
import pint
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry


@pytest.fixture
def range_between_A_and_B():
    input_data = {
        'd':2000*ureg.nmi,
        'oew':142.4*ureg.metric_ton,
        'mtow':280*ureg.metric_ton,
        'range_point_A':500*ureg.nmi,
        'payload_point_B':54*ureg.metric_ton,
        'range_point_B':5830*ureg.nmi,
        'payload_point_C':25*ureg.metric_ton,
        'range_point_C':8575*ureg.nmi,
        'range_point_D':9620*ureg.nmi,
    }
    expected_output = {
        'm_fuel': (220-(142.4+54))*ureg.metric_ton,
        'm_payload': 54*ureg.metric_ton,
    }
    return input_data, expected_output


@pytest.fixture
def range_between_B_and_C():
    input_data = {
        'd':7500*ureg.nmi,
        'oew':142.4*ureg.metric_ton,
        'mtow':280*ureg.metric_ton,
        'range_point_A':500*ureg.nmi,
        'payload_point_B':54*ureg.metric_ton,
        'range_point_B':5830*ureg.nmi,
        'payload_point_C':25*ureg.metric_ton,
        'range_point_C':8575*ureg.nmi,
        'range_point_D':9620*ureg.nmi,
    }
    expected_output = {
        'm_fuel': (280-179.14)*ureg.metric_ton,
        'm_payload': (179.14-142.4)*ureg.metric_ton,
    }
    return input_data, expected_output


@pytest.fixture
def range_between_C_and_D():
    input_data = {
        'd':9000*ureg.nmi,
        'oew':142.4*ureg.metric_ton,
        'mtow':280*ureg.metric_ton,
        'range_point_A':500*ureg.nmi,
        'payload_point_B':54*ureg.metric_ton,
        'range_point_B':5830*ureg.nmi,
        'payload_point_C':25*ureg.metric_ton,
        'range_point_C':8575*ureg.nmi,
        'range_point_D':9620*ureg.nmi,
    }
    expected_output = {
        'm_fuel': (280-(142.4+25))*ureg.metric_ton,
        'm_payload': (157-142.4)*ureg.metric_ton,
    }
    return input_data, expected_output