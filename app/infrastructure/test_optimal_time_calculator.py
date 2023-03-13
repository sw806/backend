from datetime import datetime
from typing import List
from app.infrastructure.eletricity_prices import PricePoint
from app.infrastructure.optimal_time_calculator import OptimalTimeCalculator
from app.infrastructure.optimal_time_calculator2 import OptimalTimeCalculator2


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
        optimal_time = OptimalTimeCalculator2().calculate_optimal_time(price_points, 1, 3600)

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
        optimal_time = OptimalTimeCalculator2().calculate_optimal_time(price_points, 1, 7200)

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
        optimal_time = OptimalTimeCalculator2().calculate_optimal_time(price_points, 1, 7200)

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
        optimal_time = OptimalTimeCalculator2().calculate_optimal_time(price_points, 1, 3600)

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
        optimal_time = OptimalTimeCalculator2.calculate_optimal_time(self, price_points, 1, 5400)

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
        optimal_time = OptimalTimeCalculator2.calculate_optimal_time(self, price_points, 1, 4500)

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
        optimal_time = OptimalTimeCalculator2.calculate_optimal_time(self, price_points, 1, 6300)

        # Assert
        assert optimal_time == int(expected.timestamp())