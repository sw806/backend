from datetime import datetime
from typing import List, Tuple
from infrastructure.discrete_function import DiscreteFunction
from infrastructure.power_usage_function import PowerUsageFunction

class ScheduledPowerUsageFunction(
    DiscreteFunction[datetime, float, float, Tuple[datetime, float]]
):
    def __init__(
        self,
        start: datetime,
        power_usage_function: PowerUsageFunction
    ) -> None:
        set: List[Tuple[datetime, float]] = []
        for runtime_point in power_usage_function.set:
            runtime = power_usage_function.get_domain(runtime_point)
            power = power_usage_function.get_codomain(runtime_point)
            new_point = ((start + runtime), power) 
            set.append(new_point)

        super().__init__(set)

        self.start = start
        self.power_usage_function = power_usage_function

    @property
    def min_domain(self) -> datetime:
        return self.start + self.power_usage_function.min_domain

    @property
    def max_domain(self) -> datetime:
        return self.start + self.power_usage_function.max_domain

    def domain_order(self, a: datetime, b: datetime) -> int:
        return -1 if a < b else 0 if a == b else 1

    def combine_codomains(self, a: float, b: float) -> float:
        return a + b

    def combine_integrals(self, a: float, b: float) -> float:
        return a + b

    def is_valid_argument(self, argument: datetime) -> bool:
        return argument >= self.min_domain and argument <= self.max_domain

    def get_domain(self, point: Tuple[datetime, float]) -> datetime:
        (time, _) = point
        return time

    def get_codomain(self, point: Tuple[datetime, float]) -> float:
        (_, power) = point
        return power

    def next_discrete_point_from(
        self,
        min: datetime,
        argument: datetime,
        max: datetime
    ) -> Tuple[datetime, float] | None:
        runtime_min = min - self.start
        runtime_argument = argument - self.start
        runtime_max = max - self.start
        
        next_power_point = self.power_usage_function.next_discrete_point_from(
            runtime_min, runtime_argument, runtime_max
        )
        if next_power_point is None: return None

        return (
            self.start + self.power_usage_function.get_domain(next_power_point), 
            self.power_usage_function.get_codomain(next_power_point)
        )

    def discrete_point_at(self, argument: datetime) -> Tuple[datetime, float]:
        (runtime, power) = self.power_usage_function.discrete_point_at(argument - self.start)
        return (self.start + runtime, power)

    def integral_over(
        self, 
        initial_start: datetime, start: datetime, 
        initial_end: datetime, end: datetime
    ) -> float:
        initial_start_runtime = initial_start - self.start
        start_runtime = start - self.start
        initial_end_runtime = initial_end - self.start
        end_runtime = end - self.start
        return self.power_usage_function.integral_over(
            initial_start_runtime, start_runtime,
            initial_end_runtime, end_runtime
        )