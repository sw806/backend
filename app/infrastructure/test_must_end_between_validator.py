from datetime import datetime, timedelta
from random import random

import pytest

from infrastructure.datetime_interval import DatetimeInterval
from infrastructure.must_end_between_validator import MustEndBetweenValidator
from infrastructure.task import Task
from infrastructure.power_usage_function import PowerUsageFunction


class TestMustStartBetweenValidator():
    def test_start_times_no_interval_duration(self):
        # Arrange
        datetime_interval = DatetimeInterval(datetime(2021, 1, 1, 15))
        must_start_between_validator = MustEndBetweenValidator(datetime_interval)
        power_usage_function = PowerUsageFunction(
            [(timedelta(hours=0), 1)], extend_by=timedelta(minutes=30)
        )
        task = Task(power_usage_function, must_start_between_validator)
        
        # Act
        start_times = must_start_between_validator.start_times(task)

        # Assert
        assert len(start_times) == 1
        assert datetime_interval.start - power_usage_function.duration in start_times

    def test_start_times_exact_equal_size_interval_duration(self):
        # Arrange
        power_usage_function = PowerUsageFunction(
            [(timedelta(hours=0), 1)], extend_by=timedelta(minutes=30)
        )
        datetime_interval = DatetimeInterval(datetime(2021, 1, 1, 15), power_usage_function.duration)
        must_start_between_validator = MustEndBetweenValidator(datetime_interval)
        task = Task(power_usage_function, must_start_between_validator)
        
        # Act
        start_times = must_start_between_validator.start_times(task)

        # Assert
        assert len(start_times) == 2
        assert datetime_interval.start - power_usage_function.duration in start_times
        assert datetime_interval.end - power_usage_function.duration in start_times

    def test_start_times_exactly_half_size_interval_duration(self):
        # Arrange
        power_usage_function = PowerUsageFunction(
            [(timedelta(hours=0), 1)], extend_by=timedelta(minutes=15)
        )
        datetime_interval = DatetimeInterval(datetime(2021, 1, 1, 15), power_usage_function.duration * 2)
        must_start_between_validator = MustEndBetweenValidator(datetime_interval)
        task = Task(power_usage_function, must_start_between_validator)
        
        # Act
        start_times = must_start_between_validator.start_times(task)

        # Assert
        assert len(start_times) == 3
        assert datetime_interval.start - power_usage_function.duration in start_times
        assert datetime_interval.start - power_usage_function.duration + datetime_interval.duration / 2 in start_times
        assert datetime_interval.end - power_usage_function.duration in start_times

    def test_start_times_varying_size_interval_duration(self):
        # Arrange
        power_usage_function = PowerUsageFunction(
            [(timedelta(hours=0), 1)], extend_by=timedelta(minutes=15)
        )
        datetime_interval = DatetimeInterval(datetime(2021, 1, 1, 15), power_usage_function.duration * 3)
        must_start_between_validator = MustEndBetweenValidator(datetime_interval)
        task = Task(power_usage_function, must_start_between_validator)
        
        # Act
        start_times = must_start_between_validator.start_times(task)

        # Assert
        assert len(start_times) == 4
        assert datetime_interval.start - power_usage_function.duration in start_times
        assert datetime_interval.start - power_usage_function.duration + power_usage_function.duration in start_times
        assert datetime_interval.end - power_usage_function.duration - power_usage_function.duration in start_times
        assert datetime_interval.end - power_usage_function.duration in start_times

    def test_validate_must_end_between(self):
        for _ in range(1000):
            # Arrange
            power_usage_function = PowerUsageFunction(
                [(timedelta(hours=0), 1)], extend_by=timedelta(minutes=15)
            )
            
            start_datetime = datetime(2021, 1, 1, 15)
            start_duration = timedelta(minutes=5)
            datetime_interval = DatetimeInterval(start_datetime + power_usage_function.duration, start_duration)

            must_start_between_validator = MustEndBetweenValidator(datetime_interval)
            task = Task(power_usage_function, must_start_between_validator)
            
            # Act
            seconds = int(random() * 2000 - 1000)
            checked_time = start_datetime - timedelta(seconds=seconds)
            valid = must_start_between_validator.validate(task, checked_time)

            # Assert
            min_start_time = datetime_interval.start - task.duration
            max_start_time = datetime_interval.end - task.duration
            if checked_time < min_start_time:
                assert valid is False
            if checked_time >= min_start_time and checked_time <= max_start_time:
                assert valid is True
            if checked_time > max_start_time:
                assert valid is False