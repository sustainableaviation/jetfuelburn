import pytest
from jetfuelburn import ureg
from jetfuelburn.utility.aerodynamics import poll_schumann_drag_polars
from jetfuelburn.utility.physics import (
    _calculate_dynamic_pressure,
    _calculate_airspeed_from_mach,
)


class TestPollSchumannDragPolars:
    """
    Tests for the Poll & Schumann (2025) drag polar.
    """

    def test_data_loading(self):
        """Test that all 67 aircraft types of Table 2 are loaded."""
        available = poll_schumann_drag_polars.list_aircraft()
        assert len(available) == 67
        assert {"A320", "B738", "B788", "A306", "B742", "B737"} <= set(available)

    def test_parameter_retrieval(self):
        """Test the low-speed polar of the A320 at the design-optimum Reynolds number (Table 2, Eqs. 31-38)."""
        params = poll_schumann_drag_polars.get_basic_drag_parameters("A320")
        assert params["S"].check("[area]")
        assert params["S"].to("m^2").magnitude == pytest.approx(122.4)
        assert params["CD0"] == pytest.approx(0.01859, abs=5e-5)
        assert params["K"] == pytest.approx(0.04314, abs=5e-5)

    def test_drag_calculation_sanity(self):
        """Test that the drag is a positive force in newtons."""
        drag = poll_schumann_drag_polars.calculate_drag(
            "A320", 60 * ureg.metric_ton * ureg.gravity, 0.78, 35000 * ureg.ft
        )
        assert drag.units == ureg.newton
        assert drag.magnitude > 0

    def test_lift_to_drag_sanity(self):
        """Test that every type has a plausible L/D at its design-optimum Mach number and lift coefficient at FL350."""
        h = 35000 * ureg.ft
        for acft in poll_schumann_drag_polars.list_aircraft():
            data = poll_schumann_drag_polars._aircraft_data[acft]
            q = _calculate_dynamic_pressure(
                speed=_calculate_airspeed_from_mach(data["M_DO"], h), altitude=h
            )
            S = poll_schumann_drag_polars.get_basic_drag_parameters(acft)["S"]
            l_d = poll_schumann_drag_polars.calculate_lift_to_drag(
                acft, data["CL_DO"] * q * S, data["M_DO"], h
            )
            assert l_d.check("[]")
            assert 14 < l_d.magnitude < 24, acft

    def test_unit_invariance(self):
        """Test that the same lift in different units gives the same drag."""
        h = 35000 * ureg.ft
        drag_n = poll_schumann_drag_polars.calculate_drag(
            "B788", 1788e3 * ureg.N, 0.85, h
        )
        drag_kn = poll_schumann_drag_polars.calculate_drag(
            "B788", 1788 * ureg.kN, 0.85, h
        )
        drag_lbf = poll_schumann_drag_polars.calculate_drag(
            "B788", (1788e3 * ureg.N).to(ureg.lbf), 0.85, h
        )
        assert drag_n.magnitude == pytest.approx(drag_kn.magnitude, rel=1e-12)
        assert drag_n.magnitude == pytest.approx(drag_lbf.magnitude, rel=1e-9)

    def test_physics_behavior(self):
        """Test that drag rises with lift, and with Mach number at a fixed lift coefficient."""
        h = 35000 * ureg.ft
        assert poll_schumann_drag_polars.calculate_drag(
            "A320", 80 * ureg.kN, 0.75, h
        ) > poll_schumann_drag_polars.calculate_drag("A320", 40 * ureg.kN, 0.75, h)

        lift = 60 * ureg.metric_ton * ureg.gravity

        def drag_per_lift(M):
            # the lift scales with M², so the lift coefficient stays fixed
            L = lift * (M / 0.78) ** 2
            return (
                poll_schumann_drag_polars.calculate_drag("A320", L, M, h) / L
            ).magnitude

        assert drag_per_lift(0.82) > drag_per_lift(0.78) > drag_per_lift(0.70)
        assert poll_schumann_drag_polars.calculate_drag(
            "A320", lift, 0.82, h, compressibility=False
        ) < poll_schumann_drag_polars.calculate_drag("A320", lift, 0.82, h)

    def test_reproduces_paper_figure_3(self):
        """
        Test against Fig. 3 of Poll & Schumann (2025): maximum L/D of an A320 at 58,800 kg
        over altitude at fixed Mach number (values read from the vector drawing of the PDF).
        """
        lift = 58800 * ureg.kg * ureg.gravity
        figure_3 = {
            0.65: 17.731,
            0.70: 17.539,
            0.75: 17.068,
            0.80: 16.162,
            0.82: 15.313,
        }
        for M, l_d_max in figure_3.items():
            best = max(
                poll_schumann_drag_polars.calculate_lift_to_drag(
                    "A320", lift, M, z * 25 * ureg.m
                ).magnitude
                for z in range(320, 560)
            )
            assert best == pytest.approx(l_d_max, rel=2e-3), M

    def test_binder_function_integration(self):
        """Test the partial returned by the binder function."""
        calculate_for_a320 = (
            poll_schumann_drag_polars.calculate_lift_to_drag_binder_function(
                acft="A320"
            )
        )
        l_d = calculate_for_a320(L=500 * ureg.kN, M=0.78, h=30000 * ureg.feet)
        assert l_d.check("[]")
        assert l_d.magnitude > 0
        assert (
            poll_schumann_drag_polars.calculate_lift_to_drag_binder_function(
                "A320", 500 * ureg.kN, 0.78, 30000 * ureg.feet
            )
            == l_d
        )

    def test_invalid_inputs(self):
        """Test that invalid inputs raise ValueError."""
        with pytest.raises(ValueError, match="not found"):
            poll_schumann_drag_polars.calculate_drag(
                "NON_EXISTENT_CRAFT_XYZ", 10000 * ureg.N, 0.5, 10000 * ureg.ft
            )
        with pytest.raises(ValueError, match="Mach number"):
            poll_schumann_drag_polars.calculate_drag(
                "A320", 10000 * ureg.N, -0.5, 10000 * ureg.ft
            )
        with pytest.raises(ValueError, match="Altitude"):
            poll_schumann_drag_polars.calculate_drag(
                "A320", 10000 * ureg.N, 0.5, -1 * ureg.ft
            )
        with pytest.raises(ValueError, match="Lift"):
            poll_schumann_drag_polars.calculate_drag(
                "A320", 0 * ureg.N, 0.5, 10000 * ureg.ft
            )
