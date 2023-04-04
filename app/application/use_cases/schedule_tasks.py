from datetime import datetime, timedelta
import sys
from typing import List, Optional
from pydantic.dataclasses import dataclass

from infrastructure import (
    TaskValidator, MustStartBetweenValidator
)
from infrastructure.datetime_interval import DatetimeInterval as ModelDatetimeInterval
from application.use_cases.get_spot_price_task import GetSpotPricesRequest, GetSpotPricesResponse
from application.use_cases.use_Case import UseCase

@dataclass
class DatetimeInterval:
    start: int
    duration: int

@dataclass
class MaximumPowerConsumption:
    maximum_consumption: float

@dataclass
class TaskInterval:
    earliest_start: int
    latest_start: Optional[int]

    @property
    def validator(self) -> TaskValidator:
        earliest_datetime = datetime.fromtimestamp(self.earliest_start)
        duration = timedelta(seconds=sys.maxsize)
        if not self.latest_start is None:
            latest_datetime = datetime.fromtimestamp(self.latest_start)
            duration = latest_datetime - earliest_datetime
        return MustStartBetweenValidator(
            ModelDatetimeInterval(earliest_datetime, duration)
        )

@dataclass
class Task:
    duration: int
    power: float
    must_start_between: List[TaskInterval]

@dataclass
class ScheduledTask:
    task: Task
    start_interval: DatetimeInterval

@dataclass
class Schedule:
    tasks: List[ScheduledTask]
    maximum_power_consumption: Optional[MaximumPowerConsumption] = None

@dataclass
class ScheduleTasksRequest:
    tasks: List[Task]
    schedule: Optional[Schedule] = None

class ScheduleTasksResponse:
    def __init__(
        self,
    ) -> None:
        pass

class ScheduleTasksUseCase(UseCase[ScheduleTasksRequest, ScheduleTasksResponse]):
    def __init__(
        self,
        get_spot_prices: UseCase[GetSpotPricesRequest, GetSpotPricesResponse],
    ) -> None:
        self.get_spot_prices = get_spot_prices

    def do(self, request: ScheduleTasksRequest) -> ScheduleTasksResponse:
        # print(request)

        # Get all price points.
        # price_response = self.get_spot_prices.do(
        #     GetSpotPricesRequest(datetime.now())
        # )
        # price_points = price_response.price_points
        # print(price_points)

        # Create schedule.
        # self.scheduler.schedule_tasks()

        return ScheduleTasksResponse()