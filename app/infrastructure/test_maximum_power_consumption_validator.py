from datetime import datetime, timedelta, timezone

from infrastructure.must_end_between_validator import MustEndBetweenValidator
from infrastructure.power_usage_function_factory import PowerUsageFunctionFactory
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

    def test_maximum_power_consumption_validator_checks_times_after_task_start(self):
        # Arrange

        # This should not be possible if both tasks uses 1Kw and max consumption is 1Kw.
        # "1" starts at 2021-01-01 17:00:00 and ends at 2021-01-01 18:00:00
        # "2" starts at 2021-01-01 16:00:00 and ends at 2021-01-01 17:15:00

        power_function_1 = PowerUsageFunctionFactory().create_constant_consumption(timedelta(minutes=60), 1)
        task_1 = Task(power_function_1, id="1")
        scheduled_task_1 = ScheduledTask(
            DatetimeInterval(datetime(2021, 1, 1, 17), timedelta()),
            task_1,
            1
        )

        schedule = Schedule([scheduled_task_1])

        power_function_2 = PowerUsageFunctionFactory().create_constant_consumption(timedelta(minutes=75), 1)
        task_2 = Task(power_function_2, id="2")

        validator = MaximumPowerConsumptionValidator(1)

        # Act
        valid = validator.validate(
            schedule, task_2, datetime(2021, 1, 1, 16)
        )

        # Assert
        assert not valid

    def test_maximum_power_consumption_end_right_before_next_starts(self):
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

        # Act
        valid = schedule.can_schedule_task_at(
            task_2, datetime(2021, 1, 1, 15, 45)
        )

        # Assert
        assert valid

    def test_variable_power_consuming_task_exceeds_power_consumption(self):
        # Arrange
        power_usage_function = PowerUsageFunctionFactory().create_variable_consumption(
            [(timedelta(), 1), (timedelta(minutes=5), 2)], timedelta(minutes=5)
        )
        task = Task(power_usage_function)

        validator = MaximumPowerConsumptionValidator(1)
        schedule = Schedule([], validator)

        # Act
        valid = schedule.can_schedule_task_at(
            task, datetime.now(tz=timezone.utc)
        )

        # Assert
        assert not valid
    
    def test_long_constant_power_consuming_task(self):
        # Arrange

        # "1" starts at 2021-01-01 14:00:00 and ends at 2021-01-01 19:00:00 : 1681819200
        # "2" starts at 2021-01-01 13:00:00 and ends at 2021-01-01 18:00:00 : 1681815600

        power_function_1 = PowerUsageFunctionFactory().create_constant_consumption(
            timedelta(hours=5), 2
        )
        task_1 = Task(power_function_1)
        scheduled_task_1 = ScheduledTask(
            DatetimeInterval(datetime.fromtimestamp(1681819200), timedelta(hours=0)), task_1, 0
        )

        power_function_2 = PowerUsageFunctionFactory().create_constant_consumption(
            timedelta(hours=5), 2
        )
        task_2 = Task(power_function_2)

        validator = MaximumPowerConsumptionValidator(2)
        schedule = Schedule([scheduled_task_1], validator)
        
        # Act
        valid = schedule.can_schedule_task_at(
            task_2, datetime.fromtimestamp(1681815600)
        )

        # Assert
        assert not valid