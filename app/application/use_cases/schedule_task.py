from datetime import datetime, timedelta
from infrastructure import OptimalTimeCalculator
from application.use_cases.get_spot_price_task import GetSpotPricesUseCase, GetSpotPricesRequest, GetSpotPricesResponse
from pydantic.dataclasses import dataclass


@dataclass
class ScheduleTaskRequest:
    duration: int
    power: float

    def __init__(self, duration: int, power: float):
        self.duration = duration
        self.power = power

@dataclass
class ScheduleTaskResponse:
    def __init__(self, start_date: int):
        self.start_date = start_date

class ScheduleTaskUseCase:
    def __init__(self) -> None:
        pass

    def do(self, request: ScheduleTaskRequest) -> ScheduleTaskResponse:
        getSpotPricesUseCase = GetSpotPricesUseCase()
        price_points = getSpotPricesUseCase.do(GetSpotPricesRequest(datetime.now())).price_points
        optimal_time_calculator = OptimalTimeCalculator()
        optimal_time = optimal_time_calculator.calculate_optimal_time(price_points, timedelta(seconds=request.duration))
        return ScheduleTaskResponse(optimal_time)
