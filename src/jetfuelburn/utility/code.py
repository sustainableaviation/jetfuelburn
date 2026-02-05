# %%
from typing import Callable
import inspect

def _validate_function(
    func: Callable,
    required_params: set,
    expected_return_type: type | None = None
) -> None:
    r"""
    Given a callable (= a function), a set of required parameter names
    and an optional expected return type,
    checks if the function accepts all required parameters
    and (if provided) has the correct return type hint.

    For instance, for a function:

    ```python
    def my_func(a, b, c) -> int:
        return a + b + c
    ```

    the function can be validated as:

    ```python
    _validate_function(
    my_func, {'a', 'b', 'c'}, expected_return_type=int)
    ```

    Parameters
    ----------
    func : Callable
        The function to validate.
    required_params : set
        A set of parameter names that the function must accept.
    expected_return_type : type | None, optional
        If provided, the function return type hint must match this type.  Defaults to None.

    Raises
    ------
    ValueError
        If the function is missing required parameters or has an invalid return type.

    Returns
    -------
    None
    """
    sig = inspect.signature(func)
    func_params = sig.parameters.keys()
    missing = required_params - func_params
    if missing:
        raise ValueError(
            f"Function {func.__name__} missing parameters: {missing}. "
            f"Must accept: {required_params}"
        )
    
    if expected_return_type is not None:
        return_annotation = sig.return_annotation
        
        if return_annotation is inspect.Signature.empty:
            raise ValueError(f"Function '{func.__name__}' is missing a return type hint.")

        if return_annotation != expected_return_type:
            raise ValueError(
                f"Function '{func.__name__}' has invalid return type. "
                f"Expected: {expected_return_type.__name__}, "
                f"Got: {getattr(return_annotation, '__name__', return_annotation)}"
            )