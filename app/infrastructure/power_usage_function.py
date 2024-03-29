from datetime import timedelta
from typing import List, Optional, Tuple

from infrastructure.discrete_function import DiscreteFunction


class PowerUsageFunction(DiscreteFunction[timedelta, float, float, Tuple[timedelta, float]]):
    def __init__(
        self,
        power_points: List[Tuple[timedelta, float]],
        extend_by: timedelta = timedelta(hours=1)
    ) -> None:
        super().__init__(power_points)
        # If the power points are missing the first point (min domain) then add it
        (first_time, first_power) = power_points[0]
        if first_time > self.min_domain:
            power_points.insert(0, (self.min_domain, first_power))

        min_step = extend_by
        (last_time, _) = power_points[0]
        for (curr_time, _) in power_points[1:]:
            step = curr_time - last_time
            if step < min_step: min_step = step

        self._min_step = min_step
        self.extend_by = extend_by

    @property
    def min_domain(self) -> timedelta:
        return timedelta()

    @property
    def max_domain(self) -> timedelta:
        return super().max_domain + self.extend_by

    def domain_order(self, a: timedelta, b: timedelta) -> int:
        return -1 if a < b else 0 if a == b else 1

    def combine_codomains(self, a: float, b: float) -> float:
        return a + b

    def combine_integrals(self, a: float, b: float) -> float:
        return a + b

    def is_valid_argument(self, argument: timedelta) -> bool:
        return argument >= self.min_domain and argument <= self.max_domain

    def get_domain(self, point: Tuple[timedelta, float]) -> timedelta:
        (delta, _) = point
        return delta

    def get_codomain(self, point: Tuple[timedelta, float]) -> float:
        (_, power) = point
        return power

    def next_discrete_point_from(
        self,
        min: timedelta,
        argument: timedelta,
        max: timedelta,
    ) -> Optional[Tuple[timedelta, float]]:
        # Check if this argument exceeds the last price point's time.
        last_point = self.set[-1]
        last_time = self.get_domain(last_point)
        if argument >= last_time:
            # Check if delta is inside acceptable bounds.
            delta = argument - last_time
            if delta < self.extend_by:
                return (self.max_domain, self.get_codomain(last_point))
            else:
                return None

        return super().next_discrete_point_from(min, argument, max)

    def discrete_point_at(self, argument: timedelta) -> Tuple[timedelta, float]:
        # Check if this argument is between the min domain (0 hour) and first point.
        first_point = self.set[0]
        if argument >= self.min_domain and argument <= self.get_domain(first_point):
            return first_point

        # Check if this argument exceeds the last price point's time.
        last_point = self.set[-1]
        last_time = self.get_domain(last_point)
        if argument >= last_time:
            # Check if delta is inside acceptable bounds.
            delta = argument - last_time
            if delta <= self.extend_by:
                return last_point

        return super().discrete_point_at(argument)

    @property
    def duration(self) -> timedelta:
        return self.max_domain - self.min_domain


    def apply(self, argument: timedelta) -> float:
        """Calculates the kw at the current time.

        Args:
            argument (TDomain): The time to get the kw for

        Returns:
            TCodomain: The kw at the time.
        """
        return super().apply(argument)

    def integral_over(
        self,
        min: timedelta, start: timedelta,
        max: timedelta, end: timedelta
    ) -> float:
        hours = (end - start).seconds / 3600
        start_point = self.discrete_point_at(start)
        return self.get_codomain(start_point) * hours

    def integrate(self, start: timedelta, end: timedelta) -> float:
        """Calculates the kwh over a timespan.

        Args:
            start (TDomain): The start (or minimum) argument to calculate the integral from.
            end (TDomain): The end (or maximum) argument to calculate the integral to.

        Returns:
            TIntegral: Energy used as kwh from start to end.
        """
        return super().integrate(start, end)