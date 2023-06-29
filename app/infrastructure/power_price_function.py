from datetime import datetime, timedelta
from typing import Optional, Tuple
from infrastructure.discrete_function import DiscreteFunction

from infrastructure.power_usage_function import PowerUsageFunction
from infrastructure.spot_price_function import SpotPriceFunction
from infrastructure.zipped_discrete_function import ZippedDiscreteFunction
from domain import PricePoint
from infrastructure.discrete_function_iterator import DiscreteFunctionIterator
from infrastructure.scheduled_power_usage_function import ScheduledPowerUsageFunction


class ZippedPowerPriceFunction(
    ZippedDiscreteFunction[
        # Domains
        datetime, timedelta, 
        # Codomains
        float, float,
        # Integrals 
        float, float, 
        # discrete points
        PricePoint, Tuple[timedelta, float],
        # Step
        timedelta
    ]
):
    def __init__(
        self,
        power_usage_function: PowerUsageFunction,
        spot_price_function: SpotPriceFunction,
    ) -> None:
        super().__init__(spot_price_function, power_usage_function)
    
    def min_step(start, step_1: timedelta, step_2: timedelta) -> timedelta:
        return min(step_1, step_2)

    def step_lengths(
        self, 
        start: Tuple[datetime, timedelta], 
        end: Tuple[datetime, timedelta]
    ) -> Tuple[timedelta, timedelta]:
        (start_1, start_2) = start
        (end_1, end_2) = end
        return (
            end_1 - start_1,
            end_2 - start_2
        )

    def step_by(
        self, 
        start: Tuple[datetime, timedelta], 
        step: timedelta
    ) -> Tuple[datetime, timedelta]:
        (start_1, start_2) = start
        return (start_1 + step, start_2 + step)

    def combine_codomains(
        self, 
        a: Tuple[float, float], 
        b: Tuple[float, float]
    ) -> Tuple[float, float]:
        (a_1, a_2) = a
        (b_1, b_2) = b
        return (a_1 + b_1, a_2 + b_2)

    def combine_integrals(
        self, 
        a: Tuple[float, float], 
        b: Tuple[float, float]
    ) -> Tuple[float, float]:
        (a_1, a_2) = a
        (b_1, b_2) = b
        return (a_1 + b_1, a_2 + b_2)

    def integral_over(
        self, 
        min: Tuple[datetime, timedelta], start: Tuple[datetime, timedelta],
        max: Tuple[datetime, timedelta], end: Tuple[datetime, timedelta],
    ) -> Tuple[float, float]:
        (min_1, min_2) = min
        (start_1, start_2) = start
        (max_1, max_2) = max
        (end_1, end_2) = end
        
        return (
            self.function_1.integral_over(min_1, start_1, max_1, end_1),
            self.function_2.integral_over(min_2, start_2, max_2, end_2),
        )

