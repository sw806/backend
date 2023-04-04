from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional
from pydantic.dataclasses import dataclass

from application.use_cases.get_spot_price_task import GetSpotPricesRequest, GetSpotPricesResponse
from application.use_cases.use_Case import UseCase
from infrastructure import (
    MaximumPowerConsumptionValidator,
    MustStartBetweenValidator,
    MustEndBetweenValidator,
    Task as ModelTask,
    PowerUsageFunctionFactory,
    ScheduledTask as ModelScheduledTask,
    Schedule as ModelSchedule,
    DatetimeInterval as ModelDatetimeInterval,
    Scheduler, SpotPriceFunction
)


@dataclass
class DatetimeInterval:
    start: int
    duration: int

    @property
    def to_model(self) -> ModelDatetimeInterval:
        return ModelDatetimeInterval(
            datetime.fromtimestamp(self.start),
            timedelta(seconds=self.duration)
        )
    
    @staticmethod
    def from_model(model: ModelDatetimeInterval) -> DatetimeInterval:
        return DatetimeInterval(
            # FIXME: Does this pPOSIX conversion give any errors?
            start=int(model.start.timestamp()),
            duration=model.duration.seconds
        )

@dataclass
class MaximumPowerConsumption:
    maximum_consumption: float

    @property
    def to_validator(self) -> MaximumPowerConsumptionValidator:
        return MaximumPowerConsumptionValidator(self.maximum_consumption)

    @staticmethod
    def from_validator(model: MaximumPowerConsumptionValidator) -> MaximumPowerConsumption:
        return MaximumPowerConsumption(
            maximum_consumption = model.maximum_consumption
        )

@dataclass
class MustStartBetween:
    start_interval: DatetimeInterval

    @property
    def to_validator(self) -> MustStartBetweenValidator:
        return MustStartBetweenValidator(self.start_interval.to_model)

    @staticmethod
    def from_validator(model: MustStartBetweenValidator) -> MustStartBetween:
        return MustStartBetween(
            start_interval = DatetimeInterval.from_model(model.start_time_interval)
        )

@dataclass
class MustEndBetween:
    end_interval: DatetimeInterval

    @property
    def to_validator(self) -> MustEndBetweenValidator:
        return MustEndBetweenValidator(self.end_interval.to_model)

    @staticmethod
    def from_validator(model: MustEndBetweenValidator) -> MustEndBetween:
        return MustEndBetween(
            end_interval = DatetimeInterval.from_model(model.end_time_interval)
        )

@dataclass
class Task:
    duration: int
    power: float
    must_start_between: List[MustStartBetween]
    must_end_between: List[MustEndBetween]

    @property
    def to_model(self) -> ModelTask:
        power_usage_factory = PowerUsageFunctionFactory()
        power_usage_function = power_usage_factory.create_constant_consumption(
            timedelta(minutes=self.duration), self.power
        )

        # FIXME: This should get all possible permutations of the validators.

        return ModelTask(
            power_usage_function,
            None
        )

    @staticmethod
    def from_model(model: ModelTask) -> Task:
        return Task(
            duration = int(model.duration.seconds / 60),
            # FIXME: Assumes constant power consumption as the value of the first point in the discrete function.
            power = model.power_usage_function.apply(
                model.power_usage_function.min_domain
            ),
            # FIXME: Correct set the must start/end between validators.
            must_start_between = [],
            must_end_between = [],
        )

@dataclass
class ScheduledTask:
    task: Task
    start_interval: DatetimeInterval

    @property
    def to_model(self) -> ModelScheduledTask:
        return ModelScheduledTask(
            self.start_interval.to_model, self.task.to_model
        )

    @staticmethod
    def from_model(model: ModelScheduledTask) -> ScheduledTask:
        return ScheduledTask(
            task = Task.from_model(model.task),
            start_interval = DatetimeInterval.from_model(model.start_interval)
        )

@dataclass
class Schedule:
    tasks: List[ScheduledTask]
    maximum_power_consumption: Optional[MaximumPowerConsumption] = None

    @property
    def to_model(self) -> ModelSchedule:
        task_models = [task.to_model for task in self.tasks]
        power_consumption_validator = None
        if self.maximum_power_consumption is not None:
            power_consumption_validator = self.maximum_power_consumption.to_validator
        return ModelSchedule(task_models, power_consumption_validator)

    @staticmethod
    def from_model(model: ModelSchedule) -> Schedule:
        return Schedule(
            tasks = [ScheduledTask.from_model(task) for task in model.tasks],
            # FIXME: Correct set maximum power consumption constraint.
            maximum_power_consumption = None
        )

@dataclass
class ScheduleTasksRequest:
    tasks: List[Task]
    schedule: Optional[Schedule] = None

    @property
    def task_models(self) -> List[ModelTask]:
        return [task.to_model for task in self.tasks]

    @property
    def schedule_model(self) -> Optional[ModelSchedule]:
        if self.schedule is None:
            return None
        return self.schedule.to_model

@dataclass
class ScheduleTasksResponse:
    tasks: List[Task]
    schedule: Optional[Schedule] = None

class ScheduleTasksUseCase(UseCase[ScheduleTasksRequest, ScheduleTasksResponse]):
    def __init__(
        self,
        get_spot_prices: UseCase[GetSpotPricesRequest, GetSpotPricesResponse],
    ) -> None:
        self.get_spot_prices = get_spot_prices

    def do(self, request: ScheduleTasksRequest) -> ScheduleTasksResponse:
        print(request)

        # Get all price points.
        price_response = self.get_spot_prices.do(
            GetSpotPricesRequest(datetime.now())
        )
        price_points = price_response.price_points
        print(price_points)

        # Create spot price function
        spot_price_function = SpotPriceFunction(price_points)

        # Create scheduler and base schedule.
        scheduler = Scheduler(spot_price_function)
        base_schedule = request.schedule_model
        if base_schedule is None:
            base_schedule = ModelSchedule()

        # Schedule new schedule.
        new_schedules = scheduler.schedule_tasks(
            request.task_models, base_schedule
        )

        # TODO: Create recommendation engine to choose cheapest schedule.
        
        # FIXME: Takes the first schedule and assumes it to be the cheapest.
        return ScheduleTasksResponse(
            tasks=[],
            schedule=Schedule.from_model(new_schedules[0]),
        )