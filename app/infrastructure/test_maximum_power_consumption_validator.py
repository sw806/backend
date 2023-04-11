from datetime import datetime, timedelta

from infrastructure.schedule import Schedule
from infrastructure.datetime_interval import DatetimeInterval
from infrastructure.maximum_power_consumption_validator import MaximumPowerConsumptionValidator
from infrastructure.power_usage_function import PowerUsageFunction
from infrastructure.schedule_task import ScheduledTask
from infrastructure.task import Task


class TestMaximumPowerConsumptionValidator:
    def test_power_consumption_at_single_task_at_start(self):
        # Arrange
        expected = 0
        power_function = PowerUsageFunction([
            (timedelta(), expected),
            (timedelta(minutes=20), 1),
        ], timedelta(hours=1))
        validator = MaximumPowerConsumptionValidator(3)
        task0 = ScheduledTask(
            DatetimeInterval(datetime(2021, 12, 19), timedelta()),
            Task(power_function),
            0
        )

        # Act
        actual = validator.power_consumption_at(
            [task0], datetime(2021, 12, 19)
        )

        # Assert
        assert actual == expected

    def test_power_consumption_at_single_task_at_second_point(self):
        # Arrange
        expected = 0
        power_function = PowerUsageFunction([
            (timedelta(), 0),
            (timedelta(minutes=20), expected),
        ], timedelta(hours=1))
        validator = MaximumPowerConsumptionValidator(3)
        task0 = ScheduledTask(
            DatetimeInterval(datetime(2021, 12, 19), timedelta()),
            Task(power_function),
            0
        )

        # Act
        actual = validator.power_consumption_at(
            [task0], datetime(2021, 12, 19) + timedelta(minutes=20)
        )

        # Assert
        assert actual == expected

    def test_power_consumption_at_single_task_at_end(self):
        # Arrange
        power_function = PowerUsageFunction([
            (timedelta(), 0),
            (timedelta(minutes=20), 1),
        ], timedelta(hours=1))
        validator = MaximumPowerConsumptionValidator(3)
        task0 = ScheduledTask(
            DatetimeInterval(datetime(2021, 12, 19), timedelta()),
            Task(power_function),
            0
        )

        # Act
        actual = validator.power_consumption_at(
            [task0], task0.end_interval.end
        )

        # Assert
        assert actual == 0

    def test_next_power_consumption_from_at_single_task_at_start(self):
        # Arrange
        expected = datetime(2021, 12, 19) + timedelta(minutes=20)
        power_function = PowerUsageFunction([
            (timedelta(), 0),
            (timedelta(minutes=20), 1),
        ], timedelta(hours=1))
        validator = MaximumPowerConsumptionValidator(3)
        task0 = ScheduledTask(
            DatetimeInterval(datetime(2021, 12, 19), timedelta()),
            Task(power_function),
            0
        )

        # Act
        actual = validator.next_power_consumption_from(
            [task0], datetime(2021, 12, 19)
        )

        # Assert
        assert actual == expected

    def test_next_power_consumption_from_at_single_task_at_second_point(self):
        # Arrange
        power_function = PowerUsageFunction([
            (timedelta(), 0),
            (timedelta(minutes=20), 1),
        ], timedelta(hours=1))
        validator = MaximumPowerConsumptionValidator(3)
        task0 = ScheduledTask(
            DatetimeInterval(datetime(2021, 12, 19), timedelta()),
            Task(power_function),
            0
        )

        # Act
        actual = validator.next_power_consumption_from(
            [task0], datetime(2021, 12, 19) + timedelta(minutes=20)
        )

        # Assert
        assert actual == None

    def test_next_power_consumption_from_at_single_task_at_end(self):
        # Arrange
        power_function = PowerUsageFunction([
            (timedelta(), 0),
            (timedelta(minutes=20), 1),
        ], timedelta(hours=1))
        validator = MaximumPowerConsumptionValidator(3)
        task0 = ScheduledTask(
            DatetimeInterval(datetime(2021, 12, 19), timedelta()),
            Task(power_function),
            0
        )

        # Act
        actual = validator.next_power_consumption_from(
            [task0], task0.end_interval.end
        )

        # Assert
        assert actual is None

    def test_validate_does_exceed(self):
        # Arrange
        power_function = PowerUsageFunction([
            (timedelta(), 1.2),
        ], timedelta(hours=1))
        validator = MaximumPowerConsumptionValidator(3)
        task0 = ScheduledTask(
            DatetimeInterval(datetime(2021, 12, 19, 10), timedelta()),
            Task(power_function),
            0
        )
        task1 = ScheduledTask(
            DatetimeInterval(datetime(2021, 12, 19, 10), timedelta()),
            Task(power_function),
            0
        )
        schedule = Schedule([task0, task1])
        task = Task(power_function)

        # Act
        actual = validator.validate(schedule, task, datetime(2021, 12, 19, 10))

        # Assert
        assert actual == False

    def test_validate_does_not_exceed(self):
        # Arrange
        power_function = PowerUsageFunction([
            (timedelta(), 1.2),
        ], timedelta(hours=1))
        validator = MaximumPowerConsumptionValidator(3)
        task0 = ScheduledTask(
            DatetimeInterval(datetime(2021, 12, 19, 10), timedelta()),
            Task(power_function),
            0
        )
        task1 = ScheduledTask(
            DatetimeInterval(datetime(2021, 12, 19, 10), timedelta()),
            Task(power_function),
            0
        )
        schedule = Schedule([task0, task1])
        task = Task(power_function)

        # Act
        actual = validator.validate(schedule, task, datetime(2021, 12, 19, 11))

        # Assert
        assert actual == True