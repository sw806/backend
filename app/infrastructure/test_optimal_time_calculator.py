from datetime import datetime
from typing import List
from app.infrastructure.eletricity_prices import PricePoint
from app.infrastructure.optimal_time_calculator import OptimalTimeCalculator


class TestOptimalTimeCalculator:
    def test_one_hour_span(self):
        # Arrange
        expected: datetime = datetime(2021, 1, 1, 19)
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 10.0),
            PricePoint(datetime(2021, 1, 1, 16), 10.0),
            PricePoint(datetime(2021, 1, 1, 17), 10.0),
            PricePoint(datetime(2021, 1, 1, 18), 10.0),
            PricePoint(expected, 5.0),
            PricePoint(datetime(2021, 1, 1, 19), 10.0),
            PricePoint(datetime(2021, 1, 1, 20), 10.0),
            PricePoint(datetime(2021, 1, 1, 21), 10.0),
            PricePoint(datetime(2021, 1, 1, 22), 10.0)
        ]

        # Act
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, 1, 3600)

        # Assert
        assert optimal_time == int(expected.timestamp())

    def test_two_hour_span(self):
        # Arrange
        expected: datetime = datetime(2021, 1, 1, 18)
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 10.0),
            PricePoint(datetime(2021, 1, 1, 16), 10.0),
            PricePoint(datetime(2021, 1, 1, 17), 10.0),
            PricePoint(datetime(2021, 1, 1, 18), 10.0),
            PricePoint(expected, 5.0),
            PricePoint(datetime(2021, 1, 1, 20), 10.0),
            PricePoint(datetime(2021, 1, 1, 21), 10.0),
            PricePoint(datetime(2021, 1, 1, 22), 10.0),
            PricePoint(datetime(2021, 1, 1, 23), 10.0)
        ]

        # Act
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, 1, 7200)

        # Assert
        assert optimal_time == int(expected.timestamp())

    def test_one_hour_span_early_edge_case(self):
        # Arrange
        expected: datetime = datetime(2021, 1, 1, 15)
        price_points: List[PricePoint] = [
            PricePoint(expected, 5.0),
            PricePoint(datetime(2021, 1, 1, 16), 10.0),
            PricePoint(datetime(2021, 1, 1, 17), 10.0),
            PricePoint(datetime(2021, 1, 1, 18), 10.0),
            PricePoint(datetime(2021, 1, 1, 19), 10.0),
            PricePoint(datetime(2021, 1, 1, 20), 10.0),
            PricePoint(datetime(2021, 1, 1, 21), 10.0),
            PricePoint(datetime(2021, 1, 1, 22), 10.0),
            PricePoint(datetime(2021, 1, 1, 23), 10.0)
        ]

        # Act
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, 1, 7200)

        # Assert
        assert optimal_time == int(expected.timestamp())

        def test_one_hour_span_early_edge_case(self):
            # Arrange
            expected: datetime = datetime(2021, 1, 1, 15)
            price_points: List[PricePoint] = [
                PricePoint(expected, 5.0),
                PricePoint(datetime(2021, 1, 1, 16), 10.0),
                PricePoint(datetime(2021, 1, 1, 17), 10.0),
                PricePoint(datetime(2021, 1, 1, 18), 10.0),
                PricePoint(datetime(2021, 1, 1, 19), 10.0),
                PricePoint(datetime(2021, 1, 1, 20), 10.0),
                PricePoint(datetime(2021, 1, 1, 21), 10.0),
                PricePoint(datetime(2021, 1, 1, 22), 10.0),
                PricePoint(datetime(2021, 1, 1, 23), 10.0)
            ]

            # Act
            optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, 1, 3600)

            # Assert
            assert optimal_time == int(expected.timestamp())

    def test_one_hour_span_late_edge_case(self):
        # Arrange
        expected: datetime = datetime(2021, 1, 1, 23)
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 10.0),
            PricePoint(datetime(2021, 1, 1, 16), 10.0),
            PricePoint(datetime(2021, 1, 1, 17), 10.0),
            PricePoint(datetime(2021, 1, 1, 18), 10.0),
            PricePoint(datetime(2021, 1, 1, 19), 10.0),
            PricePoint(datetime(2021, 1, 1, 20), 10.0),
            PricePoint(datetime(2021, 1, 1, 21), 10.0),
            PricePoint(datetime(2021, 1, 1, 22), 10.0),
            PricePoint(expected, 5.0)
        ]

        # Act
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, 1, 3600)

        # Assert
        assert optimal_time == int(expected.timestamp())