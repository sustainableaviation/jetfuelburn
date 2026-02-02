import pytest
from contextlib import nullcontext as does_not_raise

# Assuming the function is imported from your module
# from your_module import _interpolate

def test_interpolate_basic_logic():
    """
    Test basic interpolation logic on a simple positive slope.
    """
    
    
    x_list = [0, 10, 20]
    y_list = [0, 100, 200]
    
    # Test point exactly in the middle of first interval
    assert _interpolate(5, x_list, y_list) == 50.0
    
    # Test point in the middle of second interval
    assert _interpolate(15, x_list, y_list) == 150.0

@pytest.mark.parametrize(
    "x_val, x_list, y_list, expected",
    [
        # Case: Simple positive linear
        (2.5, [0, 5], [0, 10], 5.0),
        
        # Case: Negative slope
        (5, [0, 10], [100, 0], 50.0),
        
        # Case: Zero slope (flat line)
        (3, [1, 5], [10, 10], 10.0),
        
        # Case: Floating point precision inputs
        (0.5, [0.0, 1.0], [0.0, 3.3], 1.65),
        
        # Case: Point very close to lower bound (but valid > x[0])
        (0.0001, [0, 1], [0, 100], 0.01),
        
        # Case: Large numbers
        (1500, [1000, 2000], [5000, 7000], 6000),
    ]
)
def test_interpolate_calculation_accuracy(x_val, x_list, y_list, expected):
    """
    Verify calculation accuracy across different slopes and number types.
    """
    result = _interpolate(x_val, x_list, y_list)
    
    # Use approx for float comparison to avoid precision errors
    assert result == pytest.approx(expected)

@pytest.mark.parametrize(
    "x_val, x_list, y_list, error_match",
    [
        # Below Minimum
        (-1, [0, 10], [0, 100], "less than minimum"),
        
        # Exact Minimum (Code uses strict inequality < so this raises error)
        (0, [0, 10], [0, 100], "less than minimum"),
        
        # Above Maximum
        (11, [0, 10], [0, 100], "greater than maximum"),
        
        # Exact Maximum (Code uses strict inequality > so this raises error)
        (10, [0, 10], [0, 100], "greater than maximum"),
    ]
)
def test_interpolate_bounds_checks(x_val, x_list, y_list, error_match):
    """
    Ensure ValueError is raised when x_val is out of bounds 
    (or inclusive of bounds based on current implementation).
    """
    with pytest.raises(ValueError, match=error_match):
        _interpolate(x_val, x_list, y_list)

def test_interpolate_irregular_intervals():
    """
    Test that bisect correctly identifies intervals in non-uniformly spaced lists.
    """
    # Intervals are size 2, then size 10, then size 100
    x_list = [0, 2, 12, 112]
    y_list = [0, 2, 12, 112] # y = x
    
    # Check interpolation in the small interval
    assert _interpolate(1, x_list, y_list) == 1.0
    
    # Check interpolation in the large interval
    assert _interpolate(50, x_list, y_list) == 50.0