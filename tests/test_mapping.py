import pytest
import os
import tempfile
import csv
import ipyleaflet
from jetfuelburn.utility.mapping import plot_ofp


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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            writer = csv.writer(f)
            writer.writerows(content)
            temp_path = f.name

        yield temp_path

        if os.path.exists(temp_path):
            os.remove(temp_path)

    def test_plot_ofp_returns_map(self, sample_csv):
        """Test that plot_ofp returns an ipyleaflet Map."""
        m = plot_ofp(sample_csv)
        assert isinstance(m, ipyleaflet.Map)

    def test_plot_ofp_layer_counts(self, sample_csv):
        """Test that the correct number of layers are added to the map.

        With 2 valid rows (ZRH, SFO) every row is either start or end, so:
          1 TileLayer (base)
        + 1 Polyline
        + 1 Marker  (ZRH – start endpoint)
        + 1 Marker  (ZRH – label DivIcon)
        + 1 Marker  (SFO – end endpoint)
        + 1 Marker  (SFO – label DivIcon)
        = 6 layers
        """
        m = plot_ofp(sample_csv)

        layer_types = [type(layer).__name__ for layer in m.layers]
        print(f"Layers found: {layer_types}")

        assert any(isinstance(l, ipyleaflet.Polyline) for l in m.layers)
        assert any(isinstance(l, ipyleaflet.Marker) for l in m.layers)
        assert not any(isinstance(l, ipyleaflet.CircleMarker) for l in m.layers)
        assert len(m.layers) == 6

    def test_plot_ofp_three_rows(self):
        """Test layer counts when there is a middle waypoint (non-endpoint CircleMarker).

        With 3 valid rows:
          1 TileLayer
        + 1 Polyline
        + 1 Marker  (start endpoint)
        + 1 Marker  (start label)
        + 1 CircleMarker (middle)
        + 1 Marker  (middle label)
        + 1 Marker  (end endpoint)
        + 1 Marker  (end label)
        = 8 layers
        """
        content = [
            ["waypoint", "lat", "lon"],
            ["ZRH", 47.4582, 8.5555],
            ["MID", 50.0, -10.0],
            ["SFO", 37.6188, -122.3751],
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            writer = csv.writer(f)
            writer.writerows(content)
            temp_path = f.name

        try:
            m = plot_ofp(temp_path)
            assert any(isinstance(l, ipyleaflet.CircleMarker) for l in m.layers)
            assert len(m.layers) == 8
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_plot_ofp_custom_label(self, sample_csv):
        """Test that custom label_column is accepted and does not raise."""
        m = plot_ofp(sample_csv, label_column="custom_label")
        assert isinstance(m, ipyleaflet.Map)

    def test_plot_ofp_custom_lat_lon_cols(self, sample_csv_custom_cols):
        """Test that lat_col and lon_col parameters are respected."""
        m = plot_ofp(sample_csv_custom_cols, lat_col="latitude", lon_col="longitude")
        assert isinstance(m, ipyleaflet.Map)
        assert any(isinstance(l, ipyleaflet.Polyline) for l in m.layers)

    def test_plot_ofp_missing_lat_lon_cols(self, sample_csv):
        """Test that a CSV missing the specified lat/lon columns yields an empty-data map."""
        m = plot_ofp(sample_csv, lat_col="doesnt_exist", lon_col="also_missing")
        assert isinstance(m, ipyleaflet.Map)
        # Only TileLayer + empty Polyline – no markers
        assert len(m.layers) == 2

    def test_plot_ofp_empty_data(self):
        """Test plot_ofp with a header-only CSV (no data rows)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["waypoint", "lat", "lon"])
            temp_path = f.name

        try:
            m = plot_ofp(temp_path)
            assert isinstance(m, ipyleaflet.Map)
            # Base tile layer + empty Polyline
            assert len(m.layers) >= 1
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_plot_ofp_output_html(self, sample_csv):
        """Test that the map is saved to HTML when output_html is provided."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            output_html = f.name

        try:
            plot_ofp(sample_csv, output_html=output_html)
            assert os.path.exists(output_html)
            assert os.path.getsize(output_html) > 0
        finally:
            if os.path.exists(output_html):
                os.remove(output_html)

    def test_plot_ofp_url(self):
        """Test that plot_ofp delegates URL reading to polars.read_csv."""
        from unittest.mock import patch
        import polars as pl

        url = "https://example.com/test.csv"
        mock_df = pl.DataFrame({
            "waypoint": ["TEST"],
            "lat": [0.0],
            "lon": [0.0],
        })

        with patch("polars.read_csv", return_value=mock_df) as mock_read_csv:
            m = plot_ofp(url)
            mock_read_csv.assert_called_once_with(url)
            assert isinstance(m, ipyleaflet.Map)
            # 1 TileLayer + 1 Polyline + 1 endpoint Marker + 1 label Marker
            # (single row is both start and end → one Marker, not two)
            assert len(m.layers) == 4
