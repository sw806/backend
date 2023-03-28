from typing import List, Optional
from pydantic.dataclasses import dataclass

from application.use_cases.get_spot_price_task import GetSpotPricesRequest, GetSpotPricesResponse
from application.use_cases.use_Case import UseCase

@dataclass
class DatetimeInterval:
    start: int
    duration: float

@dataclass
class MaximumPowerConsumption:
    maximum_consumption: float

@dataclass
class MustStartBetween:
    start_interval: DatetimeInterval

@dataclass
class MustEndBetween:
    end_interval: DatetimeInterval

@dataclass
class Task:
    duration: int
    power: float
    must_start_between: Optional[MustStartBetween] = None
    must_end_between: Optional[MustEndBetween] = None

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