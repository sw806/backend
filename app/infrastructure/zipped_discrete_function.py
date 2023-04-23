from typing import Generic, List, Optional, Tuple, TypeVar
from infrastructure.discrete_function import *

TDomain1 = TypeVar("TDomain1")
TCodomain1 = TypeVar("TCodomain1")
TIntegral1 = TypeVar("TIntegral1")
TDiscretePoint1 = TypeVar("TDiscretePoint1")

TDomain2 = TypeVar("TDomain2")
TCodomain2 = TypeVar("TCodomain2")
TIntegral2 = TypeVar("TIntegral2")
TDiscretePoint2 = TypeVar("TDiscretePoint2")

TStep = TypeVar("TStep")

class ZippedDiscreteFunction(
    DiscreteFunction[Tuple[TDomain1, TDomain2], Tuple[TCodomain1, TCodomain2], Tuple[TIntegral1, TIntegral2], Tuple[TDiscretePoint1, TDiscretePoint2]],
    Generic[TDomain1, TDomain2, TCodomain1, TCodomain2, TIntegral1, TIntegral2, TDiscretePoint1, TDiscretePoint2, TStep]
):
    def __init__(
        self,
        function_1: DiscreteFunction[TDomain1, TCodomain1, TIntegral1, TDiscretePoint1],
        function_2: DiscreteFunction[TDomain2, TCodomain2, TIntegral2, TDiscretePoint2],
    ) -> None:
        # TODO: Should we lazy evaluate the entire set if required?
        super().__init__([])
        self.function_1 = function_1
        self.function_2 = function_2

    def domain_order(self, a: Tuple[TDomain1, TDomain2], b: Tuple[TDomain1, TDomain2]) -> int:
        (a1, a2) = a
        (b1, b2) = b
        a_order = self.function_1.domain_order(a1, b1)
        b_order = self.function_2.domain_order(a2, b2)
        if a_order == b_order: return a_order
        else: raise ValueError("Deconstructed discrete points of zipped function does not have the same order")


    def is_valid_argument(self, argument: Tuple[TDomain1, TDomain2]) -> bool:
        return self.domain_gt_eq(argument, self.min_domain) and \
               self.domain_lt_eq(self.max_domain, argument)

    def get_domain(self, point: Tuple[TDiscretePoint1, TDiscretePoint2]) -> Tuple[TDomain1, TDomain2]:
        (p_1, p_2) = point
        return (
            self.function_1.get_domain(p_1),
            self.function_2.get_domain(p_2),
        )

    def get_codomain(self, point: Tuple[TDiscretePoint1, TDiscretePoint2]) -> Tuple[TCodomain1, TCodomain2]:
        (p_1, p_2) = point
        return (
            self.function_1.get_codomain(p_1),
            self.function_2.get_codomain(p_2),
        )

    def discrete_point_at(self, argument: Tuple[TDomain1, TDomain2]) -> Tuple[TDiscretePoint1, TDiscretePoint2]:
        (a_1, a_2) = argument
        return (
            self.function_1.discrete_point_at(a_1),
            self.function_2.discrete_point_at(a_2),
        )

    def is_in_same_discrete_point(
        self, 
        global_min: Tuple[TDomain1, TDomain2], 
        a: Tuple[TDomain1, TDomain2], 
        b: Tuple[TDomain1, TDomain2], 
        global_max: Tuple[TDomain1, TDomain2]
    ) -> bool:
        a_next = self.next_discrete_point_from(global_min, a, global_max)
        b_next = self.next_discrete_point_from(global_min, b, global_max)
        return a_next == b_next

    def next_discrete_point_from(
            self, 
            global_min: Tuple[TDomain1, TDomain2],
            argument: Tuple[TDomain1, TDomain2],
            global_max: Tuple[TDomain1, TDomain2]
        ) -> Optional[Tuple[TDiscretePoint1, TDiscretePoint2]]:
        # Boundary check.
        if self.domain_lt(argument, global_min): return None
        if self.domain_gt(argument, global_max): return None

        # Deconstruct parameters.
        (global_min_1, global_min_2) = global_min
        (argument_1, argument_2) = argument
        (global_max_1, global_max_2) = global_max

        # Find next points.
        next_point_1 = self.function_1.next_discrete_point_from(global_min_1, argument_1, global_max_1)
        next_point_2 = self.function_2.next_discrete_point_from(global_min_2, argument_2, global_max_2)

        # If both next points are None then we have reached the end.
        if next_point_1 is None or next_point_2 is None: return None
    
        # If one or none of the next points are non then get the domain
        next_domain_1 = argument_1 if next_point_1 is None else self.function_1.get_domain(next_point_1)
        next_domain_2 = argument_2 if next_point_2 is None else self.function_2.get_domain(next_point_2)

        # The one increasing with the smallest delta is chosen.
        (step_1, step_2) = self.step_lengths(
            (global_min_1, global_min_2), (next_domain_1, next_domain_2)
        )
        smallest_step = self.min_step(step_1, step_2)

        # The new time and delta is then stepping by the smallest step.
        (new_domain_1, new_domain_2) = self.step_by(
            (global_min_1, global_min_2), smallest_step
        )

        return (
            self.function_1.discrete_point_at(new_domain_1),
            self.function_2.discrete_point_at(new_domain_2),
        )

    @abstractmethod
    def min_step(start, step_1: TStep, step_2: TStep) -> TStep:
        pass

    @abstractmethod
    def step_lengths(self, start: Tuple[TDomain1, TDomain2], end: Tuple[TDomain1, TDomain2]) -> Tuple[TStep, TStep]:
        pass

    @abstractmethod
    def step_by(self, start: Tuple[TDomain1, TDomain2], step: TStep) -> Tuple[TDomain1, TDomain2]:
        pass