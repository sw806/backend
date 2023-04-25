from datetime import datetime, timedelta
from typing import List

from infrastructure.discrete_function_iterator import DiscreteFunctionIterator
from infrastructure.power_emission_function import PowerEmissionFunction
from infrastructure.datetime_interval import DatetimeInterval
from infrastructure.power_price_function import PowerPriceFunction
from infrastructure.spot_price_function import SpotPriceFunction
from infrastructure.co2_emission_function import Co2EmissionFunction
from infrastructure.task import Task


class ScheduledTask:
    def __init__(self, start_interval: DatetimeInterval, task: Task, cost: float) -> None:
        self.start_interval = start_interval
        self.task = task
        self.cost = cost

    @property
    def end_interval(self) -> DatetimeInterval:
        return DatetimeInterval(
            self.start_interval.start + self.task.duration,
            self.start_interval.duration
        )

    def derieve_start_times(self) -> List[datetime]:
        return self.task.derieve_start_times(
            self.start_interval.start
        )

    def runs_at(self, time: datetime) -> bool:
        earliest_start_time = self.start_interval.start
        last_end_time = (earliest_start_time + self.start_interval.duration) + self.task.duration
        return time >= earliest_start_time and time < last_end_time

    def get_max_power_consumption_at(self, time: datetime) -> float:
        if not self.runs_at(time):
            return 0

        # Calculate the duration bounds
        min_runtime = time - self.start_interval.start
        max_runtime = min_runtime + self.start_interval.duration

        # Initialise the greatest consumption to the first.
        # TODO: This is actually also calculate on the first iterator of the for-loop. Possible optimisation.
        greatest_consumption = self.task.power_usage_function.apply(min_runtime)

        # iterate over all runtimes between "min_duration" and "max_duration"
        iterator = DiscreteFunctionIterator(
            [self.task.power_usage_function], min_runtime, max_runtime
        )
        for current_runtime in iterator:
            current_consumption = self.task.power_usage_function.apply(current_runtime)

            if current_consumption > greatest_consumption:
                greatest_consumption = current_consumption

        return greatest_consumption

    def get_max_emission(self, emission_function: Co2EmissionFunction) -> float:
        if self.start_interval.start < emission_function.min_domain:
            return 0

        if self.start_interval.start + self.task.duration > emission_function.max_domain:
            return 0

        power_emission_function = PowerEmissionFunction(
            self.task.power_usage_function, emission_function
        )

        greatest_emission = power_emission_function.integrate_from_to(
            self.start_interval.start, self.task.duration
        )

        runtime_iterator = DiscreteFunctionIterator(
            [self.task.power_usage_function], end=self.start_interval.duration
        )
        for current_runtime in runtime_iterator:
            if current_runtime > self.start_interval.duration:
                break

            current_emission = power_emission_function.integrate_from_to(
                self.start_interval.start + current_runtime, self.task.duration
            )

            if current_emission > greatest_emission:
                greatest_emission = current_emission

        return greatest_emission

    def get_max_total_price(self, price_function: SpotPriceFunction) -> float:
        power_price_function = PowerPriceFunction(
            self.task.power_usage_function, price_function
        )

        greatest_price = power_price_function.integrate_from_to(
            self.start_interval.start, self.task.duration
        )

        runtime_iterator = DiscreteFunctionIterator(
            [self.task.power_usage_function], end=self.start_interval.duration
        )
        for current_runtime in runtime_iterator:
            if current_runtime > self.start_interval.duration:
                break

            current_price = power_price_function.integrate_from_to(
                self.start_interval.start + current_runtime, self.task.duration
            )

            if current_price > greatest_price:
                greatest_price = current_price

        return greatest_price