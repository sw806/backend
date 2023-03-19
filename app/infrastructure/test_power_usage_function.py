
from datetime import timedelta
from typing import List, Tuple
from random import random

from infrastructure.power_usage_function import PowerUsageFunction


class TestPowerUsageFunction:
    def test_apply_correctly_evaluates_and_returns_price(self):
        # Arrange
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=1), 1),
            (timedelta(hours=2), 2),
            (timedelta(hours=3), 3),
            (timedelta(hours=4), 4),
            (timedelta(hours=5), 5),
            (timedelta(hours=6), 6),
            (timedelta(hours=7), 7),
            (timedelta(hours=8), 8)
        ]
        power_usage_function = PowerUsageFunction(power_points)

        for point in power_points:
            # Act
            (_, power) = point
            integral = power_usage_function.apply(
                power_usage_function.get_domain(point)
            )

            # Assert
            assert integral == power

    def test_integrate_over_the_same_power_point(self):
        # Setup
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=1), 1),
            (timedelta(hours=2), 2),
            (timedelta(hours=3), 3),
            (timedelta(hours=4), 4),
            (timedelta(hours=5), 5),
            (timedelta(hours=6), 6),
            (timedelta(hours=7), 7),
            (timedelta(hours=8), 8)
        ]
        power_usage_function = PowerUsageFunction(power_points)

        for power_point in power_points[:-1]:
            for _ in range(1000):
                # Arrange
                hours: float = random()
                (start, power) = power_point
                end: timedelta = start + timedelta(hours=hours)
                expected = power * hours

                # Act
                integral: float = power_usage_function.integrate(start, end)

                # Assert
                assert integral - expected < 0.01

    def test_integrate_over_nearly_the_same_power_point(self):
        # Setup
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=1), 1),
            (timedelta(hours=2), 2),
            (timedelta(hours=3), 3),
            (timedelta(hours=4), 4),
            (timedelta(hours=5), 5),
            (timedelta(hours=6), 6),
            (timedelta(hours=7), 7),
            (timedelta(hours=8), 8)
        ]
        power_usage_function = PowerUsageFunction(power_points)


        for idx, (end_delta, _) in enumerate(power_points[1:]):
            # Arrange
            (start_delta, start_power) = power_points[idx]

            # Act
            integral: float = power_usage_function.integrate(
                start_delta, end_delta
            )

            # Assert
            assert integral == start_power

    def test_integrate_over_multiple_hours(self):
        # Arrange
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=1), 1),
            (timedelta(hours=2), 2),
            (timedelta(hours=3), 3),
            (timedelta(hours=4), 4),
            (timedelta(hours=5), 5),
            (timedelta(hours=6), 6),
            (timedelta(hours=7), 7),
            (timedelta(hours=8), 8)
        ]
        power_usage_function = PowerUsageFunction(power_points)

        # Act
        integral = power_usage_function.integrate(
            timedelta(hours=1),
            timedelta(hours=4)
        )

        # Assert
        assert integral == 1 + 2 + 3

    def test_integrate_from_0_hour_to_1(self):
        # Arrange
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=1), 1),
        ]
        power_usage_function = PowerUsageFunction(power_points)

        # Act
        integral = power_usage_function.integrate(
            timedelta(hours=0),
            timedelta(hours=1)
        )

        # Assert
        assert integral == 1

    def test_integrate_from_1_hour_to_2(self):
        # Arrange
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=1), 1),
        ]
        power_usage_function = PowerUsageFunction(power_points)

        # Act
        integral = power_usage_function.integrate(
            timedelta(hours=1),
            timedelta(hours=2)
        )

        # Assert
        assert integral == 1

    def test_integrate_from_0_hour_to_2(self):
        # Arrange
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=1), 1),
        ]
        power_usage_function = PowerUsageFunction(power_points)

        # Act
        integral = power_usage_function.integrate(
            timedelta(hours=0),
            timedelta(hours=2)
        )

        # Assert
        assert integral == 2

    def test_sum_single_power_point(self):
        # Arrange
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=1), 1),
            (timedelta(hours=2), 2),
            (timedelta(hours=3), 3),
            (timedelta(hours=4), 4),
            (timedelta(hours=5), 5),
            (timedelta(hours=6), 6),
            (timedelta(hours=7), 7),
            (timedelta(hours=8), 8)
        ]
        power_usage_function = PowerUsageFunction(power_points)

        # Act
        sum = power_usage_function.sum(
            timedelta(hours=1), timedelta(hours=1)
        )

        # Assert
        assert sum == 1

    def test_sum_between_two_power_points(self):
        # Arrange
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=1), 1),
            (timedelta(hours=2), 2),
            (timedelta(hours=3), 3),
            (timedelta(hours=4), 4),
            (timedelta(hours=5), 5),
            (timedelta(hours=6), 6),
            (timedelta(hours=7), 7),
            (timedelta(hours=8), 8)
        ]
        power_usage_function = PowerUsageFunction(power_points)

        # Act
        sum = power_usage_function.sum(
            timedelta(hours=1), timedelta(hours=1, minutes=30)
        )

        # Assert
        assert sum == 3


    def test_sum_two_power_points(self):
        # Arrange
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=1), 1),
            (timedelta(hours=2), 2),
            (timedelta(hours=3), 3),
            (timedelta(hours=4), 4),
            (timedelta(hours=5), 5),
            (timedelta(hours=6), 6),
            (timedelta(hours=7), 7),
            (timedelta(hours=8), 8)
        ]
        power_usage_function = PowerUsageFunction(power_points)

        # Act
        sum = power_usage_function.sum(
            timedelta(hours=1), timedelta(hours=2)
        )

        # Assert
        assert sum == 3

    def test_sum_over_all_power_points(self):
        # Arrange
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=1), 1),
            (timedelta(hours=2), 2),
            (timedelta(hours=3), 3),
            (timedelta(hours=4), 4),
            (timedelta(hours=5), 5),
            (timedelta(hours=6), 6),
            (timedelta(hours=7), 7),
            (timedelta(hours=8), 8)
        ]
        power_usage_function = PowerUsageFunction(power_points, extend_by=timedelta(hours=0))

        # Act
        sum = power_usage_function.sum(
            power_usage_function.min_domain, power_usage_function.max_domain
        )

        # Assert
        assert sum == 37

    def test_sum_over_all_power_points_extended_one_hour(self):
        # Arrange
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=1), 1),
            (timedelta(hours=2), 2),
            (timedelta(hours=3), 3),
            (timedelta(hours=4), 4),
            (timedelta(hours=5), 5),
            (timedelta(hours=6), 6),
            (timedelta(hours=7), 7),
            (timedelta(hours=8), 8)
        ]
        power_usage_function = PowerUsageFunction(power_points, extend_by=timedelta(hours=1))

        # Act
        sum = power_usage_function.sum(
            power_usage_function.min_domain, power_usage_function.max_domain
        )

        # Assert
        assert sum == 45
    
    def test_random_sum_over_power_points(self):
        # Arrange
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=1), 1),
            (timedelta(hours=2), 1),
            (timedelta(hours=3), 1),
            (timedelta(hours=4), 1),
            (timedelta(hours=5), 1),
            (timedelta(hours=6), 1),
            (timedelta(hours=7), 1),
            (timedelta(hours=8), 1)
        ]
        power_usage_function = PowerUsageFunction(power_points, extend_by=timedelta(hours=1))

        for _ in range(1000):
            # Act
            hours = int(5 * random())
            expected = 1 + (1 * hours)
            sum = power_usage_function.sum(
                power_usage_function.min_domain, power_usage_function.min_domain + timedelta(hours=hours)
            )

            # Assert
            assert sum == expected