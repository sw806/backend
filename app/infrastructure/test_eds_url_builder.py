from datetime import datetime

from .eds_url_builder import EdsUrlBuilder

class TestEdsEndpointBuilder:
    def test_with_just_dataset(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset)

        # Act
        url = builder.build()

        # Assert
        assert url == f'https://api.energidataservice.dk/dataset/{dataset}?timezone=utc'

    def test_with_dk1_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .add_to_filter("PriceArea", "DK1")

        # Act
        url = builder.build()

        # Assert
        assert url == f'https://api.energidataservice.dk/dataset/{dataset}' + '?filter={"PriceArea":["DK1"]}&timezone=utc'


    def test_with_dk1_and_dk2_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .add_to_filter("PriceArea", "DK1") \
            .add_to_filter("PriceArea", "DK2")

        # Act
        url = builder.build()

        # Assert
        assert url == f'https://api.energidataservice.dk/dataset/{dataset}' + '?filter={"PriceArea":["DK1","DK2"]}&timezone=utc'

    def test_with_start_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .set_start(datetime(2023, 3, 7))

        # Act
        url = builder.build()

        # Assert
        assert url == f'https://api.energidataservice.dk/dataset/{dataset}?start=2023-03-07T00:00&timezone=utc'

    def test_with_end_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .set_end(datetime(2023, 3, 7))

        # Act
        url = builder.build()

        # Assert
        assert url == f'https://api.energidataservice.dk/dataset/{dataset}?end=2023-03-07T00:00&timezone=utc'

    def test_with_limit_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .set_limit(100)

        # Act
        url = builder.build()

        # Assert
        assert url == f'https://api.energidataservice.dk/dataset/{dataset}?limit=100&timezone=utc'

    def test_with_offset_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .set_offset(100)

        # Act
        url = builder.build()

        # Assert
        assert url == f'https://api.energidataservice.dk/dataset/{dataset}?offset=100&timezone=utc'

    def test_with_timezone_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .set_timezone("dk")

        # Act
        url = builder.build()

        # Assert
        assert url == f'https://api.energidataservice.dk/dataset/{dataset}?timezone=dk&timezone=utc'

    def test_with_sort_on_key_asending_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .set_sort_on_key("HourUTC", True)

        # Act
        url = builder.build()

        # Assert
        assert url == f'https://api.energidataservice.dk/dataset/{dataset}?sort=HourUTC ASC&timezone=utc'

    def test_with_sort_on_key_desending_filter(self):
        # Arrange
        dataset = "Elspotprices"
        builder = EdsUrlBuilder(dataset) \
            .set_sort_on_key("HourUTC", False)

        # Act
        url = builder.build()

        # Assert
        assert url == f'https://api.energidataservice.dk/dataset/{dataset}?sort=HourUTC DESC&timezone=utc'

    def test_with_everything(self):
        # Arrange
        builder = EdsUrlBuilder("Elspotprices") \
            .set_offset(0) \
            .set_limit(20) \
            .set_start(datetime(2023, 3, 1)) \
            .set_end(datetime(2023, 3, 3)) \
            .add_to_filter("PriceArea", "DK1") \
            .add_to_filter("PriceArea", "DK2") \
            .set_sort_on_key("HourUTC", True) \
            .set_timezone("dk")

        # Act
        url = builder.build()

        # Assert
        assert 'offset=0' in url
        assert 'limit=20' in url
        assert 'start=2023-03-01T00:00' in url
        assert 'end=2023-03-03T00:00' in url
        assert 'filter={"PriceArea":["DK1","DK2"]}' in url
        assert 'sort=HourUTC ASC' in url
        assert 'timezone=dk' in url

    def test_with_datetime_now(self):
        # Arrange
        now = datetime.now()
        builder = EdsUrlBuilder("Elspotprices") \
            .set_start(now)

        # Act
        url = builder.build()

        year_str = str(now.year).zfill(4)
        month_str = str(now.month).zfill(2)
        day_str = str(now.day).zfill(2)
        hour_str = str(now.hour).zfill(2)
        minute_str = str(now.minute).zfill(2)
        expected_iso = f'{year_str}-{month_str}-{day_str}T{hour_str}:{minute_str}'

        # Assert
        assert f'start={expected_iso}' in url