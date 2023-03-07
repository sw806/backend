from datetime import datetime
import pytest

from .eds_url_builder import EdsUrlBuilder

class TestEdsEndpointBuilder:
    def test_with_just_dataset(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset)

        # Act
        url = builder.build()

        # Assert
        assert url == f'https://api.energidataservice.dk/{dataset}'

    def test_with_dk1_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .add_to_filter("PriceArea", "DK1")

        # Act
        url = builder.build()

        print(url)

        # Assert
        assert url == f'https://api.energidataservice.dk/{dataset}' + '?filter={"PriceArea":["DK1"]}'


    def test_with_dk1_and_dk2_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .add_to_filter("PriceArea", "DK1") \
            .add_to_filter("PriceArea", "DK2")

        # Act
        url = builder.build()

        print(url)

        # Assert
        assert url == f'https://api.energidataservice.dk/{dataset}' + '?filter={"PriceArea":["DK1","DK2"]}'

    def test_with_start_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .set_start(datetime(2023, 3, 7))

        # Act
        url = builder.build()

        print(url)

        # Assert
        assert url == f'https://api.energidataservice.dk/{dataset}?start=2023-03-07T00:00'

    def test_with_end_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .set_end(datetime(2023, 3, 7))

        # Act
        url = builder.build()

        print(url)

        # Assert
        assert url == f'https://api.energidataservice.dk/{dataset}?end=2023-03-07T00:00'

    def test_with_limit_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .set_limit(100)

        # Act
        url = builder.build()

        print(url)

        # Assert
        assert url == f'https://api.energidataservice.dk/{dataset}?limit=100'

    def test_with_offset_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .set_offset(100)

        # Act
        url = builder.build()

        print(url)

        # Assert
        assert url == f'https://api.energidataservice.dk/{dataset}?offset=100'

    def test_with_timezone_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .set_timezone("dk")

        # Act
        url = builder.build()

        print(url)

        # Assert
        assert url == f'https://api.energidataservice.dk/{dataset}?timezone=dk'

    def test_with_sort_on_key_asending_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .set_sort_on_key("HourUTC", True)

        # Act
        url = builder.build()

        print(url)

        # Assert
        assert url == f'https://api.energidataservice.dk/{dataset}?sort=HourUTC ASC'

    def test_with_sort_on_key_desending_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .set_sort_on_key("HourUTC", False)

        # Act
        url = builder.build()

        print(url)

        # Assert
        assert url == f'https://api.energidataservice.dk/{dataset}?sort=HourUTC DESC'