from datetime import datetime
from typing import List
from infrastructure.datetime_interval import DatetimeInterval
from infrastructure.power_price_function import PowerPriceFunction
from infrastructure.spot_price_function import SpotPriceFunction
from infrastructure.task import Task


class ScheduledTask:
    def __init__(self, start_interval: DatetimeInterval, task: Task) -> None:
        self.start_interval = start_interval
        self.task = task

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

    def get_power_consumption_at(self, time: datetime) -> float:
        if not self.runs_at(time):
            return 0

        duration = time - self.start_interval.start
        return self.task.power_usage_function.apply(duration)

    def get_total_price(self, price_function: SpotPriceFunction) -> float:
        power_price_function = PowerPriceFunction(
            self.task.power_usage_function, price_function
        )
        return power_price_function.integrate_from_to(
            self.start_interval.start, self.task.duration
        )