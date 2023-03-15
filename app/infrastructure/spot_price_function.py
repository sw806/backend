from datetime import datetime, timedelta
from typing import List, Optional
from infrastructure.discrete_function import DiscreteFunction, TDiscretePoint

from infrastructure.eletricity_prices import PricePoint


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

    def discrete_point_at(self, argument: datetime) -> PricePoint:
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