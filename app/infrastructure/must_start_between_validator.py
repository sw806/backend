from datetime import datetime
from typing import List

from infrastructure.discrete_function_iterator import DiscreteFunctionIterator
from infrastructure.datetime_interval import DatetimeInterval
from infrastructure.task import Task, TaskValidator


class MustStartBetweenValidator(TaskValidator):
    def __init__(self, start_time_interval: DatetimeInterval) -> None:
        super().__init__()
        self.start_time_interval = start_time_interval
    
    def start_times(self, task: Task) -> List[datetime]:
        start_times = []

        # Iterate over all runtime intervals between the "start_time_interval" and "duration"
        for runtime in DiscreteFunctionIterator(
            [ task.power_usage_function ], 
            end=self.start_time_interval.duration
        ):
            earliest_start_time = self.start_time_interval.start + runtime
            if not earliest_start_time in start_times:
                start_times.append(earliest_start_time)

            last_start_time = self.start_time_interval.end - runtime
            if not last_start_time in start_times:
                start_times.append(last_start_time)

        return start_times

    def validate(self, task: Task, start_time: datetime) -> bool:
        return start_time >= self.start_time_interval.start and \
            start_time <= self.start_time_interval.end