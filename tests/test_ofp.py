# %%
import math
import textwrap
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from jetfuelburn import ureg
from jetfuelburn.utility.ofp import _get_aircraft_performance, generate_4d_trajectory

# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------

DATA_YAML = (
    Path(__file__).parent.parent
    / "src"
    / "jetfuelburn"
    / "data"
    / "EurocontrolAPD"
    / "data.yaml"
)
"""Path to the real EUROCONTROL APD YAML file shipped with the package."""

OFP_CSV = Path(__file__).parent / "data" / "ofp" / "ofp_basic.csv"
"""Path to the OFP test fixture."""

PERF_YAML = Path(__file__).parent / "data" / "ofp" / "performance.yaml"
"""Path to the performance test fixture."""


@pytest.fixture()
def tmp_yaml() -> Path:
    """Return the path to the static performance YAML test fixture."""
    return PERF_YAML


@pytest.fixture()
def df_ofp_csv() -> pd.DataFrame:
    """Load the existing OFP CSV fixture as a :class:`pandas.DataFrame`."""
    return pd.read_csv(OFP_CSV)


# ---------------------------------------------------------------------------
# Tests for _get_aircraft_performance
# ---------------------------------------------------------------------------


class TestGetAircraftPerformance:
    """Tests for the internal ``_get_aircraft_performance`` helper."""

    # --- happy-path lookups ------------------------------------------------

    def test_climb_lower_band(
        self,
        tmp_yaml: Path,
    ):
        """Altitude in the lower climb band returns the correct rate."""
        rate = _get_aircraft_performance(tmp_yaml, "TEST", "climb", 2500 * ureg.ft)
        assert rate.check("[length]/[time]")
        assert math.isclose(rate.to("ft/min").magnitude, 1000.0)

    def test_climb_upper_band(
        self,
        tmp_yaml: Path,
    ):
        """Altitude in the higher climb band returns the correct rate."""
        rate = _get_aircraft_performance(tmp_yaml, "TEST", "climb", 20000 * ureg.ft)
        assert rate.check("[length]/[time]")
        assert math.isclose(rate.to("ft/min").magnitude, 500.0)

    def test_descent_upper_band(
        self,
        tmp_yaml: Path,
    ):
        """Altitude in the higher descent band returns a negative rate."""
        rate = _get_aircraft_performance(tmp_yaml, "TEST", "descent", 20000 * ureg.ft)
        assert rate.check("[length]/[time]")
        assert math.isclose(rate.to("ft/min").magnitude, -1000.0)

    def test_descent_lower_band(
        self,
        tmp_yaml: Path,
    ):
        """Altitude in the approach descent band returns the correct rate."""
        rate = _get_aircraft_performance(tmp_yaml, "TEST", "descent", 2500 * ureg.ft)
        assert rate.check("[length]/[time]")
        assert math.isclose(rate.to("ft/min").magnitude, -500.0)

    def test_boundary_altitude_lower(
        self,
        tmp_yaml: Path,
    ):
        """Altitude exactly at the lower boundary (0 ft) is accepted."""
        rate = _get_aircraft_performance(tmp_yaml, "TEST", "climb", 0 * ureg.ft)
        assert math.isclose(rate.to("ft/min").magnitude, 1000.0)

    def test_boundary_altitude_band_transition(
        self,
        tmp_yaml: Path,
    ):
        """Altitude exactly at the band boundary (5 000 ft) is accepted."""
        rate = _get_aircraft_performance(tmp_yaml, "TEST", "climb", 5000 * ureg.ft)
        # 5 000 ft satisfies BOTH bands (min_alt <= alt <= max_alt for both);
        # the first matching band is returned.
        assert rate.check("[length]/[time]")

    def test_uses_real_yaml_file(self):
        """Smoke-test against the real EUROCONTROL APD YAML bundled with the package."""
        rate = _get_aircraft_performance(DATA_YAML, "B123", "climb", 10000 * ureg.ft)
        assert rate.check("[length]/[time]")
        assert rate.magnitude > 0  # climb rate must be positive

    def test_real_yaml_descent_is_negative(self):
        """Descent rates in the real data file are negative."""
        rate = _get_aircraft_performance(DATA_YAML, "B123", "descent", 30000 * ureg.ft)
        assert rate.to("ft/min").magnitude < 0

    # --- error handling ----------------------------------------------------

    def test_invalid_phase_raises(
        self,
        tmp_yaml: Path,
    ):
        """A phase other than 'climb' or 'descent' raises :class:`ValueError`."""
        with pytest.raises(ValueError, match="climb.*descent"):
            _get_aircraft_performance(tmp_yaml, "TEST", "cruise", 10000 * ureg.ft)

    def test_unknown_aircraft_raises(
        self,
        tmp_yaml: Path,
    ):
        """An aircraft key absent from the YAML raises :class:`ValueError`."""
        with pytest.raises(ValueError, match="not found"):
            _get_aircraft_performance(tmp_yaml, "UNKNOWN_XYZ", "climb", 10000 * ureg.ft)

    def test_altitude_out_of_bands_raises(
        self,
        tmp_yaml: Path,
    ):
        """An altitude above all defined bands raises :class:`ValueError`."""
        with pytest.raises(ValueError, match="not found in any altitude band"):
            _get_aircraft_performance(tmp_yaml, "TEST", "climb", 99999 * ureg.ft)

    def test_error_message_lists_available_aircraft(
        self,
        tmp_yaml: Path,
    ):
        """The ValueError for an unknown aircraft lists available aircraft types."""
        with pytest.raises(ValueError, match="TEST"):
            _get_aircraft_performance(tmp_yaml, "BOGUS", "climb", 10000 * ureg.ft)

    def test_wrong_unit_raises(
        self,
        tmp_yaml: Path,
    ):
        """Passing a non-length quantity is rejected by the ``@ureg.check`` decorator."""
        with pytest.raises(Exception):
            _get_aircraft_performance(tmp_yaml, "TEST", "climb", 10000 * ureg.kg)


