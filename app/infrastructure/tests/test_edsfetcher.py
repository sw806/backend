from app.infrastructure.edsfetcher import EDSFetcher
import pytest

class TestEDSFetcher:
    def test_fetch_data_records_in_file_equals_number_in_request(self):
        # Arrange
        endpoint = 'https://api.energidataservice.dk/dataset/Elspotprices?limit=6'
        file_path = '/home/dremacs/github/backend/app/infrastructure/tests/test_data.json'
        # Act
        EDSFetcher(endpoint, file_path).fetch_data()
        with open(file_path, 'r') as f:
            data = f.read()
        # Assert
        no_of_records = (data.count("{") + data.count("}")) / 2
        assert no_of_records == 1

    def test_fetch_data_bad_endpoint_causes_exception(self):
        # Arrange
        endpoint = 'https://invalid-endpoint'
        file_path = '/home/dremacs/github/backend/app/infrastructure/tests/test_data.json'
        # Act/Assert
        with pytest.raises(Exception):
            EDSFetcher(endpoint, file_path).fetch_data()