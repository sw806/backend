from datetime import datetime, timedelta
from typing import List

from infrastructure.maximum_power_consumption_validator import MaximumPowerConsumptionValidator
from infrastructure.power_usage_function_factory import PowerUsageFunctionFactory
from infrastructure.task_validator_conjunction import TaskValidatorConjunction
from infrastructure.must_end_between_validator import MustEndBetweenValidator
from infrastructure.must_start_between_validator import MustStartBetweenValidator
from infrastructure.datetime_interval import DatetimeInterval
from infrastructure.schedule import Schedule
from infrastructure.schedule_task import ScheduledTask
from infrastructure.scheduler import Scheduler
from infrastructure.task import Task
from infrastructure.power_usage_function import PowerUsageFunction
from domain import PricePoint
from infrastructure.spot_price_function import SpotPriceFunction


class TestScheduler:
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
            DatetimeInterval(datetime(2021, 1, 1, 16, 15), timedelta()), task, 0
        )
        schedule = Schedule([scheduled_task])

        # Act
        start_points = scheduler.get_all_possible_start_times(task, schedule)

        # Assert
        assert len(start_points) == 7
        assert datetime(2021, 1, 1, 15) in start_points
        assert datetime(2021, 1, 1, 15, 15) in start_points
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
            DatetimeInterval(datetime(2021, 1, 1, 16, 15), timedelta()), task, 0
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
            DatetimeInterval(datetime(2021, 1, 1, 16, 15), timedelta()), task, 0
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
        assert len(start_points) == 5
        assert datetime(2021, 1, 1, 15) in start_points
        assert datetime(2021, 1, 1, 15, 45) in start_points
        assert datetime(2021, 1, 1, 15, 55) in start_points
        assert datetime(2021, 1, 1, 16) in start_points
        assert datetime(2021, 1, 1, 16, 45) in start_points
    
    def test_get_available_start_times_variable_power_consumption_with_start_constraint(self):
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
        must_start_between_validator = MustStartBetweenValidator(
            DatetimeInterval(datetime(2021, 1, 1, 15), timedelta(hours=1))
        )
        task = Task(power_usage_function, must_start_between_validator)

        schedule = Schedule([])

        # Act
        start_points = scheduler.get_all_possible_start_times(task, schedule)

        # Assert
        assert len(start_points) == 10
        assert datetime(2021, 1, 1, 15) in start_points
        assert datetime(2021, 1, 1, 15, 5) in start_points
        assert datetime(2021, 1, 1, 15, 10) in start_points
        assert datetime(2021, 1, 1, 15, 15) in start_points
        assert datetime(2021, 1, 1, 15, 30) in start_points
        assert datetime(2021, 1, 1, 15, 40) in start_points
        assert datetime(2021, 1, 1, 15, 45) in start_points
        assert datetime(2021, 1, 1, 15, 50) in start_points
        assert datetime(2021, 1, 1, 15, 55) in start_points
        assert datetime(2021, 1, 1, 16) in start_points

    
    def test_get_available_start_times_variable_power_consumption_with_start_and_end_constraint(self):
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
        must_start_between_validator = MustStartBetweenValidator(
            DatetimeInterval(datetime(2021, 1, 1, 15, 55), timedelta(minutes=15))
        )
        must_end_between_validator = MustEndBetweenValidator(
            DatetimeInterval(datetime(2021, 1, 1, 16, 10), timedelta(minutes=5))
        )
        task = Task(
            power_usage_function,
            TaskValidatorConjunction([must_start_between_validator, must_end_between_validator])
        )

        schedule = Schedule([])

        # Act
        start_points = scheduler.get_all_possible_start_times(task, schedule)

        # Assert
        assert len(start_points) == 2
        assert datetime(2021, 1, 1, 15, 55) in start_points
        assert datetime(2021, 1, 1, 16) in start_points
    
    def test_get_available_start_times_variable_power_consumption_with_start_constraint_offsetted(self):
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
        must_start_between_validator = MustStartBetweenValidator(
            DatetimeInterval(datetime(2021, 1, 1, 15, 30), timedelta(minutes=15))
        )
        task = Task(
            power_usage_function, must_start_between_validator
        )

        schedule = Schedule([])

        # Act
        start_points = scheduler.get_all_possible_start_times(task, schedule)

        # Assert
        assert len(start_points) == 4
        assert datetime(2021, 1, 1, 15, 30) in start_points
        assert datetime(2021, 1, 1, 15, 30) in start_points
        assert datetime(2021, 1, 1, 15, 35) in start_points
        assert datetime(2021, 1, 1, 15, 45) in start_points

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

        schedule = Schedule()

        # Act
        schedules = scheduler.schedule_task_for(task, schedule)
        schedules.sort(key=lambda x: x.get_total_price(spot_price_function))

        # Assert
        assert len(schedules) == 2
        assert schedules[0].get_total_price(spot_price_function) == 1
        assert schedules[1].get_total_price(spot_price_function) == 4

    def test_end_constraint_and_max_consumption_start_and_end_same_time(self):
        # Arrange

        # "1" starts at 2021-01-01 17:00:00 and ends at 2021-01-01 18:00:00
        # "2" starts at 2021-01-01 15:45:00 and ends at 2021-01-01 17:00:00

        power_function_1 = PowerUsageFunctionFactory().create_constant_consumption(timedelta(minutes=60), 1)
        task_1 = Task(power_function_1, id="1")
        scheduled_task_1 = ScheduledTask(
            DatetimeInterval(datetime(2021, 1, 1, 17), timedelta()),
            task_1,
            1
        )

        power_function_2 = PowerUsageFunctionFactory().create_constant_consumption(timedelta(minutes=75), 1)
        must_end_between_2 = MustEndBetweenValidator(
            DatetimeInterval(scheduled_task_1.start_interval.start, timedelta())
        )
        task_2 = Task(power_function_2, must_end_between_2, "2")

        validator = MaximumPowerConsumptionValidator(1)
        schedule = Schedule([scheduled_task_1], validator)

        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 1),
            PricePoint(datetime(2021, 1, 1, 17), 1),
            PricePoint(datetime(2021, 1, 1, 18), 1),
        ]
        scheduler = Scheduler(
            SpotPriceFunction(price_points)
        )

        # Act
        start_points = scheduler.get_all_possible_start_times(
            task_2, schedule
        )
        valid = schedule.can_schedule_task_at(
            task_2, datetime(2021, 1, 1, 15, 45)
        )

        # Assert
        assert datetime(2021, 1, 1, 15, 45) in start_points
        assert valid

    def test_len_schedules_from_scheduler(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        scheduler = Scheduler(
            SpotPriceFunction(price_points)
        )

        power_function_1 = PowerUsageFunctionFactory().create_constant_consumption(timedelta(minutes=60), 1)
        task_1 = Task(power_function_1, id="1")

        power_function_2 = PowerUsageFunctionFactory().create_constant_consumption(timedelta(minutes=60), 1)
        task_2 = Task(power_function_2, id="2")

        power_function_3 = PowerUsageFunctionFactory().create_constant_consumption(timedelta(minutes=60), 1)
        task_3 = Task(power_function_3, id="3")

        # Act
        schedules = scheduler.schedule_tasks([task_1, task_2, task_3])

        # Assert
        assert len(schedules) == 6