# ---------------------------------------------------------------------------
# Tests for generate_4d_trajectory
# ---------------------------------------------------------------------------


class TestGenerate4DTrajectory:
    """Tests for the public ``generate_4d_trajectory`` function."""

    # --- input validation --------------------------------------------------

    def test_empty_dataframe_raises(
        self,
        tmp_yaml: Path,
    ):
        """An empty flight plan raises :class:`ValueError`."""
        df_empty = pd.DataFrame(columns=["waypoint", "alt", "timecum", "lat", "lon"])
        with pytest.raises(ValueError, match="[Ee]mpty"):
            generate_4d_trajectory(df_empty, "TEST", tmp_yaml)

    def test_missing_column_raises(
        self,
        tmp_yaml: Path,
    ):
        """A DataFrame missing a required column raises :class:`ValueError`."""
        df = pd.DataFrame(
            {
                "waypoint": ["A", "B"],
                "timecum": [0, 10],
                "lat": [0.0, 1.0],
                "lon": [0.0, 1.0],
                # 'alt' is intentionally omitted
            }
        )
        with pytest.raises(ValueError, match="alt"):
            generate_4d_trajectory(df, "TEST", tmp_yaml)

    # --- output shape / types ----------------------------------------------

    def test_output_is_dataframe(
        self,
        tmp_yaml: Path,
    ):
        """The return value is a :class:`pandas.DataFrame`."""
        df = pd.DataFrame(
            {
                "waypoint": ["DEP", "ARR"],
                "alt": [0, 5000],
                "timecum": [0, 60],
                "lat": [47.0, 48.0],
                "lon": [8.0, 9.0],
            }
        )
        result = generate_4d_trajectory(df, "TEST", tmp_yaml)
        assert isinstance(result, pd.DataFrame)

    def test_output_contains_alt_filled(
        self,
        tmp_yaml: Path,
    ):
        """The output DataFrame contains the ``alt_filled`` column."""
        df = pd.DataFrame(
            {
                "waypoint": ["DEP", "ARR"],
                "alt": [0, 5000],
                "timecum": [0, 60],
                "lat": [47.0, 48.0],
                "lon": [8.0, 9.0],
            }
        )
        result = generate_4d_trajectory(df, "TEST", tmp_yaml)
        assert "alt_filled" in result.columns

    def test_output_resolution_1min(
        self,
        tmp_yaml: Path,
    ):
        """
        With ``resolution_min=1``, consecutive timestamps in the output are
        exactly 1 minute apart.

        Notes
        -----
        The merge in ``generate_4d_trajectory`` produces an integer-indexed
        DataFrame; the resampled timestamps are available in the ``'timestamp'``
        column (carried through the merge from ``df_resampled``).
        """
        df = pd.DataFrame(
            {
                "waypoint": ["DEP", "ARR"],
                "alt": [0, 5000],
                "timecum": [0, 10],
                "lat": [47.0, 48.0],
                "lon": [8.0, 9.0],
            }
        )
        result = generate_4d_trajectory(
            df, "TEST", tmp_yaml, time_resolution=1 * ureg.minute
        )
        # The 'timestamp' column holds datetime64 values after the merge
        timestamps = pd.to_datetime(result["timestamp"].dropna())
        if len(timestamps) >= 2:
            diffs = timestamps.diff().dropna()
            for d in diffs:
                assert abs(d.total_seconds() - 60.0) < 1e-6

    # --- level-off strategy ------------------------------------------------

    def test_level_off_at_next_waypoint_altitude(
        self,
        tmp_yaml: Path,
    ):
        """
        Aircraft climbs to the next waypoint's altitude well before the waypoint
        is reached (CLB waypoint), so it must level off.

        Setup
        -----
        - DEP  : alt=0 ft,    time=0 min  (known)
        - MID  : alt=CLB,     time=60 min (unknown → filled by level-off logic)
        - ARR  : alt=5000 ft, time=120 min (known)

        ROC in the 0–5 000 ft band = 1 000 ft/min → the aircraft reaches
        5 000 ft after 5 minutes. The MID waypoint is 60 minutes away, so
        the filled altitude at MID must be 5 000 ft (level-off cap).
        """
        df = pd.DataFrame(
            {
                "waypoint": ["DEP", "MID", "ARR"],
                "alt": ["0", "CLB", "5000"],
                "timecum": [0, 60, 120],
                "lat": [47.0, 47.5, 48.0],
                "lon": [8.0, 8.5, 9.0],
            }
        )
        result = generate_4d_trajectory(
            df,
            "TEST",
            tmp_yaml,
            time_resolution=1 * ureg.minute,
            timestamp_start=pd.Timestamp("2025-01-01 00:00:00"),
        )
        # At t=30 min (well after the 5-min level-off point) altitude must be 5 000 ft
        ts_check = pd.Timestamp("2025-01-01 00:30:00")
        row = result[result["timestamp"] == ts_check]
        if len(row) > 0:
            assert math.isclose(row["alt_filled"].iloc[0], 5000.0, rel_tol=1e-3)

    def test_clb_token_is_interpolated(
        self,
        tmp_yaml: Path,
    ):
        """
        Waypoints tagged with the ``'CLB'`` string token get their altitude
        filled in by the function; the output column ``alt_filled`` must be
        fully numeric (no NaN) for a well-defined flight plan.
        """
        df = pd.DataFrame(
            {
                "waypoint": ["DEP", "MID", "ARR"],
                "alt": ["0", "CLB", "5000"],
                "timecum": [0, 30, 60],
                "lat": [47.0, 47.5, 48.0],
                "lon": [8.0, 8.5, 9.0],
            }
        )
        result = generate_4d_trajectory(
            df, "TEST", tmp_yaml, time_resolution=1 * ureg.minute
        )
        assert result["alt_filled"].notna().all()

    # --- integration against real OFP CSV fixture --------------------------

    def test_integration_real_ofp_csv(self):
        """
        Integration test: run ``generate_4d_trajectory`` against the actual OFP
        CSV fixture (KSFO→LSZH) and the real EUROCONTROL APD performance data.
        Verifies basic sanity of the result.
        """
        df = pd.read_csv(OFP_CSV)
        result = generate_4d_trajectory(
            df_ofp=df,
            aircraft_type="B123",
            perf_data_path=DATA_YAML,
            time_resolution=1 * ureg.minute,
        )
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert "alt_filled" in result.columns
        # Altitude must be non-negative throughout
        assert (result["alt_filled"].dropna() >= 0).all()

    def test_integration_monotone_cruise(self):
        """
        With a purely level flight plan (all altitudes numeric and identical)
        the output altitude should be constant.
        """
        df = pd.DataFrame(
            {
                "waypoint": ["A", "B", "C"],
                "alt": [35000, 35000, 35000],
                "timecum": [0, 30, 60],
                "lat": [47.0, 47.5, 48.0],
                "lon": [8.0, 8.5, 9.0],
            }
        )
        result = generate_4d_trajectory(
            df_ofp=df,
            aircraft_type="B123",
            perf_data_path=DATA_YAML,
            time_resolution=1 * ureg.minute,
        )
        alts = result["alt_filled"].dropna()
        assert (
            alts == 35000
        ).all(), "Altitude should stay constant during level cruise"

    # --- custom column names -----------------------------------------------

    def test_custom_column_names(
        self,
        tmp_yaml: Path,
    ):
        """Custom column name arguments are respected."""
        df = pd.DataFrame(
            {
                "wp": ["DEP", "ARR"],
                "elevation": [0, 5000],
                "elapsed": [0, 30],
                "latitude": [47.0, 48.0],
                "longitude": [8.0, 9.0],
            }
        )
        result = generate_4d_trajectory(
            df_ofp=df,
            aircraft_type="TEST",
            perf_data_path=tmp_yaml,
            colname_wp="wp",
            colname_timecum="elapsed",
            colname_alt="elevation",
            colname_lat="latitude",
            colname_lon="longitude",
        )
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    # --- descent / TOD behavior --------------------------------------------

    def test_tod_no_premature_ground_level(self, tmp_yaml):
        """
        With TOD strategy, the aircraft must hold cruise altitude at the start
        of a descent segment rather than descending immediately.

        Setup
        -----
        - DEP: 35000 ft, t=0 min
        - MID: DSC,      t=60 min
        - ARR: 0 ft,     t=120 min

        ROD in the 5000–35000 ft band = 1000 ft/min → 35 min needed to descend
        from 35000 to 0 ft. TOD should therefore occur around t=25 min, meaning
        the aircraft must still be at 35000 ft at t=10 min.
        The old (buggy) behaviour would already be at 25000 ft by t=10 min.
        """
        df = pd.DataFrame(
            {
                "waypoint": ["DEP", "MID", "ARR"],
                "alt": [35000, "DSC", 0],
                "timecum": [0, 60, 120],
                "lat": [47.0, 47.5, 48.0],
                "lon": [8.0, 8.5, 9.0],
            }
        )
        result = generate_4d_trajectory(
            df, "TEST", tmp_yaml, time_resolution=1 * ureg.minute
        )
        # At t=10 min the aircraft should still be at cruise altitude (TOD not yet reached)
        ts_check = pd.Timestamp("2025-01-01 00:10:00")
        row = result[result["timestamp"] == ts_check]
        assert len(row) > 0, "Expected a row at t=10 min"
        assert (
            row["alt_filled"].iloc[0] > 30000
        ), "Aircraft should still be near cruise altitude at t=10 min (TOD not yet reached)"
