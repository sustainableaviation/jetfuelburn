import pytest
import os
import tempfile
import csv
from ipyleaflet import Map, Polyline, Marker, CircleMarker
from jetfuelburn.utility.mapping import plot_ofp

class TestMapping:

    @pytest.fixture
    def sample_csv(self):
        """Create a temporary CSV file for testing."""
        content = [
            ["waypoint", "lat", "lon", "custom_label"],
            ["ZRH", 47.4582, 8.5555, "Zurich"],
            ["SFO", 37.6188, -122.3751, "San Francisco"],
            ["Invalid", "not_a_float", 0.0, "Skip me"],
            ["Missing", 0.0, "", "Skip me too"]
        ]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerows(content)
            temp_path = f.name
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def test_plot_ofp_returns_map(self, sample_csv):
        """Test that plot_ofp returns an ipyleaflet Map."""
        m = plot_ofp(sample_csv)
        assert isinstance(m, Map)

    def test_plot_ofp_layer_counts(self, sample_csv):
        """Test that the correct number of layers are added to the map."""
        m = plot_ofp(sample_csv)
        
        # layers in ipyleaflet Map (current implementation):
        # 1. TileLayer (base)
        # 2. Polyline
        # 3. CircleMarker (ZRH)
        # 4. CircleMarker (SFO)
        
        layer_types = [type(layer) for layer in m.layers]
        print(f"Layers found: {layer_types}")
        
        assert any(isinstance(l, Polyline) for l in m.layers)
        assert any(isinstance(l, CircleMarker) for l in m.layers)
        # Markers were removed by user in Step 264
        assert not any(isinstance(l, Marker) for l in m.layers)
        
        assert len(m.layers) == 4

    def test_plot_ofp_custom_label(self, sample_csv):
        """Test that custom label column is used."""
        m = plot_ofp(sample_csv, label_column="custom_label")
        
        # Find CircleMarkers and check their names
        circle_markers = [layer for layer in m.layers if isinstance(layer, CircleMarker)]
        assert len(circle_markers) == 2
        
        names = [cm.name for cm in circle_markers]
        assert "Zurich" in names
        assert "San Francisco" in names

    def test_plot_ofp_empty_data(self):
        """Test plot_ofp with an empty CSV."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["waypoint", "lat", "lon"])
            temp_path = f.name
            
        try:
            m = plot_ofp(temp_path)
            assert isinstance(m, Map)
            # Base tile layer + Polyline (empty)
            assert len(m.layers) >= 1
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_plot_ofp_output_html(self, sample_csv):
        """Test that the map is saved to HTML if requested."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_html = f.name
            
        try:
            plot_ofp(sample_csv, output_html=output_html)
            assert os.path.exists(output_html)
            assert os.path.getsize(output_html) > 0
        finally:
            if os.path.exists(output_html):
                os.remove(output_html)

    def test_plot_ofp_url(self):
        """Test that plot_ofp handles URLs."""
        from unittest.mock import patch, MagicMock
        
        url = "https://example.com/test.csv"
        csv_content = "waypoint,lat,lon\nTEST,0.0,0.0\n"
        
        mock_response = MagicMock()
        mock_response.read.return_value = csv_content.encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        
        with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
            m = plot_ofp(url)
            mock_urlopen.assert_called_once_with(url)
            assert isinstance(m, Map)
            # 1 TileLayer + 1 Polyline + 1 CircleMarker = 3
            assert len(m.layers) == 3
