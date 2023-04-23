from typing import Generic, Iterator, List, Optional
from infrastructure.discrete_function import DiscreteFunction, TDiscretePoint

from infrastructure.function import TCodomain, TDomain, TIntegral


class DiscreteFunctionIterator(Iterator, Generic[TDomain, TCodomain, TIntegral, TDiscretePoint]):
    current: Optional[TDomain]

    def __init__(
        self,
        functions: List[DiscreteFunction[TDomain, TCodomain, TIntegral, TDiscretePoint]],
        start: Optional[TDomain] = None,
        end: Optional[TDomain] = None
    ) -> None:
        self.functions = functions

        # If start is None then it is the min domain for all functions.
        if start is None:
            start = functions[0].min_domain
        if end is None:
            end = functions[0].max_domain

        if len(functions) > 0:
            for function in functions[1:]:
                min_domain = function.min_domain
                if function.domain_order(min_domain, start) < 0:
                    start = min_domain
                
                max_domain = function.max_domain
                if function.domain_order(max_domain, end) > 0:
                    end = max_domain

        self.current = start
        self.start = start
        self.end = end

    def get_next_from(self, argument: Optional[TDomain]) -> Optional[TDomain]:
        if argument is None: return None
        if argument == self.end: return None

        smallest_domain: Optional[TDomain] = None
        for function in self.functions:
            # Get the next point and check if there was one.
            next_point = function.next_discrete_point_from(
                function.min_domain, argument, function.max_domain
            )
            if next_point is None: continue

            # Deconstruct the point and check if it is the first or smaller than the smallest.
            next_domain = function.get_domain(next_point)
            if function.domain_order(next_domain, self.end) > 0:
                continue

            if smallest_domain is None or \
                function.domain_order(next_domain, smallest_domain) < 0:
                smallest_domain = next_domain
        
        if smallest_domain is None:
            smallest_domain = self.end

        return smallest_domain

    def __next__(self) -> Optional[TDomain]:
        temp = self.current
        if temp is None:
            raise StopIteration
        self.current = self.get_next_from(self.current)
        return temp