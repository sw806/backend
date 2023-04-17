from __future__ import annotations

from datetime import datetime, timedelta, timezone
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
    Scheduler, SpotPriceFunction,
    LowestPriceRecommender,
    TaskValidatorDisjunction, TaskValidatorConjunction,
    TaskValidator,
    TaskValidatorSplitter,
    TaskValidatorSplit
)


@dataclass
class DatetimeInterval:
    start: int
    duration: int

    @property
    def to_model(self) -> ModelDatetimeInterval:
        return ModelDatetimeInterval(
            datetime.fromtimestamp(self.start, timezone.utc),
            timedelta(seconds=self.duration)
        )
    
    @staticmethod
    def from_model(model: ModelDatetimeInterval) -> DatetimeInterval:
        return DatetimeInterval(
            # FIXME: Does this POSIX conversion give any errors?
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
    must_start_between: Optional[List[MustStartBetween]] = None
    must_end_between: Optional[List[MustEndBetween]] = None
    id: Optional[str] = None

    @property
    def to_model(self) -> ModelTask:
        power_usage_factory = PowerUsageFunctionFactory()
        power_usage_function = power_usage_factory.create_constant_consumption(
            timedelta(seconds=self.duration), self.power
        )

        # TODO: This should use the factory pattern.
        if self.must_start_between is None: self.must_start_between = []
        if self.must_end_between is None: self.must_end_between = []

        conjunctions: List[TaskValidator] = []
        if len(self.must_start_between) > 0:
            conjunctions.append(
                TaskValidatorDisjunction([ validator.to_validator for validator in self.must_start_between ])
            )

        if len(self.must_end_between) > 0:
            conjunctions.append(
                TaskValidatorDisjunction([ validator.to_validator for validator in self.must_end_between ])
            )

        conjunction = None if len(conjunctions) is None else TaskValidatorConjunction(conjunctions)


        return ModelTask(power_usage_function, conjunction, self.id)

    @staticmethod
    def from_model(model: ModelTask) -> Task:
        split = TaskValidatorSplit()
        if model.validator is not None:
            splitter = TaskValidatorSplitter()
            splitter.visit(model.validator)
            split = splitter.split
            must_start_between_validators = [MustStartBetween.from_validator(validator) for validator in split.must_start_between_validators]
            must_end_between_validators = [MustEndBetween.from_validator(validator) for validator in split.must_end_between_validators]

        return Task(
            id = model.id,
            duration = model.duration.seconds,
            # FIXME: Assumes constant power consumption as the value of the first point in the discrete function.
            power = model.power_usage_function.apply(
                model.power_usage_function.min_domain
            ),
            must_start_between = must_start_between_validators,
            must_end_between = must_end_between_validators,
        )

@dataclass
class ScheduledTask:
    task: Task
    start_interval: DatetimeInterval
    cost: float

    @property
    def to_model(self) -> ModelScheduledTask:
        return ModelScheduledTask(
            self.start_interval.to_model, self.task.to_model, self.cost
        )

    @staticmethod
    def from_model(model: ModelScheduledTask) -> ScheduledTask:
        return ScheduledTask(
            task = Task.from_model(model.task),
            start_interval = DatetimeInterval.from_model(model.start_interval),
            cost = model.cost
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
        # Get all price points.
        price_response = self.get_spot_prices.do(
            GetSpotPricesRequest(datetime.now(), ascending=True)
        )
        price_points = price_response.price_points

        # Create spot price function.
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

        # Get the recommendation.
        if len(new_schedules) == 0:
            recommendation = None
        else:
            # TODO: Recommender can be abstracted away as a dependecy on the abstract reommender class as a ctor parameter.
            lowest_price_recommender = LowestPriceRecommender(spot_price_function)
            recommendation = Schedule.from_model(
                lowest_price_recommender.recommend(new_schedules)
            )
        
        # Construct the response.
        return ScheduleTasksResponse(
            tasks=[],
            schedule=recommendation,
        )