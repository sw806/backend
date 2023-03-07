from .edsfetcher import EDSFetcher
import pytest

class TestEDSFetcher:
    def test_fetch_data_bad_endpoint_causes_exception(self):
        # Arrange
        endpoint = 'https://invalid-endpoint'
        # Act/Assert
        with pytest.raises(Exception):
            EDSFetcher(endpoint).get_prices()