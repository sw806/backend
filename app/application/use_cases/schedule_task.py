from datetime import datetime, timedelta
from infrastructure import OptimalTimeCalculator, EdsRequests
from pydantic.dataclasses import dataclass


@dataclass
class ScheduleTaskRequest:
    duration: int
    power: float

    def __init__(self, duration: int, power: float):
        self.duration = duration
        self.power = power

class ScheduleTaskResponse:
    def __init__(self, start_date: int):
        self.start_date = start_date

class ScheduleTaskUseCase:
    def __init__(self) -> None:
        pass

    def do(self, request: ScheduleTaskRequest) -> ScheduleTaskResponse:
        eds_requests = EdsRequests()
        price_points = eds_requests.get_prices(datetime.now())
        optimal_time_calculator = OptimalTimeCalculator()
        optimal_time = optimal_time_calculator.calculate_optimal_time(price_points, timedelta(seconds=request.duration))
        return ScheduleTaskResponse(optimal_time)