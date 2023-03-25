from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Generic, List, Optional, TypeVar
from infrastructure.function import Function, TCodomain, TDomain, TIntegral


TDiscretePoint = TypeVar("TDiscretePoint")
class DiscreteFunction(
    Function[TDomain, TCodomain, TIntegral],
    ABC,
    Generic[TDomain, TCodomain, TIntegral, TDiscretePoint],
):
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

    @abstractmethod
    def domain_order(self, a: TDomain, b: TDomain) -> int:
        pass

    @abstractmethod
    def combine_codomains(self, a: TCodomain, b: TCodomain) -> TCodomain:
        pass

    @abstractmethod
    def combine_integrals(self, a: TIntegral, b: TIntegral) -> TIntegral:
        pass

    @abstractmethod
    def is_valid_argument(self, argument: TDomain) -> bool:
        pass

    def discrete_point_at(self, argument: TDomain) -> TDiscretePoint:
        if not self.is_valid_argument(argument):
            raise ValueError("The argument is outside the domain boundaries")

        previous: TDiscretePoint = self.set[0]
        for point in self.set[1:]:
            if self.domain_order(argument, self.get_domain(point)) < 0:
                return previous
            previous = point

        raise Exception("Unknown error")

    def get_all_discrete_points(
        self,
        start_domain: Optional[TDomain] = None,
        end_domain: Optional[TDomain] = None
    ) -> List[TDiscretePoint]:
        if start_domain is None: start_domain = self.min_domain
        if end_domain is None: end_domain = self.max_domain

        points: List[TDiscretePoint] = []

        current_domain = start_domain
        current_point = self.discrete_point_at(current_domain)

        while self.domain_order(current_domain, end_domain) < 0:
            points.append(current_point)

            current_domain = self.get_domain(current_point)
            next_point = self.next_discrete_point_from(
                start_domain, current_domain, end_domain
            )

            if next_point is None: break
            current_point = next_point

        return points

    def is_in_same_discrete_point(self, min: TDomain, a: TDomain, b: TDomain, max: TDomain) -> bool:
        return self.discrete_point_at(a) == self.discrete_point_at(b)

    def next_discrete_point_from(
        self,
        min: TDomain,
        argument: TDomain,
        max: TDomain,
    ) -> Optional[TDiscretePoint]:
        if self.domain_order(argument, min) < 0: return None
        if self.domain_order(argument, max) > 0: return None

        point: TDiscretePoint = self.discrete_point_at(argument)
        index = self.set.index(point) + 1
        if index >= len(self.set): return None
        return self.set[index]

    def apply(self, argument: TDomain) -> TCodomain:
        return self.get_codomain(self.discrete_point_at(argument))

    def sum_helper(
        self,
        min: TDomain, argument: TDomain, max: TDomain,
    ) -> TCodomain:
        current_codomain: TCodomain = self.apply(argument)

        # Max is exclusive
        if argument == max: return current_codomain

        next_point: Optional[TDiscretePoint] = self.next_discrete_point_from(min, argument, max)
        if next_point is None:
            return current_codomain

        next_domain: TDomain = self.get_domain(next_point)
        return self.combine_codomains(
            current_codomain, self.sum_helper(min, next_domain, max)
        )

    def sum(self, start: TDomain, end: TDomain) -> TCodomain:
        return self.sum_helper(start, start, end)

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

        # To keep the algorithm clear one can remove this check where the "start" and "middle" split can is condially computed.
        # This means that if "next_point" is "None" then "start_integral" and "middle_integral" is always "0".
        end_integral = self.integrate_helper(
            min, next_to_last_domain,
            max, end
        )
        integral = end_integral
        if not next_to_first_point is None:
            next_to_first_domain = self.get_domain(next_to_first_point)
            start_integral = self.integrate_helper(
                min, start,
                max, next_to_first_domain
            )
            middle_integral = self.integrate_helper(
                min, next_to_first_domain,
                max, next_to_last_domain
            )
            integral = self.combine_integrals(
                integral,
                self.combine_integrals(start_integral, middle_integral)
            )

        return integral

    def integrate(self, start: TDomain, end: TDomain) -> TIntegral:
        return self.integrate_helper(start, start, end, end)