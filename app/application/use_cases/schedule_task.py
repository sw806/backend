from datetime import datetime
from typing import Optional
from infrastructure import EdsRequests
from infrastructure import OptimalTimeCalculator
from pydantic import BaseModel

class ScheduleTaskRequest(BaseModel):
    def __init__(self, duration: Optional[int], energy: Optional[float],
                 power: Optional[float]):
        self.duration = duration
        self.energy = energy
        self.power = power


class ScheduleTaskResponse(BaseModel):
    def __init__(self, start_date: int):
        self.start_date = start_date


class ScheduleTaskUseCase:
    def __init__(self) -> None:
        pass

    def do(self, request: ScheduleTaskRequest) -> ScheduleTaskResponse:
        price_points = EdsRequests().get_prices(datetime.now(), None)
        optimal_time = OptimalTimeCalculator()\
            .calculate_optimal_time(price_points, request.energy, request.power, request.duration)
        print("Optimal start time: ", optimal_time)
        return ScheduleTaskResponse(optimal_time)


if __name__ == "__main__":
    request = ScheduleTaskRequest(3, 1, None)
    response = ScheduleTaskUseCase().do(request)
    print(response.start_date)