from datetime import datetime, timedelta
from typing import List, Tuple

from infrastructure.scheduler import Schedule, Scheduler, Task
from infrastructure.eletricity_prices import PricePoint
from infrastructure.spot_price_function import SpotPriceFunction
from infrastructure.power_usage_function import PowerUsageFunction


class TestScheduler:
    def test_schedule_task_at_start_no_scheduled_task_duration(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 2),
            PricePoint(datetime(2021, 1, 1, 17), 3)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        task = Task(power_usage_function)

        # Act
        scheduled_task = scheduler.schedule_task_at(datetime(2021, 1, 1, 15), task)

        # Assert
        if scheduled_task is None: assert False
        assert scheduled_task.start_interval.duration == timedelta(hours=0)

    def test_schedule_task_at_start_one_hour_scheduled_task_duration(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 17), 2)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        task = Task(power_usage_function)

        # Act
        scheduled_task = scheduler.schedule_task_at(datetime(2021, 1, 1, 15), task)

        # Assert
        if scheduled_task is None: assert False
        assert scheduled_task.start_interval.duration == timedelta(hours=1)

    def test_schedule_task_at_start_scheduled_task_duration_is_max(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 17), 1)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        task = Task(power_usage_function)

        # Act
        scheduled_task = scheduler.schedule_task_at(datetime(2021, 1, 1, 15), task)

        # Assert
        if scheduled_task is None: assert False
        assert scheduled_task.start_interval.duration == timedelta(hours=2)

    def test_schedule_task_at_start_one_hour_scheduled_task_duration_even_though_it_is_cheaper(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 2),
            PricePoint(datetime(2021, 1, 1, 17), 1)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        task = Task(power_usage_function)

        # Act
        scheduled_task = scheduler.schedule_task_at(datetime(2021, 1, 1, 15), task)

        # Assert
        if scheduled_task is None: assert False
        assert scheduled_task.start_interval.duration == timedelta(hours=1)

    def test_schedule_creates_all_possible_schedules(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 2),
            PricePoint(datetime(2021, 1, 1, 17), 3)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        task = Task(power_usage_function)

        # Act
        schedules = scheduler.schedule_helper(Schedule(), task)

        # Assert
        assert len(schedules) == 3