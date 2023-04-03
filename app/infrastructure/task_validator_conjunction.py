from datetime import datetime
from typing import List
from infrastructure.task import Task, TaskValidator


class TaskValidatorConjunction(TaskValidator):
    def __init__(self, validators: List[TaskValidator]) -> None:
        super().__init__()
        self.validators = validators

    def list_intersection(self, lhs: List, rhs: List) -> List:
        return [value for value in lhs if value in rhs]

    def start_times(self, task: Task) -> List[datetime]:
        if len(self.validators) == 0:
            return []

        results: List[datetime] = self.validators[0].start_times(task)
        for validator in self.validators[1:]:
            results = self.list_intersection(results, validator.start_times(task))

        return results

    def derieve_start_times(self, task: Task, start_time: datetime) -> List[datetime]:
        if len(self.validators) == 0:
            return []

        results: List[datetime] = self.validators[0].derieve_start_times(task, start_time)
        for validator in self.validators[1:]:
            results = self.list_intersection(
                results,
                validator.derieve_start_times(task, start_time)
            )

        return results

    def validate(self, task: Task, start_time: datetime) -> bool:
        return all([validator.validate(task, start_time) for validator in self.validators])