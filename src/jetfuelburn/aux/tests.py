from jetfuelburn import ureg
import pytest


def approx_with_units(
    value_check,
    value_expected,
    rel=None,
    abs=None
) -> bool:
    """
    Given two Pint quantities, check if the values are approximately equal.

    See Also
    --------
    [`pytest.approx`](https://docs.pytest.org/en/stable/reference/reference.html#pytest-approx)

    Parameters
    ----------
    value_check : ureg.Quantity
        Value to check.
    value_expected : ureg.Quantity
        Value to compare against.
    rel : _type_, optional
        Relative tolerance, by default None
    abs : _type_, optional
        Absolute tolerance, by default None

    Returns
    -------
    bool
        True if the values are approximately equal, False otherwise.
    """
    if not pytest.approx(value_check.magnitude, rel=rel, abs=abs) == value_expected.magnitude:
        return False
    if not value_check.units == value_expected.units:
        return False
    return True


def approx_dict(
    dict_check: dict,
    dict_expected: dict,
    rel=None,
    abs=None
) -> bool:
    """
    Given two dictionaries, check if the values in the first dictionary are approximately equal to the values in the second dictionary.

    Also checks if the [Pint](https://ureg.readthedocs.io/en/stable/) units of the values in the first dictionary are equal to the units of the values in the second dictionary.

    See Also
    --------
    [`pytest.approx`](https://docs.pytest.org/en/stable/reference/reference.html#pytest-approx)

    Parameters
    ----------
    dict_check : dict
        Dictionary to check.
    dict_expected : dict
        Dictionary to compare against.
    rel : _type_, optional
        Relative tolerance, by default None
    abs : _type_, optional
        Absolute tolerance, by default None

    Returns
    -------
    bool
        True if the values in the first dictionary are approximately equal to the values in the second dictionary, False otherwise.
    """
    for key in dict_expected.keys():
        if key not in dict_check:
            return False
        if type(dict_expected[key]) != type(dict_check[key]):
            return False
        if isinstance(dict_expected[key], ureg.Quantity) == True:
            if not pytest.approx(dict_check[key].magnitude, rel=rel, abs=abs) == dict_expected[key].magnitude:
                return False
            if not dict_check[key].units == dict_expected[key].units:
                return False
        elif isinstance(dict_expected[key], ureg.Quantity) == False:
            if not pytest.approx(dict_check[key], rel=rel, abs=abs) == dict_expected[key]:
                return False
        else:
            pass
    return True


def approx_dict_of_dict(
    dict_of_dict_check: dict,
    dict_of_dict_expected: dict,
    rel=None,
    abs=None
) -> bool:
    """
    Given two dictionaries of dictionaries, check if the values in the first dictionary of dictionaries are approximately equal to the values in the second dictionary of dictionaries.

    See Also
    --------
    [`pytest.approx`](https://docs.pytest.org/en/stable/reference/reference.html#pytest-approx)

    Parameters
    ----------
    dict_of_dict_check : dict
        Dictionary of dictionaries to check.
    dict_of_dict_expected : dict
        Dictionary of dictionaries to compare against.
    rel : _type_, optional
        Relative tolerance, by default None
    abs : _type_, optional
        Absolute tolerance, by default None

    Returns
    -------
    bool
        True if the values in the first dictionary of dictionaries are approximately equal to the values in the second dictionary of dictionaries, False otherwise.
    """
    for key in dict_of_dict_expected.keys():
        if key not in dict_of_dict_check:
            return False
        if not approx_dict(
            dict_check=dict_of_dict_check[key],
            dict_expected=dict_of_dict_expected[key],
            rel=rel,
            abs=abs
        ):
            return False
    return True
