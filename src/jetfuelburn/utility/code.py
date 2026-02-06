# %%
from jetfuelburn import ureg
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


def _normalize_physics_function_or_scalar(function_or_scalar: int | float | pint.Quantity | Callable) -> Callable:
        r"""
        Given a scalar or Callable, wraps scalars in a lambda function. 
        Callables are returned as-is. 

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

        Parameters
        ----------
        function_or_scalar: int | float | pint.Quantity | Callable
            A scalar value or a function that computes a physics parameter.

        Returns
        -------
        Callable
            A function that returns the scalar value or the original Callable.

        Raises
        ------
        TypeError
            If the input is neither a scalar nor a Callable.
        """
        if isinstance(function_or_scalar, (pint.Quantity, float, int)):
            return lambda *args, **kwargs: function_or_scalar
        
        elif callable(function_or_scalar):
            return function_or_scalar
            
        else:
            raise TypeError(f"Input must be Quantity, scalar, or Callable. Got {type(function_or_scalar)}")