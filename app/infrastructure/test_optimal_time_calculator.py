from datetime import datetime
from typing import List
from app.infrastructure.eletricity_prices import PricePoint
from app.infrastructure.optimal_time_calculator import OptimalTimeCalculator


class TestOptimalTimeCalculator:
    def test_one_hour_span(self):
        # Arrange
        expected: datetime = datetime(2021, 1, 1, 19)
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 23), 10.0),
            PricePoint(datetime(2021, 1, 1, 22), 10.0),
            PricePoint(datetime(2021, 1, 1, 21), 10.0),
            PricePoint(datetime(2021, 1, 1, 20), 10.0),
            PricePoint(expected, 5.0),
            PricePoint(datetime(2021, 1, 1, 18), 10.0),
            PricePoint(datetime(2021, 1, 1, 17), 10.0),
            PricePoint(datetime(2021, 1, 1, 16), 10.0),
            PricePoint(datetime(2021, 1, 1, 15), 10.0)
        ]

        # Act
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, 1, 3600)
        # convert optimal_time to unix timestamp
        # optimal_time = int(optimal_time.timestamp())

        # Assert
        # 1609524000 is the unix timestamp for 2021-01-01 19:00:00
        assert optimal_time == int(expected.timestamp())

