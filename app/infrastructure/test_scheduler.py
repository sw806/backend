from datetime import datetime, timedelta
from typing import List, Tuple

from infrastructure.scheduler import DatetimeInterval, Schedule, ScheduledTask, Scheduler, Task
from infrastructure.eletricity_prices import PricePoint
from infrastructure.spot_price_function import SpotPriceFunction
from infrastructure.power_usage_function import PowerUsageFunction


class TestScheduler:
    @classmethod
    def __contains_scheduled_task(cls, scheduled_tasks: List[ScheduledTask], scheduled_task: ScheduledTask) -> bool:
        for task in scheduled_tasks:
            if task.start_interval == scheduled_task.start_interval and \
                task.task == scheduled_task.task and \
                task.price == scheduled_task.price:
                return True
        return False

    def test_schedule_task_at_no_extension(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        task = Task(power_usage_function)

        # Act
        scheduled_tasks = scheduler.schedule_task_at(
            datetime(2021, 1, 1, 15), task
        )

        # Assert
        assert len(scheduled_tasks) == 1

    def test_schedule_task_at_one_hour_extension_single_task(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 1),
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        task = Task(power_usage_function)
        zero_extension_scheduled_task = ScheduledTask(
            DatetimeInterval(datetime(2021, 1, 1, 15), timedelta()), task, 1.0
        )
        one_hour_extension_scheduled_task = ScheduledTask(
            DatetimeInterval(datetime(2021, 1, 1, 15), timedelta(hours=1)), task, 1.0
        )

        # Act
        scheduled_tasks = scheduler.schedule_task_at(
            datetime(2021, 1, 1, 15), task
        )

        # Assert
        assert len(scheduled_tasks) == 2
        assert TestScheduler.__contains_scheduled_task(scheduled_tasks, zero_extension_scheduled_task)
        assert TestScheduler.__contains_scheduled_task(scheduled_tasks, one_hour_extension_scheduled_task)

    def test_schedule_task_at_one_hour_extension_single_task_different_intervals(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 1),
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
        ]
        power_usage_function = PowerUsageFunction(power_points, extend_by=timedelta(minutes=30))
        task = Task(power_usage_function)
        zero_extension_scheduled_task = ScheduledTask(
            DatetimeInterval(datetime(2021, 1, 1, 15), timedelta()), task, 0.5
        )
        haft_hour_extension_scheduled_task = ScheduledTask(
            DatetimeInterval(datetime(2021, 1, 1, 15), timedelta(minutes=30)), task, 0.5
        )
        one_hour_extension_scheduled_task = ScheduledTask(
            DatetimeInterval(datetime(2021, 1, 1, 15), timedelta(hours=1)), task, 0.5
        )
        one_and_a_haft_hours_extension_scheduled_task = ScheduledTask(
            DatetimeInterval(datetime(2021, 1, 1, 15), timedelta(hours=1, minutes=30)), task, 0.5
        )

        # Act
        scheduled_tasks = scheduler.schedule_task_at(
            datetime(2021, 1, 1, 15), task
        )

        # Assert
        assert len(scheduled_tasks) == 4
        assert TestScheduler.__contains_scheduled_task(scheduled_tasks, zero_extension_scheduled_task)
        assert TestScheduler.__contains_scheduled_task(scheduled_tasks, haft_hour_extension_scheduled_task)
        assert TestScheduler.__contains_scheduled_task(scheduled_tasks, one_hour_extension_scheduled_task)
        assert TestScheduler.__contains_scheduled_task(scheduled_tasks, one_and_a_haft_hours_extension_scheduled_task)

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
        schedules = scheduler.schedule_task_for(Schedule(), task)

        # Assert
        assert len(schedules) == 3

    def test_schedule_tasks(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 15, 30), 5),
            PricePoint(datetime(2021, 1, 1, 16), 2),
            PricePoint(datetime(2021, 1, 1, 17), 3)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(spot_price_function)
        power_points_1: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
        ]
        power_usage_function_1 = PowerUsageFunction(power_points_1)
        task_1 = Task(power_usage_function_1)
        power_points_2: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 2),
        ]
        power_usage_function_2 = PowerUsageFunction(power_points_2)
        task_2 = Task(power_usage_function_2)
        tasks = [task_1, task_2]

        # Act
        schedules = scheduler.schedule_tasks(tasks)

        # Assert
        assert len(schedules) == 8