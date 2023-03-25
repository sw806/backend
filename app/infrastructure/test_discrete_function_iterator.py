from datetime import timedelta

from infrastructure.discrete_function_iterator import DiscreteFunctionIterator
from infrastructure.power_usage_function import PowerUsageFunction


class TestDiscreteFunctionIterator:
    def test_single_function_min_domain_start(self):
        # Arrange
        power_function = PowerUsageFunction([
            (timedelta(), 0),
            (timedelta(minutes=20), 1),
        ], timedelta(hours=1))
        iterator = DiscreteFunctionIterator([power_function])
        points = []

        # Act
        for point in iterator:
            points.append(point)

        # Assert
        assert len(points) == 3
        assert points[0] == timedelta()
        assert points[1] == timedelta(minutes=20)
        assert points[2] == timedelta(hours=1, minutes=20)

    def test_two_functions_same_points_min_domain_start(self):
        # Arrange
        power_function = PowerUsageFunction([
            (timedelta(), 0),
            (timedelta(minutes=20), 1),
        ], timedelta(hours=1))
        iterator = DiscreteFunctionIterator([power_function, power_function])
        points = []

        # Act
        for point in iterator:
            points.append(point)

        # Assert
        assert len(points) == 3
        assert points[0] == timedelta()
        assert points[1] == timedelta(minutes=20)
        assert points[2] == timedelta(hours=1, minutes=20)

    def test_two_functions_different_points_min_domain_start(self):
        # Arrange
        power_function_0 = PowerUsageFunction([
            (timedelta(), 0),
            (timedelta(minutes=20), 1),
        ], timedelta(hours=1))
        power_function_1 = PowerUsageFunction([
            (timedelta(), 0),
            (timedelta(minutes=15), 1),
        ], timedelta(hours=2))
        iterator = DiscreteFunctionIterator([power_function_0, power_function_1])
        points = []

        # Act
        for point in iterator:
            points.append(point)

        # Assert
        assert len(points) == 5
        assert points[0] == timedelta()
        assert points[1] == timedelta(minutes=15)
        assert points[2] == timedelta(minutes=20)
        assert points[3] == timedelta(hours=1, minutes=20)
        assert points[4] == timedelta(hours=2, minutes=15)

    def test_two_functions_different_points_min_domain_start_overlapping(self):
        # Arrange
        power_function_0 = PowerUsageFunction([
            (timedelta(), 0),
            (timedelta(minutes=20), 1),
        ], timedelta(hours=1))
        power_function_1 = PowerUsageFunction([
            (timedelta(), 0),
            (timedelta(minutes=20), 1),
        ], timedelta(hours=2))
        iterator = DiscreteFunctionIterator([power_function_0, power_function_1])
        points = []

        # Act
        for point in iterator:
            points.append(point)

        # Assert
        assert len(points) == 4
        assert points[0] == timedelta()
        assert points[1] == timedelta(minutes=20)
        assert points[2] == timedelta(hours=1, minutes=20)
        assert points[3] == timedelta(hours=2, minutes=20)
