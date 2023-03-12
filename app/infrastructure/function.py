from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Generic, List, Optional, Tuple, TypeVar

from app.infrastructure.eletricity_prices import PricePoint

TDomain = TypeVar("TDomain")
TCodomain = TypeVar("TCodomain")
TIntegral = TypeVar("TIntegral")

class Function(ABC, Generic[TDomain, TCodomain, TIntegral]):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def apply(self, argument: TDomain) -> TCodomain:
        """Apply a value (the argument) form its domain to obtain the the corresponding value from its range.

        Args:
            argument (TDomain): The argument from the domain.

        Returns:
            TCodomain: The range value from the codomain.
        """
        pass

    @abstractmethod
    def integrate(self, start: TDomain, end: TDomain) -> TIntegral:
        """Calculates the area between (inclusive) the start and end arguments.

        Args:
            start (TDomain): The start argument from the domain.
            end (TDomain): The end argument from the domain.

        Returns:
            TIntegral: The area under the funciton from start to end.
        """
        pass

TDiscretePoint = TypeVar("TDiscretePoint")
class DiscreteFunction(ABC, Generic[TDomain, TCodomain, TIntegral, TDiscretePoint]):
    def __init__(
        self,
        set: List[TDiscretePoint]
    ) -> None:
        super().__init__()
        self.set = set

    @abstractmethod
    def get_domain(self, point: TDiscretePoint) -> TDomain:
        pass

    @abstractmethod
    def get_codomain(self, point: TDiscretePoint) -> TCodomain:
        pass

    @property
    def min_domain(self) -> TDomain:
        return self.get_domain(self.set[0])

    @property
    def max_domain(self) -> TDomain:
        return self.get_domain(self.set[-1])

    def is_valid_argument(self, argument: timedelta) -> bool:
        return argument >= self.min_domain and argument <= self.max_domain

    def discrete_point_at(self, argument: TDomain) -> TDiscretePoint:
        if not self.is_valid_argument(argument):
            raise ValueError("The argument is outside the domain boundaries")

        previous: TDiscretePoint = self.set[0]
        for point in self.set[1:]:
            if argument < self.get_domain(point):
                return previous
            previous = point

        raise Exception("Unknown error")

    def is_in_same_discrete_point(self, min: TDomain, a: TDomain, b: TDomain, max: TDomain) -> bool:
        return self.discrete_point_at(a) == self.discrete_point_at(b)

    def next_discrete_point_from(
        self,
        min: TDomain,
        argument: TDomain,
        max: TDomain,
    ) -> Optional[TDiscretePoint]:
        if argument < min: return None
        if argument > max: return None

        point: TDiscretePoint = self.discrete_point_at(argument)
        index = self.set.index(point) + 1
        if index >= len(self.set): return None
        return self.set[index]

    def apply(self, argument: TDomain) -> TCodomain:
        return self.get_codomain(self.discrete_point_at(argument))

    @abstractmethod
    def integral_over(
        self,
        initial_start: TDomain, start: TDomain,
        initial_end: TDomain, end: TDomain
    ) -> TIntegral:
        pass

    def integrate_helper(
        self,
        min: TDomain, start: TDomain,
        max: TDomain, end: TDomain
    ) -> TIntegral:
        # This can often happen with the recursive calls when we have narrowed down "start", "mid", and "end" boundaries.
        if start == end: return 0

        next_to_first_point = self.next_discrete_point_from(min, start, max)

        # We are in the same point, or
        # we are not in the same point. But the "end" value is the domain value of the next from start.
        #   This check is required because the minimum step from getting the enxt point
        #   includes the next point time. This means that even though an an integral will be [a, b)
        #   we get [a, b] intervals which means the same if the "end" is precisely the "end" domain.
        #   Ultimately this hinders floating point erros happening.
        if self.is_in_same_discrete_point(min, start, end, max) or \
            not next_to_first_point is None and end == self.get_domain(next_to_first_point):
            return self.integral_over(
                min, start, 
                max, end
            )

        next_to_last_point: TDiscretePoint = self.discrete_point_at(end)
        next_to_last_domain = self.get_domain(next_to_last_point)
        next_to_first_domain = self.get_domain(next_to_first_point)

        # To keep the algorithm clear one can remove this check where the "start" and "middle" split can is condially computed.
        # This means that if "next_point" is "None" then "start_integral" and "middle_integral" is always "0".
        start_integral = middle_integral = end_integral = 0
        if not next_to_first_point is None:
            start_integral = self.integrate_helper(
                min, start,
                max, next_to_first_domain
            )
            middle_integral = self.integrate_helper(
                min, next_to_first_domain,
                max, next_to_last_domain
            )
        end_integral = self.integrate_helper(
            min, next_to_last_domain,
            max, end
        )

        return start_integral + middle_integral + end_integral

    def integrate(self, start: TDomain, end: TDomain) -> TIntegral:
        return self.integrate_helper(start, start, end, end)

