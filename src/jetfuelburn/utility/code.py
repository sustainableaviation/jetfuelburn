"""Helpers for function arguments and for deprecated names."""

import inspect
from typing import Callable
import pint


def _validate_physics_function_parameters(
    func: Callable,
    required_params: set[str],
) -> None:
    r"""
    Validates that a physics function has exactly the expected parameters.

    Parameters
    ----------
    func: Callable
        The physics function to validate.
    required_params: set[str]
        A set of required parameter names.

    Raises
    ------
    ValueError
        If the function's parameters do not match the expected names.
    """
    sig = inspect.signature(func)
    func_params = sig.parameters.keys()
    missing = required_params - func_params
    if missing:
        raise ValueError(
            f"Function {func.__name__} missing parameters: {missing}. "
            f"Must accept: {required_params}"
        )


def _normalize_physics_function_or_scalar(
    function_or_scalar: float | pint.Quantity | Callable,
) -> Callable:
    r"""
    Given a scalar or Callable, wraps scalars in a lambda function.
    Callables are returned as-is.

    Parameters
    ----------
    function_or_scalar : float | pint.Quantity | Callable
        A scalar value or a function that computes a physics parameter.

    Returns
    -------
    Callable
        A function that returns the scalar value or the original Callable.

    Raises
    ------
    TypeError
        If the input is neither a scalar nor a Callable.

    See Also
    --------
    [`jetfuelburn.rangeequation.IntegratedRangeCalculator`][]

    Notes
    -----
    For scalars, the resulting lambda function will accept any arguments and ignore them, returning the constant value.
    For instance, for:

    ```python
    const_func = _normalize_physics_function(42)
    ```

    Calling `const_func(x, y, z)` for any `x`, `y`, `z` will return `42`.
    """
    if isinstance(function_or_scalar, (pint.Quantity, float, int)):
        return lambda *args, **kwargs: function_or_scalar

    elif callable(function_or_scalar):
        return function_or_scalar

    else:
        raise TypeError(
            f"Input must be Quantity, scalar, or Callable. Got {type(function_or_scalar)}"
        )


def _deprecated_alias(func: Callable, old_name: str, new_name: str) -> Callable:
    r"""
    Wraps a function so that calling it under its old name raises a `DeprecationWarning`
    and then runs the function unchanged.

    Parameters
    ----------
    func : Callable
        The function under its new name.
    old_name : str
        The old name, as shown in the warning (e.g. `seymour_etal.calculate_fuel_consumption`).
    new_name : str
        The new name, as shown in the warning (e.g. `seymour_etal.calculate`).

    Returns
    -------
    Callable
        The wrapped function.
    """
    import functools
    import warnings

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"`{old_name}` is deprecated since jetfuelburn 4.0.0 and will be removed in 5.0.0. "
            f"Use `{new_name}` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return func(*args, **kwargs)

    return wrapper


def _add_deprecated_method_aliases(cls: type, aliases: dict[str, str]) -> None:
    r"""
    Adds deprecated aliases for renamed static methods to a class.

    Parameters
    ----------
    cls : type
        The class that holds the renamed methods.
    aliases : dict[str, str]
        Old method name mapped to new method name, e.g. `{"available_aircraft": "list_aircraft"}`.
    """
    for old, new in aliases.items():
        alias = _deprecated_alias(
            getattr(cls, new), f"{cls.__name__}.{old}", f"{cls.__name__}.{new}"
        )
        setattr(cls, old, staticmethod(alias))


def _deprecated_module_attribute(module: str, name: str, aliases: dict) -> object:
    r"""
    Resolves a removed module-level name to its replacement and raises a `DeprecationWarning`.
    Meant to be called from a module-level `__getattr__` (PEP 562).

    Parameters
    ----------
    module : str
        The module name (`__name__`).
    name : str
        The requested attribute name.
    aliases : dict
        Old name mapped to a tuple of (new name, replacement object)
        or (new name, replacement object, note appended to the warning).

    Raises
    ------
    AttributeError
        If the name is not a deprecated alias.
    """
    import warnings

    if name not in aliases:
        raise AttributeError(f"module {module!r} has no attribute {name!r}")
    new_name, replacement, *note = aliases[name]
    warnings.warn(
        f"`{module}.{name}` is deprecated since jetfuelburn 4.0.0 and will be removed in 5.0.0. "
        f"Use `{module}.{new_name}` instead." + "".join(f" {n}" for n in note),
        DeprecationWarning,
        stacklevel=3,
    )
    return replacement
