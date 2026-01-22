import pytest
from jetfuelburn.utility.geography import _get_airports_dict

class TestGeography:

    def test_get_airports_by_icao_valid(self):
        """Test that airports are correctly keyed by ICAO code (default behavior)."""
        airports = _get_airports_dict(by='icao')
        
        # Check a known sample (Dubai Intl)
        assert 'OMDB' in airports
        
        # Verify the structure of the value
        dxb = airports['OMDB']
        assert dxb['iata'] == 'DXB'
        assert dxb['airport'] == 'Dubai International Airport'
        
        # Verify coordinates are floats
        assert isinstance(dxb['latitude'], float)
        assert isinstance(dxb['longitude'], float)
        assert dxb['latitude'] == 25.2528

    def test_get_airports_by_iata_valid(self):
        """Test that airports are correctly keyed by IATA code."""
        airports = _get_airports_dict(by='iata')
        
        # Check a known sample (Abu Dhabi Intl)
        assert 'AUH' in airports
        
        # Verify cross-reference
        auh = airports['AUH']
        assert auh['icao'] == 'OMAA'

    def test_get_airports_by_name_valid(self):
        """Test that airports are correctly keyed by full name."""
        airports = _get_airports_dict(by='name')
        
        target = 'Al Ain International Airport'
        assert target in airports
        assert airports[target]['icao'] == 'OMAL'

    def test_key_redundancy_removed(self):
        """Test that the dictionary key is strictly removed from the value dictionary."""
        # When keying by ICAO, the 'icao' field should not exist in the sub-dictionary
        airports = _get_airports_dict(by='icao')
        sample = airports['OMDB']
        
        assert 'icao' not in sample
        assert 'iata' in sample
        assert 'airport' in sample

    def test_error_handling(self):
        """Test that invalid 'by' parameters raise the correct ValueError."""
        
        # 1. Invalid Key Parameter
        with pytest.raises(ValueError, match="Invalid key"):
            _get_airports_dict(by='zipcode')

        # 2. Empty String (if applicable to your validation logic)
        with pytest.raises(ValueError):
            _get_airports_dict(by='')

    def test_data_integrity(self):
        """Test that the dataset contains a reasonable amount of data."""
        airports = _get_airports_dict(by='icao')
        
        # Assuming the CSV is not empty
        assert len(airports) > 0