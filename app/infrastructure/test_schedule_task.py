from datetime import datetime, timedelta
from random import random
from typing import List

from infrastructure.power_price_function import PowerPriceFunction
from infrastructure.eletricity_prices import PricePoint
from infrastructure.spot_price_function import SpotPriceFunction
from infrastructure.schedule_task import ScheduledTask
from infrastructure.datetime_interval import DatetimeInterval
from infrastructure.power_usage_function import PowerUsageFunction
from infrastructure.task import Task


class TestScheduledTask():
    def test_end_interval(self):
        for _ in range(1000):
            # Arrange
            task_duration = timedelta(minutes=random() * 1000)
            start_duration = random() * task_duration
            power_function = PowerUsageFunction([
                (timedelta(), 1.2),
            ], task_duration)
            task = Task(power_function)

            start_datetime = datetime(2021, 1, 1, 15) 
            start_interval = DatetimeInterval(start_datetime, start_duration)
            scheduled_task = ScheduledTask(start_interval, task)

            expected = DatetimeInterval(
                start_datetime + task_duration,
                start_duration
            )

            # Act
            end_interval = scheduled_task.end_interval

            # Assert
            assert end_interval == expected
    
    def test_runs_at(self):
        for _ in range(1000):
            # Arrange
            task_duration = timedelta(minutes=random() * 1000)
            start_duration = random() * task_duration
            power_function = PowerUsageFunction([
                (timedelta(), 1.2),
            ], task_duration)
            task = Task(power_function)

            start_datetime = datetime(2021, 1, 1, 15) 
            start_interval = DatetimeInterval(start_datetime, start_duration)
            scheduled_task = ScheduledTask(start_interval, task)
            checked_datetime = start_datetime + ((random() * 2 - 1) * 2) * (start_duration + task_duration)

            # Act
            runs = scheduled_task.runs_at(checked_datetime)

            # Assert
            earliest_start_time = start_datetime
            last_end_time = start_datetime + start_duration + task_duration
            if checked_datetime < earliest_start_time:
                assert runs == False
            if checked_datetime >= earliest_start_time and checked_datetime < last_end_time:
                assert runs == True
            if checked_datetime >= last_end_time:
                assert runs == False

    def test_derieve_start_times_same_as_derieved_from_task_startime(self):
        # Arrange
        power_function = PowerUsageFunction([
            (timedelta(), 1.2),
        ], timedelta(hours=1))
        task = Task(power_function)

        start_datetime = datetime(2021, 1, 1, 15)
        start_duration = timedelta()
        start_interval = DatetimeInterval(start_datetime, start_duration)
        scheduled_task = ScheduledTask(start_interval, task)

        # Act
        datetimes = scheduled_task.derieve_start_times()

        # Assert
        assert datetimes == task.derieve_start_times(start_datetime)

    def test_get_max_power_consumption_at(self):
        # Arrange
        runtime_step = timedelta(minutes=1)
        consumption_points = [
            (runtime_step * 0, 6.0),
            (runtime_step * 1, 5.0),
            (runtime_step * 2, 4.0),
            (runtime_step * 3, 3.0),
            (runtime_step * 4, 2.0),
            (runtime_step * 5, 1.0),
        ]
        power_function = PowerUsageFunction(consumption_points, runtime_step)
        task = Task(power_function)

        start_datetime = datetime(2021, 1, 1, 15)
        start_duration = timedelta(minutes=3)
        start_interval = DatetimeInterval(start_datetime, start_duration)
        scheduled_task = ScheduledTask(start_interval, task)

        chosen_runtime = timedelta(minutes=random() * 3)
        chosen_datetime = start_datetime + chosen_runtime
        expected = power_function.apply(chosen_runtime)

        # Act
        actual = scheduled_task.get_max_power_consumption_at(chosen_datetime)

        # Assert
        assert actual == expected

    def test_get_max_total_price(self):
        for _ in range(100):
            # Arrange
            runtime_step = timedelta(minutes=1)
            consumption_points = [
                (runtime_step * 0, 6.0),
                (runtime_step * 1, 5.0),
                (runtime_step * 2, 4.0),
                (runtime_step * 3, 3.0),
                (runtime_step * 4, 2.0),
                (runtime_step * 5, 1.0),
            ]
            power_function = PowerUsageFunction(consumption_points, runtime_step)
            task = Task(power_function)

            start_datetime = datetime(2021, 1, 1, 15)
            start_duration = timedelta(minutes=random()*3)
            start_interval = DatetimeInterval(start_datetime, start_duration)
            scheduled_task = ScheduledTask(start_interval, task)

            price_points: List[PricePoint] = [
                PricePoint(start_datetime + runtime_step * 0, 1),
                PricePoint(start_datetime + runtime_step * 1, 2),
                PricePoint(start_datetime + runtime_step * 2, 3),
                PricePoint(start_datetime + runtime_step * 3, 4),
                PricePoint(start_datetime + runtime_step * 4, 5),
                PricePoint(start_datetime + runtime_step * 5, 6),
                PricePoint(start_datetime + runtime_step * 6, 7),
                PricePoint(start_datetime + runtime_step * 7, 8),
                PricePoint(start_datetime + runtime_step * 8, 9),
                PricePoint(start_datetime + runtime_step * 9, 10),
                PricePoint(start_datetime + runtime_step * 10, 11),
                PricePoint(start_datetime + runtime_step * 11, 12),
            ]
            spot_price_function = SpotPriceFunction(price_points)

            power_price_function = PowerPriceFunction(power_function, spot_price_function)
            expected = power_price_function.integrate_from_to(start_datetime + start_duration, task.duration)

            # Act
            actual = scheduled_task.get_max_total_price(spot_price_function)

            # Assert
            assert actual - expected < 0.1