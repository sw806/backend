from typing import Optional


class ScheduleTaskRequest:
    def __init__(self, id: str, duration: Optional[int], energy: Optional[float],
                 power: Optional[float]) -> None:
        self.msg = id
        self.duration = duration
        self.energy = energy
        self.power = power

class ScheduleTaskResponse:
    def __init__(self, id: str, start_date: int) -> None:
        self.id = id
        self.start_date = start_date

class ScheduleTaskUseCase:
    def __init__(self) -> None:
        pass

    def do(self, request: ScheduleTaskRequest) -> ScheduleTaskResponse:
        optimal_time_calculator = OptimalTimeCalculator()
        price_points = EDSFetcher('https://api.energidataservice.dk/dataset/Elspotprices?limit=50').get_prices()



        return ScheduleTaskResponse(f"Hello! I got '{request.msg}' and I send you this.")