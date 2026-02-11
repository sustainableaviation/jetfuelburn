import pytest
from jetfuelburn.utility.geography import _atlas


class TestGeography:

    def test_get_airport_by_icao_valid(self):
        """Test that a specific airport is retrievable by ICAO code."""
        # We now access the singleton instance's internal method
        airport = _atlas._get_airport("OMDB", by="icao")

        assert airport is not None
        assert airport["iata"] == "DXB"
        assert airport["name"] == "Dubai International Airport"

        # Verify coordinates are floats
        assert isinstance(airport["latitude"], float)
        assert isinstance(airport["longitude"], float)
        assert airport["latitude"] == 25.2528

    def test_get_airport_by_iata_valid(self):
        """Test that a specific airport is retrievable by IATA code."""
        airport = _atlas._get_airport("AUH", by="iata")

        assert airport is not None
        # Verify cross-reference works
        assert airport["icao"] == "OMAA"

    def test_get_airport_by_name_valid(self):
        """Test that a specific airport is retrievable by full name."""
        target_name = "Al Ain International Airport"
        airport = _atlas._get_airport(target_name, by="name")

        assert airport is not None
        assert airport["icao"] == "OMAL"

    def test_field_renaming_and_persistence(self):
        """
        Test that the 'airport' CSV header is renamed to 'name',
        and that other keys (iata/icao) are preserved in the object.
        """
        airport = _atlas._get_airport("OMDB", by="icao")

        # 1. Verify the rename: 'airport' should be gone, 'name' should exist
        assert "airport" not in airport
        assert "name" in airport

        # 2. Verify persistence: Unlike the old function, the new class
        # keeps 'iata' and 'icao' keys in the row object so they can be
        # shared across indices.
        assert "iata" in airport
        assert "icao" in airport

    def test_lookup_returns_none_for_missing(self):
        """Test that looking up a non-existent airport returns None."""
        # The public function raises ValueError, but the internal _get_airport returns None
        assert _atlas._get_airport("ZZZZ", by="iata") is None
        assert _atlas._get_airport("NonExistentName", by="name") is None

    def test_error_handling_invalid_key(self):
        """Test that invalid 'by' parameters raise ValueError."""
        with pytest.raises(ValueError, match="Invalid identifier type"):
            _atlas._get_airport("OMDB", by="zipcode")

    def test_data_loaded_state(self):
        """Test that the atlas flags itself as loaded after a request."""
        # Ensure data is loaded
        _atlas._get_airport("JFK")
        assert _atlas._loaded is True

        # Verify internal indices are populated
        assert len(_atlas._iata_index) > 0
        assert len(_atlas._icao_index) > 0
        assert len(_atlas._name_index) > 0
