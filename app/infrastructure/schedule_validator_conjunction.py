from datetime import datetime
from typing import List
from infrastructure.schedule import Schedule
from infrastructure.task import Task
from infrastructure.schedule import ScheduleValidator


class ScheduleValidatorConjunction(ScheduleValidator):
    def __init__(self, validators: List[ScheduleValidator]) -> None:
        super().__init__()
        self.validators = validators

    def list_intersection(self, lhs: List, rhs: List) -> List:
        return [value for value in lhs if value in rhs]

    def relevante_datetime(self, schedule: Schedule, task: Task, start_time: datetime) -> List[datetime]:
        if len(self.validators) == 0:
            return []

        results: List[datetime] = self.validators[0].relevante_datetime(schedule, task, start_time)
        for validator in self.validators[1:]:
            results = self.list_intersection(
                results,
                validator.relevante_datetime(schedule, task, start_time)
            )

        return results

    def validate(self, schedule: Schedule, task: Task, start_time: datetime) -> bool:
        return all([validator.validate(schedule, task, start_time) for validator in self.validators])
