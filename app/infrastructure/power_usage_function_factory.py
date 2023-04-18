from datetime import timedelta
from typing import List, Tuple
from infrastructure.power_usage_function import PowerUsageFunction


class PowerUsageFunctionFactory():
    def __init__(self) -> None:
        pass

    def create_constant_consumption(
        self, duration: timedelta, power: float
    ) -> PowerUsageFunction:
        return PowerUsageFunction(
            [(duration, power)], extend_by=timedelta()
        )
    
    def create_variable_consumption(
        self, power_points: List[Tuple[timedelta, float]], extend_by: timedelta = timedelta()
    ) -> PowerUsageFunction:
        return PowerUsageFunction(
            power_points, extend_by
        )