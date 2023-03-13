from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Generic, List, Optional, TypeVar
from app.infrastructure.function import TCodomain, TDomain, TIntegral


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