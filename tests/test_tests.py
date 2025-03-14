import pytest

from jetfuelburn import ureg
from jetfuelburn.aux.tests import approx_with_units, approx_dict


def test_approx_with_units():
    assert approx_with_units(
        value_check=1.001*ureg.m,
        value_expected=1.0*ureg.m,
        rel=1e-3
    )
    assert not approx_with_units(
        value_check=1.001*ureg.m,
        value_expected=1.0*ureg.kg,
        rel=1e-3
    )


def test_approx_dict():
    assert approx_dict(
        dict_check={"a": 1.001, "b": 2.0001, "c": 3.0},
        dict_expected={"a": 1.0, "b": 2.0, "c": 3.0},
        rel=1e-3
    )
    assert approx_dict(
        dict_check={"a": 1.001*ureg.m, "b": 2.0001*ureg.K},
        dict_expected={"a": 1.0*ureg.m, "b": 2.0*ureg.K},
        rel=1e-3
    )
    assert not approx_dict(
        dict_check={"a": 1.001*ureg.m, "b": 2.0001*ureg.kg},
        dict_expected={"a": 1.0*ureg.m, "b": 2.0*ureg.t},
        rel=1e-3
    )
    assert not approx_dict(
        dict_check={"a": 9.1, "b": 2.0001, "c": 3.0},
        dict_expected={"a": 1.0, "b": 2.0, "c": 3.0},
        rel=1e-3
    )
    assert not approx_dict(
        dict_check={"a": 9.1, "b": 2.0001},
        dict_expected={"a": 1.0, "b": 2.0, "c": 3.0},
        rel=1e-3
    )

