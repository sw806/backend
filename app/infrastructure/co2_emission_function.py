from datetime import datetime, timedelta
from typing import List

from infrastructure.discrete_function import DiscreteFunction
from infrastructure import Co2EmissionPoint

class Co2EmissionFunction(DiscreteFunction[datetime, float, float, Co2EmissionPoint]):
    def __init__(
            self,
            emission_points: List[Co2EmissionPoint],
            extend_by: timedelta = timedelta(minutes=5)
        ) -> None:
        super().__init__(emission_points)

        previous_time = emission_points[0].time
        for emission_point in emission_points[1:]:
            current_time = emission_point.time
            if previous_time > current_time:
                raise ValueError("The emission points are not in ascending order")
            if previous_time == current_time:
                raise ValueError("The emission point is exactly on the same time as the current")
            previous_time = current_time
    
        self.extend_by = extend_by

    @property
    def max_domain(self) -> datetime:
        return super().max_domain + self.extend_by

    def domain_order(self, a: datetime, b: datetime) -> int:
        return -1 if a < b else 0 if a == b else 1

    def combine_codomains(self, a: float, b: float) -> float:
        return a + b

    def combine_integrals(self, a: float, b: float) -> float:
        return a + b

    def is_valid_argument(self, argument: datetime) -> bool:
        return argument >= self.min_domain and argument <= self.max_domain

    def get_domain(self, point: Co2EmissionPoint) -> datetime:
        return point.time
    
    def get_codomain(self, point: Co2EmissionPoint) -> float:
        return point.emission

    def next_discrete_point_from(
            self,
            min: datetime,
            argument: datetime,
            max: datetime
        ) -> Co2EmissionPoint | None:
        # Check if this argument exceeds the last price point's time.
        last_point = self.set[-1]
        last_time = self.get_domain(last_point)
        if argument >= last_time:
            # Check if delta is inside acceptable bounds.
            delta = argument - last_time
            if delta <= self.extend_by:
                return Co2EmissionPoint(self.max_domain, self.get_codomain(last_point))

        return super().next_discrete_point_from(min, argument, max)

    def discrete_point_at(self, argument: datetime) -> Co2EmissionPoint:
        if not self.is_valid_argument(argument):
            raise ValueError(f'The argument "{argument}" is outside the domain boundaries')

        # Check if this argument exceeds the last price point's time.
        last_point = self.set[-1]
        last_time = self.get_domain(last_point)
        if argument >= last_time:
            # Check if delta is inside acceptable bounds.
            delta = argument - last_time
            if delta <= self.extend_by:
                return last_point

        return super().discrete_point_at(argument)

    def apply(self, argument: datetime) -> float:
        # Returns the gKw at time (argument)
        return super().apply(argument)

    def integral_over(
        self,
        min: datetime, start: datetime,
        max: datetime, end: datetime,
    ) -> float:
        # Returns the gKwHr
        hours = (end - start).seconds / 3600
        start_point = self.discrete_point_at(start)
        return self.get_codomain(start_point) * hours

    def integrate(self, start: datetime, end: datetime) -> float:
        return super().integrate(start, end)