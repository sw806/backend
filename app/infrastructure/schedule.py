from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from infrastructure.schedule_task import ScheduledTask
from infrastructure.spot_price_function import SpotPriceFunction
from infrastructure.task import Task

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

class ScheduleValidator(ABC):
    def __init__(self) -> None:
        super().__init__()

    def relevante_datetime(self, schedule: Schedule, task: Task, start_time: datetime) -> List[datetime]:
        return []

    @abstractmethod
    def validate(self, schedule: Schedule, task: Task, start_time: datetime) -> bool:
        pass

class Schedule:
    def __init__(
            self,
            tasks: List[ScheduledTask] = [],
            validator: Optional[ScheduleValidator] = None
        ) -> None:
        self.tasks = tasks
        self.validator = validator

    def add(self, task: ScheduledTask) -> None:
        self.tasks.append(task)

    def get_total_price(self, price_function: SpotPriceFunction) -> float:
        with tracer.start_as_current_span("GetTotalPrice"):
            total_price = 0.0
            for task in self.tasks:
                total_price += task.get_max_total_price(price_function)
            return total_price

    def can_schedule_task_at(self, task: Task, start_time: datetime) -> bool:
        if self.validator is None:
            return True

        if not task.is_scheduleable_at(start_time):
            return False

        if not self.validator.validate(self, task, start_time):
            return False
            
        return True

    def copy(self) -> Schedule:
        return Schedule(self.tasks.copy(), self.validator)