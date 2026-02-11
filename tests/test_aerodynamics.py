import pytest
from jetfuelburn import ureg
from jetfuelburn.utility.aerodynamics import (
    jsbsim_drag_polars,
    openap_drag_polars,
)


class TestJsbsimDragPolarsIntegration:
    """
    Integration tests for JSBSim drag polars.
    These tests run against the ACTUAL data.json file in the package.
    """

    def test_data_loading(self):
        """Verifies that the JSON data file is found and loaded, returning a non-empty list."""
        available = jsbsim_drag_polars.available_aircraft()
        assert isinstance(available, list)
        assert len(available) > 0, "No aircraft loaded from JSBSim data.json"

    def test_drag_calculation_sanity(self):
        """
        Picks the first available aircraft and ensures the drag calculation
        runs without error and returns a positive Force.
        """
        # Dynamically pick an aircraft that actually exists in the file
        acft = jsbsim_drag_polars.available_aircraft()[0]

        L = 50000 * ureg.newton
        M = 0.78
        h = 30000 * ureg.feet

        drag = jsbsim_drag_polars.calculate_drag(acft, L, M, h)

        assert drag.check("[force]")
        assert drag.magnitude > 0
        assert drag.units == ureg.newton or drag.units == ureg.force

    def test_lift_to_drag_sanity(self):
        """
        Verifies that L/D ratio is dimensionless and falls within a
        physically reasonable range (e.g., 5 to 30 for fixed-wing aircraft).
        """
        acft = jsbsim_drag_polars.available_aircraft()[0]

        L = 60000 * ureg.newton
        M = 0.75
        h = 32000 * ureg.feet

        l_d = jsbsim_drag_polars.calculate_lift_to_drag(acft, L, M, h)

        assert l_d.check("[]")  # Dimensionless
        # Sanity check: L/D for a jet should typically be between 5 and 25
        assert 1.0 < l_d.magnitude < 50.0

    def test_binder_function_integration(self):
        """Verifies the binder function works with real data."""
        acft = jsbsim_drag_polars.available_aircraft()[0]

        # Create the bound function
        calculate_for_acft = jsbsim_drag_polars.calculate_lift_to_drag_binder_function(
            acft=acft
        )

        # Execute it
        result = calculate_for_acft(L=50000 * ureg.newton, M=0.78, h=30000 * ureg.feet)

        assert result.check("[]")
        assert result.magnitude > 0

    def test_invalid_aircraft_lookup(self):
        """Ensures looking up a non-existent aircraft still raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            jsbsim_drag_polars.calculate_drag(
                "NON_EXISTENT_CRAFT_XYZ", 10000 * ureg.N, 0.5, 10000 * ureg.ft
            )


class TestOpenApDragPolarsIntegration:
    """
    Integration tests for OpenAP drag polars.
    These tests run against the ACTUAL data.csv file in the package.
    """

    def test_data_loading(self):
        """Verifies that the CSV data file is found and parsed."""
        available = openap_drag_polars.available_aircraft()
        assert isinstance(available, list)
        assert len(available) > 0, "No aircraft loaded from OpenAP data.csv"

    def test_parameter_retrieval(self):
        """Verifies we can retrieve basic parameters and they have correct units."""
        acft = openap_drag_polars.available_aircraft()[0]

        params = openap_drag_polars.get_basic_drag_parameters(acft)

        assert "S" in params
        assert "CD0" in params
        assert "K" in params

        # S must be an Area quantity
        assert params["S"].check("[area]")
        # CD0 and K should be floats (dimensionless coefficients)
        assert isinstance(params["CD0"], float)
        assert isinstance(params["K"], float)

    def test_drag_calculation_sanity(self):
        """
        Picks an aircraft and ensures the drag calculation returns a valid Force.
        """
        acft = openap_drag_polars.available_aircraft()[0]

        # Use typical values to ensure we don't hit edge cases (like stall)
        L = 40000 * ureg.newton
        M = 0.7
        h = 25000 * ureg.feet

        drag = openap_drag_polars.calculate_drag(acft, L, M, h)

        # The function explicitly returns .to('N') in the source code
        assert drag.units == ureg.newton
        assert drag.magnitude > 0

    def test_physics_behavior(self):
        """
        Verifies basic physics relationships hold true with the real data:
        Increasing Lift should increase Drag (due to induced drag).
        """
        acft = openap_drag_polars.available_aircraft()[0]
        M = 0.75
        h = 30000 * ureg.feet

        drag_low_lift = openap_drag_polars.calculate_drag(acft, 40000 * ureg.N, M, h)
        drag_high_lift = openap_drag_polars.calculate_drag(acft, 80000 * ureg.N, M, h)

        assert drag_high_lift > drag_low_lift

    def test_invalid_inputs(self):
        """Checks validation logic works (even with real data loaded)."""
        acft = openap_drag_polars.available_aircraft()[0]

        with pytest.raises(ValueError, match="Mach number"):
            openap_drag_polars.calculate_drag(
                acft, 10000 * ureg.N, -0.5, 10000 * ureg.ft
            )
