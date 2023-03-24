from datetime import datetime, timedelta
from typing import List
from infrastructure.scheduler_v2 import DatetimeInterval, DiscreteFunctionIterator, Schedule, ScheduledTask, Scheduler, Task
from infrastructure.power_usage_function import PowerUsageFunction
from infrastructure.eletricity_prices import PricePoint
from infrastructure.spot_price_function import SpotPriceFunction


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

    def test_two_functions_different_points_min_domain_start(self):
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

class TestSchedulerV2:
    def test_get_available_start_times_half_hour_none_scheduled(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 1),
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)

        power_usage_function = PowerUsageFunction(
            [(timedelta(hours=0), 1)], extend_by=timedelta(minutes=30)
        )
        task = Task(power_usage_function)

        # Act
        start_points = scheduler.get_all_possible_start_times(task)

        # Assert
        assert len(start_points) == 4
        assert datetime(2021, 1, 1, 15) in start_points
        assert datetime(2021, 1, 1, 15, 30) in start_points
        assert datetime(2021, 1, 1, 16) in start_points
        assert datetime(2021, 1, 1, 16, 30) in start_points

    def test_get_available_start_times_full_hour_none_scheduled(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 1),
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)

        power_usage_function = PowerUsageFunction(
            [(timedelta(hours=0), 1)], extend_by=timedelta(hours=1)
        )
        task = Task(power_usage_function)

        # Act
        start_points = scheduler.get_all_possible_start_times(task)

        # Assert
        assert len(start_points) == 2
        assert datetime(2021, 1, 1, 15) in start_points
        assert datetime(2021, 1, 1, 16) in start_points

    def test_get_available_start_times_one_and_a_half_hour_none_scheduled(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 1),
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)

        power_usage_function = PowerUsageFunction(
            [(timedelta(hours=0), 1)], extend_by=timedelta(hours=1, minutes=30)
        )
        task = Task(power_usage_function)

        # Act
        start_points = scheduler.get_all_possible_start_times(task)

        # Assert
        assert len(start_points) == 2
        assert datetime(2021, 1, 1, 15) in start_points
        assert datetime(2021, 1, 1, 15, 30) in start_points


    def test_get_available_start_times_half_hour_one_scheduled(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 1),
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)

        power_usage_function = PowerUsageFunction(
            [(timedelta(hours=0), 1)], extend_by=timedelta(minutes=30)
        )
        task = Task(power_usage_function)

        scheduled_task = ScheduledTask(
            DatetimeInterval(datetime(2021, 1, 1, 16, 15), timedelta()), task
        )
        schedule = Schedule([scheduled_task])

        # Act
        start_points = scheduler.get_all_possible_start_times(task, schedule)

        # Assert
        assert len(start_points) == 6
        assert datetime(2021, 1, 1, 15) in start_points
        assert datetime(2021, 1, 1, 15, 30) in start_points
        assert datetime(2021, 1, 1, 15, 45) in start_points
        assert datetime(2021, 1, 1, 16) in start_points
        assert datetime(2021, 1, 1, 16, 15) in start_points
        assert datetime(2021, 1, 1, 16, 30) in start_points

    def test_get_available_start_times_one_full_hour_one_scheduled(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 1),
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)

        power_usage_function = PowerUsageFunction(
            [(timedelta(hours=0), 1)], extend_by=timedelta(hours=1)
        )
        task = Task(power_usage_function)

        scheduled_task = ScheduledTask(
            DatetimeInterval(datetime(2021, 1, 1, 16, 15), timedelta()), task
        )
        schedule = Schedule([scheduled_task])

        # Act
        start_points = scheduler.get_all_possible_start_times(task, schedule)

        # Assert
        assert len(start_points) == 3
        assert datetime(2021, 1, 1, 15) in start_points
        assert datetime(2021, 1, 1, 15, 15) in start_points
        assert datetime(2021, 1, 1, 16) in start_points

    def test_get_available_start_times_one_and_a_half_hour_one_scheduled(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 1),
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)

        power_usage_function = PowerUsageFunction(
            [(timedelta(hours=0), 1)], extend_by=timedelta(hours=1, minutes=30)
        )
        task = Task(power_usage_function)

        scheduled_task = ScheduledTask(
            DatetimeInterval(datetime(2021, 1, 1, 16, 15), timedelta()), task
        )
        schedule = Schedule([scheduled_task])

        # Act
        start_points = scheduler.get_all_possible_start_times(task, schedule)

        # Assert
        assert len(start_points) == 2
        assert datetime(2021, 1, 1, 15) in start_points
        assert datetime(2021, 1, 1, 15, 30) in start_points
    
    def test_get_available_start_times_variable_power_consumption(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 1),
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)

        power_usage_function = PowerUsageFunction(
            [(timedelta(), 1), (timedelta(minutes=5), 2)], extend_by=timedelta(minutes=10)
        )
        task = Task(power_usage_function)

        schedule = Schedule([])

        # Act
        start_points = scheduler.get_all_possible_start_times(task, schedule)

        # Assert
        assert len(start_points) == 9
        assert datetime(2021, 1, 1, 15) in start_points
        assert datetime(2021, 1, 1, 15, 5) in start_points
        assert datetime(2021, 1, 1, 15, 15) in start_points
        assert datetime(2021, 1, 1, 15, 45) in start_points
        assert datetime(2021, 1, 1, 15, 55) in start_points
        assert datetime(2021, 1, 1, 16) in start_points
        assert datetime(2021, 1, 1, 16, 5) in start_points
        assert datetime(2021, 1, 1, 16, 15) in start_points
        assert datetime(2021, 1, 1, 16, 45) in start_points
    
    def test_schedule_task_for_one_full_hour_none_scheduled(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 4),
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)

        power_usage_function = PowerUsageFunction(
            [(timedelta(hours=0), 1)], extend_by=timedelta(hours=1)
        )
        task = Task(power_usage_function)

        schedule = Schedule([])

        # Act
        schedules = scheduler.schedule_task_for(task, schedule)
        schedules.sort(key=lambda x: x.get_total_price(spot_price_function))

        # Assert
        assert len(schedules) == 2
        assert schedules[0].get_total_price(spot_price_function) == 1
        assert schedules[1].get_total_price(spot_price_function) == 4