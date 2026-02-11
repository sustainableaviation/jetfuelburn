import pytest
from jetfuelburn import ureg
from jetfuelburn.utility.code import (
    _validate_physics_function_parameters,
    _normalize_physics_function_or_scalar,
)


class TestValidatePhysicsFunctionParameters:
    """Test suite for _validate_physics_function_parameters."""

    def test_exact_match(self):
        """Should pass when function signature matches required parameters exactly."""

        def dummy_func(altitude, speed):
            pass

        required = {"altitude", "speed"}
        # Should not raise
        _validate_physics_function_parameters(dummy_func, required)

    def test_superset_signature(self):
        """
        Should pass if the function accepts *more* parameters than required
        (the code checks `missing = required - func`, ignoring extras in func).
        """

        def dummy_func(altitude, speed, temperature):
            pass

        required = {"altitude", "speed"}
        # Should not raise because 'altitude' and 'speed' are present
        _validate_physics_function_parameters(dummy_func, required)

    def test_missing_parameter(self):
        """Should raise ValueError if a required parameter is missing from the function."""

        def dummy_func(altitude):
            pass

        required = {"altitude", "speed"}

        with pytest.raises(ValueError, match="missing parameters"):
            _validate_physics_function_parameters(dummy_func, required)

    def test_empty_requirements(self):
        """Should pass if there are no requirements, regardless of function signature."""

        def dummy_func(x):
            pass

        _validate_physics_function_parameters(dummy_func, set())


class TestNormalizePhysicsFunctionOrScalar:
    """Test suite for _normalize_physics_function_or_scalar."""

    def test_normalize_scalar_int(self):
        """Integers should be converted to a callable that ignores arguments."""
        normalized = _normalize_physics_function_or_scalar(42)

        assert callable(normalized)
        # Verify it ignores args and returns the constant
        assert normalized() == 42
        assert normalized(100, some_kwarg=True) == 42

    def test_normalize_scalar_float(self):
        """Floats should be converted to a callable."""
        val = 3.14
        normalized = _normalize_physics_function_or_scalar(val)

        assert callable(normalized)
        assert normalized(altitude=100) == val

    def test_normalize_pint_quantity(self):
        """Pint Quantities should be converted to a callable."""
        quantity = 500 * ureg.meter
        normalized = _normalize_physics_function_or_scalar(quantity)

        assert callable(normalized)
        assert normalized(anything="ignored") == quantity

    def test_callable_passthrough(self):
        """Callables should be returned as-is (identity check)."""

        def my_func(x):
            return x + 1

        normalized = _normalize_physics_function_or_scalar(my_func)

        # Should be the exact same function object
        assert normalized is my_func
        assert normalized(1) == 2

    def test_invalid_input_type(self):
        """Strings or other invalid types should raise TypeError."""
        with pytest.raises(
            TypeError, match="Input must be Quantity, scalar, or Callable"
        ):
            _normalize_physics_function_or_scalar("not a function or number")
