import datetime
from typing import Optional
from infrastructure import EdsRequests
from infrastructure import OptimalTimeCalculator
from pydantic.dataclasses import dataclass

@dataclass
class ScheduleTaskRequest:
    duration: int
    power: float

    def __init__(self, duration: Optional[int], power: Optional[float]):
        self.duration = duration
        self.power = power

class ScheduleTaskResponse:
    def __init__(self, start_date: int):
        self.start_date = start_date


class ScheduleTaskUseCase:
    def __init__(self) -> None:
        pass

    def do(self, request: ScheduleTaskRequest) -> ScheduleTaskResponse:
        price_points = EdsRequests().get_prices(datetime.datetime.now(), None)
        optimal_time = OptimalTimeCalculator()\
            .calculate_optimal_time(price_points, request.power, datetime.timedelta(seconds=request.duration))
        return ScheduleTaskResponse(optimal_time)