class PowerUsageFunction(DiscreteFunction[timedelta, float, float, Tuple[timedelta, float]]):
    def __init__(
        self,
        power_points: List[Tuple[timedelta, float]],
        extend_by: timedelta = timedelta(hours=1)
    ) -> None:
        # If the power points are missing the first point (min domain) then add it
        (first_time, first_power) = power_points[0]
        if first_time > self.min_domain:
            power_points.insert(0, (self.min_domain, first_power))

        super().__init__(power_points)
        self.extend_by = extend_by

    @property
    def min_domain(self) -> TDomain:
        return timedelta()

    @property
    def max_domain(self) -> TDomain:
        return super().max_domain + self.extend_by

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
            if delta <= self.extend_by:
                return (self.max_domain, self.get_codomain(last_point))

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
        return self.min_domain - self.max_domain


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
    ) -> TIntegral:
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

class SpotPriceFunction(DiscreteFunction[datetime, float, float, PricePoint]):
    def __init__(
        self,
        price_points: List[PricePoint],
        extend_by: timedelta = timedelta(hours=1)
    ) -> None:
        super().__init__(price_points)
        # Check if the price points are in ascending order and not overlapping.
        previous = int(price_points[0].time.timestamp())
        for price_point in price_points[1:]:
            current = int(price_point.time.timestamp())
            if previous > current:
                raise ValueError("The price points are not in ascending order")
            if previous == current:
                raise ValueError("The price point is exactly on the same time as the current")
            previous = int(price_point.time.timestamp())

        self.extend_by = extend_by

    @property
    def max_domain(self) -> datetime:
        return super().max_domain + self.extend_by

    def get_domain(self, point: PricePoint) -> datetime:
        return point.time

    def get_codomain(self, point: PricePoint) -> float:
        return point.price

    def next_discrete_point_from(
        self,
        min: datetime,
        argument: datetime,
        max: datetime,
    ) -> Optional[PricePoint]:
        # Check if this argument exceeds the last price point's time.
        last_point = self.set[-1]
        last_time = self.get_domain(last_point)
        if argument >= last_time:
            # Check if delta is inside acceptable bounds.
            delta = argument - last_time
            if delta <= self.extend_by:
                return PricePoint(self.max_domain, self.get_codomain(last_point))

        return super().next_discrete_point_from(min, argument, max)

    def discrete_point_at(self, argument: datetime) -> TDiscretePoint:
        if not self.is_valid_argument(argument):
            raise ValueError("The argument is outside the domain boundaries")

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
        """Calculates the dkk/kwh for the datetime argument.

        Args:
            argument (datetime): The datetime to calculate the dkk/kwh.

        Returns:
            float: Spot price in dkk/kwh at the specific time.
        """
        return super().apply(argument)

    def integral_over(
        self,
        min: datetime, start: datetime,
        max: datetime, end: datetime,
    ) -> float:
        hours = (end - start).seconds / 3600
        start_point = self.discrete_point_at(start)
        return self.get_codomain(start_point) * hours

    def integrate(self, start: datetime, end: datetime) -> float:
        """Calculates the exact integral over the price points and return dkk/kw.

        Args:
            start (datetime): The start (or minimum) argument to calculate the integral from.
            end (datetime): The end (or maximum) argument to calculate the integral to.

        Returns:
            float: Spot price integral in dkk/kw spanning form start to end.
        """
        return super().integrate(start, end)

class PowerPriceFunction(DiscreteFunction[Tuple[datetime, timedelta], float, float, Tuple[datetime, timedelta]]):
    def __init__(
        self,
        power_usage_function: PowerUsageFunction,
        spot_price_function: SpotPriceFunction,
    ) -> None:
        super().__init__([])
        self.power_usage_function = power_usage_function
        self.spot_price_function = spot_price_function

    @property
    def min_domain(self) -> TDomain:
        return (self.power_usage_function.min_domain, self.spot_price_function.min_domain)

    @property
    def max_domain(self) -> TDomain:
        return (self.power_usage_function.max_domain, self.spot_price_function.max_domain)

    def get_domain(self, point: Tuple[datetime, timedelta]) -> Tuple[datetime, timedelta]:
        return point

    def get_codomain(self, point: Tuple[datetime, timedelta]) -> float:
        (time, delta) = point
        return self.spot_price_function.apply(time) * self.power_usage_function.apply(delta)

    def discrete_point_at(self, argument: Tuple[datetime, timedelta]) -> Tuple[datetime, timedelta]:
        return argument

    def is_in_same_discrete_point(
        self,
        globa_min: Tuple[datetime, timedelta],
        a: Tuple[datetime, timedelta],
        b: Tuple[datetime, timedelta],
        global_max: Tuple[datetime, timedelta],
    ) -> bool:
        a_next = self.next_discrete_point_from(globa_min, a, global_max)
        b_next = self.next_discrete_point_from(globa_min, b, global_max)
        return a_next == b_next

    def next_discrete_point_from(
        self,
        global_min: Tuple[datetime, timedelta],
        argument: Tuple[datetime, timedelta],
        global_max: Tuple[datetime, timedelta],
    ) -> Optional[Tuple[datetime, timedelta]]:
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
    ):
        return self.integrate(
            (start, start_duration),
            (start + duration, start_duration + duration)
        )