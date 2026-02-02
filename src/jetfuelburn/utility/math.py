import bisect

def _interpolate(
    x_val: float | int,
    x_list: list[float | int],
    y_list: list[float | int]
):
    r"""
    Given two sorted lists of x/y-pairs, performs one-dimensional linear interpolation for a given x-value:

    ![1d Interpolation](../_static/interpolation.svg)

    The interpolation is performed using the formula:

    $$
        y = y_{i-1} + \frac{y_i - y_{i-1}}{x_i - x_{i-1}} \cdot (x_{val} - x_{i-1})
    $$

    where

    $(x_{i-1}, y_{i-1})$ and $(x_i, y_i)$ are the known data points surrounding $x_{val}$.

    See Also
    --------
    [`bisect.bisect_right`](https://docs.python.org/3/library/bisect.html#bisect.bisect_right)

    Parameters
    ----------
    x_val : float | int
        The x value to interpolate for.
    x_list : list[float | int]
        The list of x values (must be sorted).
    y_list : list[float | int]
        The list of y values (corresponding to x_list).

    Returns
    -------
    float | int
        The interpolated y value.
    
    Raises
    ------
    ValueError
        If x_val is out of bounds of x_list.
    
    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn.utility.math import _interpolate
    _interpolate(
        x_val=5,
        x_list=[0, 10, 20],
        y_list=[0, 100, 200]
    )
    ```
    """
    if x_val <= x_list[0]:
        raise ValueError("x_val is out of bounds (less than minimum x_list value)")
    if x_val >= x_list[-1]:
        raise ValueError("x_val is out of bounds (greater than maximum x_list value)")

    i = bisect.bisect_right(x_list, x_val)
    x0, x1 = x_list[i-1], x_list[i]
    y0, y1 = y_list[i-1], y_list[i]

    """
    x0=x[i-1]   x_val        x1=x[i]                x[i+1]
    ----X---------X-------------X----------------------X----
    """
    
    k = (y1 - y0) / (x1 - x0)
    return y0 + k * (x_val - x0)