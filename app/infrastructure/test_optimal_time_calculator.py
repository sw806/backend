from datetime import datetime, timedelta
from typing import List
from domain import PricePoint
from infrastructure import OptimalTimeCalculator


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
            PricePoint(datetime(2021, 1, 1, 20), 10.0),
            PricePoint(datetime(2021, 1, 1, 21), 10.0),
            PricePoint(datetime(2021, 1, 1, 22), 10.0)
        ]

        # Act
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, timedelta(seconds=3600))

        # Assert
        assert optimal_time == int(expected.timestamp())

    def test_two_hour_span(self):
        # Arrange
        expected: datetime = datetime(2021, 1, 1, 17)
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 10.0),
            PricePoint(datetime(2021, 1, 1, 16), 10.0),
            PricePoint(datetime(2021, 1, 1, 17), 10.0),
            PricePoint(expected, 5.0),
            PricePoint(datetime(2021, 1, 1, 19), 10.0),
            PricePoint(datetime(2021, 1, 1, 20), 10.0),
            PricePoint(datetime(2021, 1, 1, 21), 10.0),
            PricePoint(datetime(2021, 1, 1, 22), 10.0),
            PricePoint(datetime(2021, 1, 1, 23), 10.0)
        ]

        # Act
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, timedelta(seconds=7200))

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
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, timedelta(seconds=7200))

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
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, timedelta(seconds=3600))

        # Assert
        assert optimal_time == int(expected.timestamp())

    def test_one_and_a_half_hour_span(self):
        # Arrange
        expected: datetime = datetime(2021, 1, 1, 18, 30)
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 10.0),
            PricePoint(datetime(2021, 1, 1, 16), 10.0),
            PricePoint(datetime(2021, 1, 1, 17), 5.0),
            PricePoint(datetime(2021, 1, 1, 18), 6.0),
            PricePoint(datetime(2021, 1, 1, 19), 4.0),
            PricePoint(datetime(2021, 1, 1, 20), 10.0),
            PricePoint(datetime(2021, 1, 1, 21), 10.0),
            PricePoint(datetime(2021, 1, 1, 22), 10.0)
        ]

        # Act
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, timedelta(seconds=5400))

        # Assert
        assert optimal_time == int(expected.timestamp())

    def test_one_and_a_quarter_hour_span(self):
        # Arrange
        expected: datetime = datetime(2021, 1, 1, 18, 45)
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 10.0),
            PricePoint(datetime(2021, 1, 1, 16), 10.0),
            PricePoint(datetime(2021, 1, 1, 17), 5.0),
            PricePoint(datetime(2021, 1, 1, 18), 6.0),
            PricePoint(datetime(2021, 1, 1, 19), 4.0),
            PricePoint(datetime(2021, 1, 1, 20), 10.0),
            PricePoint(datetime(2021, 1, 1, 21), 10.0),
            PricePoint(datetime(2021, 1, 1, 22), 10.0)
        ]

        # Act
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, timedelta(seconds=4500))

        # Assert
        assert optimal_time == int(expected.timestamp())

    def test_one_and_three_quarters_hour_span(self):
        # Arrange
        expected: datetime = datetime(2021, 1, 1, 18, 15)
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 10.0),
            PricePoint(datetime(2021, 1, 1, 16), 10.0),
            PricePoint(datetime(2021, 1, 1, 17), 5.0),
            PricePoint(datetime(2021, 1, 1, 18), 6.0),
            PricePoint(datetime(2021, 1, 1, 19), 4.0),
            PricePoint(datetime(2021, 1, 1, 20), 10.0),
            PricePoint(datetime(2021, 1, 1, 21), 10.0),
            PricePoint(datetime(2021, 1, 1, 22), 10.0)
        ]

        # Act
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, timedelta(seconds=6300))

        # Assert
        assert optimal_time == int(expected.timestamp())

    def test_span_is_zero(self):
        # Arrange
        expected: datetime = datetime(2021, 1, 1, 15)
        price_points: List[PricePoint] = [
            PricePoint(expected, 10.0),
            PricePoint(datetime(2021, 1, 1, 16), 10.0),
            PricePoint(datetime(2021, 1, 1, 17), 5.0),
            PricePoint(datetime(2021, 1, 1, 18), 10.0),
            PricePoint(datetime(2021, 1, 1, 19), 10.0),
            PricePoint(datetime(2021, 1, 1, 20), 10.0),
            PricePoint(datetime(2021, 1, 1, 21), 10.0),
            PricePoint(datetime(2021, 1, 1, 22), 10.0)
        ]

        # Act
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, timedelta(seconds=0))

        # Assert
        assert optimal_time == int(expected.timestamp())

    def test_span_is_sub_one_minute(self):
        # Arrange
        expected: datetime = datetime(2021, 1, 1, 17)
        price_points: List[PricePoint] = [
            PricePoint(expected, 10.0),
            PricePoint(datetime(2021, 1, 1, 16), 10.0),
            PricePoint(datetime(2021, 1, 1, 17), 5.0),
            PricePoint(datetime(2021, 1, 1, 18), 10.0),
            PricePoint(datetime(2021, 1, 1, 19), 10.0),
            PricePoint(datetime(2021, 1, 1, 20), 10.0),
            PricePoint(datetime(2021, 1, 1, 21), 10.0),
            PricePoint(datetime(2021, 1, 1, 22), 10.0)
        ]

        # Act
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, timedelta(seconds=30))

        # Assert
        assert optimal_time == int(expected.timestamp())

    def test_span_is_sub_one_minute_decomposable(self):
        # Arrange
        expected: datetime = datetime(2021, 1, 1, 17)
        price_points: List[PricePoint] = [
            PricePoint(expected, 10.0),
            PricePoint(datetime(2021, 1, 1, 16), 10.0),
            PricePoint(datetime(2021, 1, 1, 17), 5.0),
            PricePoint(datetime(2021, 1, 1, 18), 10.0),
            PricePoint(datetime(2021, 1, 1, 19), 10.0),
            PricePoint(datetime(2021, 1, 1, 20), 10.0),
            PricePoint(datetime(2021, 1, 1, 21), 10.0),
            PricePoint(datetime(2021, 1, 1, 22), 10.0)
        ]

        # Act
        optimal_time = OptimalTimeCalculator().calculate_optimal_time(price_points, timedelta(seconds=3030))

        # Assert
        assert optimal_time == int(expected.timestamp())