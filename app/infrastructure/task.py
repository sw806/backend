from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from datetime import datetime, timedelta

from infrastructure.discrete_function_iterator import DiscreteFunctionIterator
from infrastructure.power_usage_function import PowerUsageFunction


class TaskValidator(ABC):
    def __init__(self) -> None:
        super().__init__()

    def start_times(self, task: Task) -> List[datetime]:
        return []

    def derieve_start_times(self, task: Task, start_time: datetime) -> List[datetime]:
        return []

    @abstractmethod
    def validate(self, task: Task, start_time: datetime) -> bool:
        pass


class Task:
    def __init__(
        self,
        power_usage_function: PowerUsageFunction,
        validators: List[TaskValidator] = []
    ) -> None:
        self.power_usage_function = power_usage_function
        self.validators = validators

    @property
    def duration(self) -> timedelta:
        return self.power_usage_function.duration
    
    def start_times(self) -> List[datetime]:
        times: List[datetime] = []
        for validator in self.validators:
            for start_time in validator.start_times(self):
                if self.is_scheduleable_at(start_time):
                    times.append(start_time)
        return times

    def derieve_start_times(self, start_time: datetime) -> List[datetime]:
        if not self.is_scheduleable_at(start_time):
            return []

        start_times: List[datetime] = []

        for runtime in DiscreteFunctionIterator([ self.power_usage_function ]):
            # If it starts at the "start_time".
            late_start = start_time - self.duration + runtime
            if not late_start in start_times and\
                self.is_scheduleable_at(late_start):
                start_times.append(late_start)

            # If it ends at the "start_time".
            early_start = start_time - runtime
            if not early_start in start_times and\
                self.is_scheduleable_at(early_start):
                start_times.append(early_start)
                
        return start_times

    def is_scheduleable_at(self, start_time: datetime) -> bool:
        for validator in self.validators:
            if not validator.validate(self, start_time):
                return False
        return True