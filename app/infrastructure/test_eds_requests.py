from typing import List, Dict, Any

import pytest
from .eds_requests import EdsRequests

class TestEdsRequests:
    def test_create_price_points_from_json_valid(self):
        # Arrange
        eds = EdsRequests()
        records: List[Dict[str, str]] = [
            { "HourDK": "2023-02-01T23:00:00", "SpotPriceDKK": "1" },
            { "HourDK": "2023-02-02T23:00:00", "SpotPriceDKK": "2" },
            { "HourDK": "2023-02-03T23:00:00", "SpotPriceDKK": "3" },
            { "HourDK": "2023-02-04T23:00:00", "SpotPriceDKK": "4" },
            { "HourDK": "2023-02-05T23:00:00", "SpotPriceDKK": "5" },
            { "HourDK": "2023-02-06T23:00:00", "SpotPriceDKK": "6" },
            { "HourDK": "2023-02-07T23:00:00", "SpotPriceDKK": "7" },
            { "HourDK": "2023-02-08T23:00:00", "SpotPriceDKK": "8" },
            { "HourDK": "2023-02-09T23:00:00", "SpotPriceDKK": "9" },
            { "HourDK": "2023-02-10T23:00:00", "SpotPriceDKK": "10" },
        ]

        # Act
        price_points = eds.create_price_points_from_json(records)

        # Assert
        assert len(price_points) == 10

    def test_create_price_points_from_json_valid_preserves_order(self):
        # Arrange
        eds = EdsRequests()
        records: List[Dict[str, str]] = [
            { "HourDK": "2023-02-01T23:00:00", "SpotPriceDKK": "1" },
            { "HourDK": "2023-02-02T23:00:00", "SpotPriceDKK": "2" },
            { "HourDK": "2023-02-03T23:00:00", "SpotPriceDKK": "3" },
            { "HourDK": "2023-02-04T23:00:00", "SpotPriceDKK": "4" },
            { "HourDK": "2023-02-05T23:00:00", "SpotPriceDKK": "5" },
            { "HourDK": "2023-02-06T23:00:00", "SpotPriceDKK": "6" },
            { "HourDK": "2023-02-07T23:00:00", "SpotPriceDKK": "7" },
            { "HourDK": "2023-02-08T23:00:00", "SpotPriceDKK": "8" },
            { "HourDK": "2023-02-09T23:00:00", "SpotPriceDKK": "9" },
            { "HourDK": "2023-02-10T23:00:00", "SpotPriceDKK": "10" },
        ]

        # Act
        price_points = eds.create_price_points_from_json(records)

        # Assert
        assert all([float(records[i]["SpotPriceDKK"]) == price_points[i].price for i in range(len(records))])

    def test_create_price_points_from_json_invalid_missing_hourdk(self):
        # Arrange
        eds = EdsRequests()
        records: List[Dict[str, str]] = [
            { "SpotPriceDKK": "1" },
        ]

        # Act / Assert
        with pytest.raises(KeyError):
            eds.create_price_points_from_json(records)

    def test_create_price_points_from_json_invalid_missing_spotpricedkk(self):
        # Arrange
        eds = EdsRequests()
        records: List[Dict[str, str]] = [
            { "HourDK": "2023-02-01T23:00:00" },
        ]

        # Act / Assert
        with pytest.raises(KeyError):
            eds.create_price_points_from_json(records)

    def test_create_price_points_from_json_invalid_none_hourdk(self):
        # Arrange
        eds = EdsRequests()
        records: List[Dict[str, str]] = [
            { "HourDK": "2023-02-1T23:00:00" },
        ]

        # Act / Assert
        with pytest.raises(ValueError):
            eds.create_price_points_from_json(records)

    def test_create_price_points_from_json_invalid_none_spotpricedkk(self):
        # Arrange
        eds = EdsRequests()
        records: List[Dict[str, str]] = [
            { "SpotPriceDKK": "NaN" },
        ]

        # Act / Assert
        with pytest.raises(KeyError):
            eds.create_price_points_from_json(records)