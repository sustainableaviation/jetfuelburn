import pytest

from jetfuelburn import ureg
from jetfuelburn.utility.tests import (
    approx_with_units,
    approx_dict,
    approx_dict_of_dict,
)


def test_approx_with_units():
    assert approx_with_units(
        value_check=1.001 * ureg.m, value_expected=1.0 * ureg.m, rel=1e-3
    )
    assert not approx_with_units(
        value_check=1.001 * ureg.m, value_expected=1.0 * ureg.kg, rel=1e-3
    )
    assert approx_with_units(
        value_check=1.09 * ureg.m, value_expected=1.0 * ureg.m, abs=0.1
    )
    assert not approx_with_units(
        value_check=1.2 * ureg.m, value_expected=1.0 * ureg.m, abs=0.1
    )


def test_approx_dict():
    assert approx_dict(
        dict_check={"a": 1.001, "b": 2.0001, "c": 3.0},
        dict_expected={"a": 1.0, "b": 2.0, "c": 3.0},
        rel=1e-3,
    )
    assert approx_dict(
        dict_check={"a": 1.001 * ureg.m, "b": 2.0001 * ureg.K},
        dict_expected={"a": 1.0 * ureg.m, "b": 2.0 * ureg.K},
        rel=1e-3,
    )
    assert not approx_dict(
        dict_check={"a": 1.001 * ureg.m, "b": 2.0001 * ureg.kg},
        dict_expected={"a": 1.0 * ureg.m, "b": 2.0 * ureg.t},
        rel=1e-3,
    )
    assert not approx_dict(
        dict_check={"a": 9.1, "b": 2.0001, "c": 3.0},
        dict_expected={"a": 1.0, "b": 2.0, "c": 3.0},
        rel=1e-3,
    )
    assert not approx_dict(
        dict_check={"a": 9.1, "b": 2.0001},
        dict_expected={"a": 1.0, "b": 2.0, "c": 3.0},
        rel=1e-3,
    )
    assert not approx_dict(
        dict_check={"a": 1},
        dict_expected={"a": 1.0},
        rel=1e-3,
    )
    assert approx_dict(
        dict_check={"a": 1.09},
        dict_expected={"a": 1.0},
        abs=0.1,
    )
    assert not approx_dict(
        dict_check={"a": 1.2},
        dict_expected={"a": 1.0},
        abs=0.1,
    )
    assert not approx_dict(
        dict_check={"a": 1.0, "b": 2.0, "d": 4.0},
        dict_expected={"a": 1.0, "b": 2.0, "c": 3.0},
        rel=1e-3,
    )


def test_approx_dict_of_dict():
    assert approx_dict_of_dict(
        dict_of_dict_check={"a": {"b": 1.001}},
        dict_of_dict_expected={"a": {"b": 1.0}},
        rel=1e-3,
    )
    assert not approx_dict_of_dict(
        dict_of_dict_check={"a": {"b": 1.1}},
        dict_of_dict_expected={"a": {"b": 1.0}},
        rel=1e-3,
    )
    assert not approx_dict_of_dict(
        dict_of_dict_check={"a": {"c": 1.001}},
        dict_of_dict_expected={"a": {"b": 1.0}},
        rel=1e-3,
    )
    assert approx_dict_of_dict(
        dict_of_dict_check={"a": {"b": 1.001 * ureg.m}},
        dict_of_dict_expected={"a": {"b": 1.0 * ureg.m}},
        rel=1e-3,
    )
    assert not approx_dict_of_dict(
        dict_of_dict_check={"a": {"b": 1.001 * ureg.kg}},
        dict_of_dict_expected={"a": {"b": 1.0 * ureg.m}},
        rel=1e-3,
    )
    assert approx_dict_of_dict(
        dict_of_dict_check={"a": {"b": 1.09}},
        dict_of_dict_expected={"a": {"b": 1.0}},
        abs=0.1,
    )
    assert not approx_dict_of_dict(
        dict_of_dict_check={"a": {"b": 1.2}},
        dict_of_dict_expected={"a": {"b": 1.0}},
        abs=0.1,
    )
