from datetime import datetime, timedelta

from infrastructure.datetime_interval import DatetimeInterval
from infrastructure.must_start_between_validator import MustStartBetweenValidator
from infrastructure.power_usage_function import PowerUsageFunction
from infrastructure.task import Task


class TestTask():
    def test_start_times_no_validators(self):
        # Arrange
        power_function = PowerUsageFunction([
            (timedelta(), 1.2),
        ], timedelta(hours=1))
        task = Task(power_function)

        # Act
        datetimes = task.start_times()

        # Assert
        assert len(datetimes) == 0

    def test_start_times_one_validators(self):
        # Arrange
        datetime_interval = DatetimeInterval(datetime(2021, 1, 1, 15))
        must_start_between_validator = MustStartBetweenValidator(datetime_interval)
        power_function = PowerUsageFunction([
            (timedelta(), 1.2),
        ], timedelta(hours=1))
        task = Task(power_function, [must_start_between_validator])

        # Act
        datetimes = task.start_times()

        # Assert
        assert len(datetimes) == 1
        assert datetime_interval.start in datetimes

    def test_start_times_two_validators_contradicting(self):
        # Arrange
        datetime_interval_1 = DatetimeInterval(datetime(2021, 1, 1, 15))
        must_start_between_validator_1 = MustStartBetweenValidator(datetime_interval_1)
        datetime_interval_2 = DatetimeInterval(datetime(2021, 1, 1, 16))
        must_start_between_validator_2 = MustStartBetweenValidator(datetime_interval_2)
        power_function = PowerUsageFunction([
            (timedelta(), 1.2),
        ], timedelta(hours=1))
        task = Task(power_function, [must_start_between_validator_1, must_start_between_validator_2])

        # Act
        datetimes = task.start_times()

        # Assert
        assert len(datetimes) == 0
    
    def test_derieve_start_times_no_validators(self):
        # Arrange
        start_time = datetime(2021, 1, 1, 15)
        power_function = PowerUsageFunction([
            (timedelta(), 1.2),
        ], timedelta(hours=1))
        task = Task(power_function)

        # Act
        datetimes = task.derieve_start_times(start_time)

        # Assert
        assert len(datetimes) == 2
        assert start_time - power_function.duration in datetimes
        assert start_time in datetimes
    
    def test_derieve_start_times_with_a_must_start_before_validator(self):
        # Arrange
        start_time = datetime(2021, 1, 1, 15)
        datetime_interval = DatetimeInterval(start_time)
        must_start_between_validator = MustStartBetweenValidator(datetime_interval)
        power_function = PowerUsageFunction([
            (timedelta(), 1.2),
        ], timedelta(hours=1))
        task = Task(power_function, [must_start_between_validator])

        # Act
        datetimes = task.derieve_start_times(start_time)

        # Assert
        assert len(datetimes) == 1
        assert start_time in datetimes

    def test_derieve_start_times_must_have_all_starts_and_stops(self):
        # Arrange
        start_time = datetime(2021, 1, 1, 15)
        power_function = PowerUsageFunction([
            # Include start: 15
            # Include end:   14:30
            (timedelta(), 1),
            # Include start: 14:30
            # Include end:   14:00
            (timedelta(minutes=30), 2),
            # Include start: 14:00
            # Include end:   13:00
            (timedelta(hours=1), 3),
        ], timedelta(hours=1))
        task = Task(power_function)

        # Act
        datetimes = task.derieve_start_times(start_time)

        # Assert
        assert len(datetimes) == 4
        assert datetime(2021, 1, 1, 15) in datetimes
        assert datetime(2021, 1, 1, 14, 30) in datetimes
        assert datetime(2021, 1, 1, 14) in datetimes
        assert datetime(2021, 1, 1, 13) in datetimes

    def test_is_scheduleable_at_defaults_to_true(self):
        # Arrange
        start_time = datetime(2021, 1, 1, 15)
        power_function = PowerUsageFunction([
            (timedelta(), 1.2),
        ], timedelta(hours=1))
        task = Task(power_function)

        # Act
        scheduleable = task.is_scheduleable_at(start_time)

        # Assert
        assert scheduleable is True