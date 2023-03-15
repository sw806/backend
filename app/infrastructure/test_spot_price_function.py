from datetime import datetime, timedelta
from random import random
from typing import List
from infrastructure.eletricity_prices import PricePoint
from infrastructure.spot_price_function import SpotPriceFunction


class TestSpotPriceFunction:
    def test_apply_correctly_evaluates_and_returns_price(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 2),
            PricePoint(datetime(2021, 1, 1, 17), 3),
            PricePoint(datetime(2021, 1, 1, 18), 4),
            PricePoint(datetime(2021, 1, 1, 19), 5),
            PricePoint(datetime(2021, 1, 1, 20), 6),
            PricePoint(datetime(2021, 1, 1, 21), 7),
            PricePoint(datetime(2021, 1, 1, 22), 8)
        ]
        spot_price_function = SpotPriceFunction(price_points)

        for price_point in price_points:
            # Act
            price = spot_price_function.apply(price_point.time)

            # Assert
            assert price == price_point.price

    def test_integrate_over_the_same_price_point(self):
        # Setup
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 2),
            PricePoint(datetime(2021, 1, 1, 17), 3),
            PricePoint(datetime(2021, 1, 1, 18), 4),
            PricePoint(datetime(2021, 1, 1, 19), 5),
            PricePoint(datetime(2021, 1, 1, 20), 6),
            PricePoint(datetime(2021, 1, 1, 21), 7),
            PricePoint(datetime(2021, 1, 1, 22), 8)
        ]
        spot_price_function = SpotPriceFunction(price_points)

        for price_point in price_points:
            for _ in range(1000):
                # Arrange
                hours: float = random()
                start: datetime = price_point.time
                end: datetime = start + timedelta(hours=hours)
                expected = price_point.price * hours

                # Act
                integral: float = spot_price_function.integrate(start, end)

                # Assert
                assert integral - expected < 0.01

    def test_integrate_over_nearly_the_same_price_point(self):
        # Setup
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 2),
            PricePoint(datetime(2021, 1, 1, 17), 3),
            PricePoint(datetime(2021, 1, 1, 18), 4),
            PricePoint(datetime(2021, 1, 1, 19), 5),
            PricePoint(datetime(2021, 1, 1, 20), 6),
            PricePoint(datetime(2021, 1, 1, 21), 7),
            PricePoint(datetime(2021, 1, 1, 22), 8)
        ]
        spot_price_function = SpotPriceFunction(price_points)

        for idx, end_price_point in enumerate(price_points[1:]):
            # Arrange
            start_price_point = price_points[idx]

            # Act
            integral: float = spot_price_function.integrate(
                start_price_point.time, end_price_point.time
            )

            # Assert
            assert integral == price_points[idx].price

    def test_integrate_over_multiple_hours(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 2),
            PricePoint(datetime(2021, 1, 1, 17), 3),
            PricePoint(datetime(2021, 1, 1, 18), 4),
            PricePoint(datetime(2021, 1, 1, 19), 5),
            PricePoint(datetime(2021, 1, 1, 20), 6),
            PricePoint(datetime(2021, 1, 1, 21), 7),
            PricePoint(datetime(2021, 1, 1, 22), 8)
        ]
        spot_price_function = SpotPriceFunction(price_points)

        # Act
        integral = spot_price_function.integrate(
            datetime(2021, 1, 1, 15),
            datetime(2021, 1, 1, 18)
        )

        # Assert
        assert integral == 1 + 2 + 3

    def test_integrate_from_0_hour_to_1(self):
        # Arrange
        power_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
        ]
        spot_price_function = SpotPriceFunction(power_points)

        # Act
        integral = spot_price_function.integrate(
            datetime(2021, 1, 1, 15),
            datetime(2021, 1, 1, 16)
        )

        # Assert
        assert integral == 1
