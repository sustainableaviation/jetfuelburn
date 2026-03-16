import pytest
import os
import tempfile
import csv
import pandas as pd
import plotly.graph_objects as go
from jetfuelburn.utility.mapping import plot_ofp_2d, plot_ofp_1d


class TestMapping:

    @pytest.fixture
    def sample_csv(self):
        """Create a temporary CSV file with two valid rows and two invalid rows."""
        content = [
            ["waypoint", "lat", "lon", "custom_label"],
            ["ZRH", 47.4582, 8.5555, "Zurich"],
            ["SFO", 37.6188, -122.3751, "San Francisco"],
            ["Invalid", "not_a_float", 0.0, "Skip me"],
            ["Missing", 0.0, "", "Skip me too"],
        ]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            writer = csv.writer(f)
            writer.writerows(content)
            temp_path = f.name

        yield temp_path

        if os.path.exists(temp_path):
            os.remove(temp_path)

    @pytest.fixture
    def sample_csv_custom_cols(self):
        """Create a temporary CSV file using non-default lat/lon column names."""
        content = [
            ["waypoint", "latitude", "longitude"],
            ["ZRH", 47.4582, 8.5555],
            ["SFO", 37.6188, -122.3751],
        ]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            writer = csv.writer(f)
            writer.writerows(content)
            temp_path = f.name

        yield temp_path

        if os.path.exists(temp_path):
            os.remove(temp_path)

    def test_plot_ofp_2d_returns_figure(
        self,
        sample_csv,
    ):
        """Test that plot_ofp_2d returns a Plotly Figure."""
        fig = plot_ofp_2d(sample_csv)
        assert isinstance(fig, go.Figure)

    def test_plot_ofp_2d_trace_counts(
        self,
        sample_csv,
    ):
        """Test that the correct number of traces are added to the figure.

        With 2 valid rows (ZRH, SFO):
          1 trace for the path line
        + 1 trace for ZRH
        + 1 trace for SFO
        = 3 traces
        """
        fig = plot_ofp_2d(sample_csv)
        assert len(fig.data) == 3
        # Check that we have Scattermap traces
        assert all(isinstance(t, go.Scattermap) for t in fig.data)

    def test_plot_ofp_2d_custom_label(
        self,
        sample_csv,
    ):
        """Test that custom label_column is accepted and does not raise."""
        fig = plot_ofp_2d(sample_csv, label_col="custom_label")
        assert isinstance(fig, go.Figure)

    def test_plot_ofp_2d_custom_lat_lon_cols(
        self,
        sample_csv_custom_cols,
    ):
        """Test that lat_col and lon_col parameters are respected."""
        fig = plot_ofp_2d(
            sample_csv_custom_cols, lat_col="latitude", lon_col="longitude"
        )
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 3

    def test_plot_ofp_2d_empty_data(self):
        """Test plot_ofp_2d with a header-only CSV."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            writer = csv.writer(f)
            writer.writerow(["waypoint", "lat", "lon"])
            temp_path = f.name

        try:
            fig = plot_ofp_2d(temp_path)
            assert isinstance(fig, go.Figure)
            # Should have the line trace at least (even if empty)
            assert len(fig.data) >= 1
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_plot_ofp_2d_output_html(
        self,
        sample_csv,
    ):
        """Test that the figure is saved to HTML when output_html is provided."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_html = f.name

        try:
            plot_ofp_2d(sample_csv, output_html=output_html)
            assert os.path.exists(output_html)
            assert os.path.getsize(output_html) > 0
        finally:
            if os.path.exists(output_html):
                os.remove(output_html)

    def test_plot_ofp_2d_dataframe_input(self):
        """Test that plot_ofp_2d accepts a pandas DataFrame directly."""
        df = pd.DataFrame(
            {
                "waypoint": ["ZRH", "SFO"],
                "lat": [47.4582, 37.6188],
                "lon": [8.5555, -122.3751],
            }
        )
        fig = plot_ofp_2d(df)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 3

    def test_plot_ofp_1d_returns_figure(self):
        """Test that plot_ofp_1d returns a Plotly Figure."""
        df = pd.DataFrame(
            {
                "timestamp": [0, 10, 20],
                "alt": [0, 5000, 10000],
            }
        )
        fig = plot_ofp_1d(df)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Scatter)

    def test_plot_ofp_1d_with_labels(self):
        """Test that plot_ofp_1d correctly displays labels."""
        df = pd.DataFrame(
            {
                "timestamp": [0, 10, 20],
                "alt": [0, 5000, 10000],
                "waypoint": ["A", "B", "C"],
            }
        )
        fig = plot_ofp_1d(df, label_col="waypoint")
        assert isinstance(fig, go.Figure)
        assert "text" in fig.data[0].mode
        assert list(fig.data[0].text) == ["A", "B", "C"]