class PowerPriceFunction(
    DiscreteFunction[Tuple[datetime, timedelta], float, float, Tuple[datetime, timedelta]]
):
    def __init__(
        self,
        power_usage_function: PowerUsageFunction,
        spot_price_function: SpotPriceFunction,
    ) -> None:
        super().__init__([])
        self.power_usage_function = power_usage_function
        self.spot_price_function = spot_price_function

    @property
    def min_domain(self) -> Tuple[datetime, timedelta]:
        return (self.spot_price_function.min_domain, self.power_usage_function.min_domain)

    @property
    def max_domain(self) -> Tuple[datetime, timedelta]:
        return (self.spot_price_function.max_domain, self.power_usage_function.max_domain)

    def domain_order(self, a: Tuple[datetime, timedelta], b: Tuple[datetime, timedelta]) -> int:
        (a_time, a_delta) = a
        (b_time, b_delta) = b
        time_order = self.spot_price_function.domain_order(a_time, b_time)
        delta_order = self.power_usage_function.domain_order(a_delta, b_delta)
        if time_order == delta_order: return time_order
        else: raise ValueError("Time and delta order was not the same")

    def combine_codomains(self, a: float, b: float) -> float:
        return a + b

    def combine_integrals(self, a: float, b: float) -> float:
        return a + b

    def is_valid_argument(self, argument: Tuple[datetime, timedelta]) -> bool:
        return argument >= self.min_domain and argument <= self.max_domain

    def get_domain(self, point: Tuple[datetime, timedelta]) -> Tuple[datetime, timedelta]:
        return point

    def get_codomain(self, point: Tuple[datetime, timedelta]) -> float:
        (time, delta) = point
        return self.spot_price_function.apply(time) * self.power_usage_function.apply(delta)

    def discrete_point_at(self, argument: Tuple[datetime, timedelta]) -> Tuple[datetime, timedelta]:
        return argument

    def is_in_same_discrete_point(
        self,
        global_min: Tuple[datetime, timedelta],
        a: Tuple[datetime, timedelta],
        b: Tuple[datetime, timedelta],
        global_max: Tuple[datetime, timedelta],
    ) -> bool:
        a_next = self.next_discrete_point_from(global_min, a, global_max)
        b_next = self.next_discrete_point_from(global_min, b, global_max)
        return a_next == b_next

    def next_discrete_point_from(
        self,
        global_min: Tuple[datetime, timedelta],
        argument: Tuple[datetime, timedelta],
        global_max: Tuple[datetime, timedelta],
    ) -> Optional[Tuple[datetime, timedelta]]:
        # TODO: Generalise this method.

        # Boundary check
        if argument < global_min: return None
        if argument > global_max: return None

        # De-constructu parameters.
        (min_time, min_delta) = global_min
        (time, delta) = argument
        (max_time, max_delta) = global_max

        # Find the next times for both price and power.
        next_time_point = self.spot_price_function.next_discrete_point_from(min_time, time, max_time)
        next_delta_point = self.power_usage_function.next_discrete_point_from(min_delta, delta, max_delta)

        # If both next points are None then we have reached the end.
        if next_time_point is None or next_delta_point is None:
            return None

        # If one or none of the next discrete points are none then get the domain.
        next_time = time if next_time_point is None else self.spot_price_function.get_domain(next_time_point)
        next_delta = delta if next_delta_point is None else self.power_usage_function.get_domain(next_delta_point)

        # The one increasing with the smallest timedelta is chosen.
        time_step = next_time - min_time
        delta_step = next_delta - min_delta
        smallest_step =  min(time_step, delta_step)

        # The new time and delta is then stepping by smallest step.
        new_time = min_time + smallest_step
        new_delta = min_delta + smallest_step

        return (new_time, new_delta)

    def integral_over(
        self,
        min: Tuple[datetime, timedelta], start: Tuple[datetime, timedelta],
        max: Tuple[datetime, timedelta], end: Tuple[datetime, timedelta],
    ) -> float:
        # De-construct parameters
        (min_time, min_delta) = min
        (start_time, start_delta) = start
        (end_time, end_delta) = end
        (max_time, max_delta) = max

        if not (min_time - max_time) == (min_delta - max_delta):
            raise ValueError("The timedelate between the datetimes and timedeltas must be the same")

        # Because of the way "next_discrete_point_from" then we have to use the price at the start of this "step".
        #   What is meant here is that the start and from includes the domain of the beginning of the next point.
        price = self.spot_price_function.apply(start_time)
        # We can just use "integral_over" instead of "integrate"
        # As our "next_discrete_point_from" takes the smallest possible step.
        # Because of this, we want "skip" any discrete points.
        power_integral = self.power_usage_function.integral_over(
            min_delta, start_delta, max_delta, end_delta
        )

        return power_integral * price

    def integrate_from_to(
        self,
        start: datetime,
        duration: timedelta,
        start_duration: timedelta = timedelta()
    ) -> float:
        return self.integrate(
            (start, start_duration),
            (start + duration, start_duration + duration)
        )