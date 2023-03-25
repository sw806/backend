from datetime import datetime
from typing import List

from infrastructure.must_start_between_validator import MustStartBetweenValidator
from infrastructure.datetime_interval import DatetimeInterval
from infrastructure.task import Task, TaskValidator


class MustEndBetweenValidator(TaskValidator):
    def __init__(self, end_time_interval: DatetimeInterval) -> None:
        super().__init__()
        self.end_time_interval = end_time_interval
    
    def create_must_start_between_validator_for(self, task: Task) -> MustStartBetweenValidator:
        return MustStartBetweenValidator(
            DatetimeInterval(self.end_time_interval.start - task.duration, self.end_time_interval.duration)
        )

    def start_times(self, task: Task) -> List[datetime]:
        must_start_between_validator = self.create_must_start_between_validator_for(task)
        return must_start_between_validator.start_times(task)

    def validate(self, task: Task, start_time: datetime) -> bool:
        must_start_between_validator = self.create_must_start_between_validator_for(task)
        return must_start_between_validator.validate(task, start_time)