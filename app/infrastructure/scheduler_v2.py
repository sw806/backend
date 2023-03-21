from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Optional
from infrastructure.power_price_function import PowerPriceFunction
from infrastructure.spot_price_function import SpotPriceFunction
from infrastructure.power_usage_function import PowerUsageFunction

class Task:
    def __init__(self, power_usage_function: PowerUsageFunction) -> None:
        self.power_usage_function = power_usage_function

    @property
    def duration(self) -> timedelta:
        return self.power_usage_function.duration
    
    def is_scheduleable_at(self, start_time: datetime) -> bool:
        return True

class DatetimeInterval:
    def __init__(self, start: datetime, duration: timedelta = timedelta()) -> None:
        self.start = start
        self.duration = duration
    
    @property
    def end(self) -> datetime:
        return self.start + self.duration
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

class ScheduledTask:
    def __init__(self, start_interval: DatetimeInterval, task: Task) -> None:
        self.start_interval = start_interval
        self.task = task

    def get_price(self, price_function: SpotPriceFunction) -> float:
        power_price_function = PowerPriceFunction(
            self.task.power_usage_function, price_function
        )
        return power_price_function.integrate_from_to(self.start_interval.start, self.task.duration)

class Schedule:
    def __init__(self, tasks: List[ScheduledTask] = []) -> None:
        self.tasks = tasks

    def add(self, task: ScheduledTask) -> None:
        self.tasks.append(task)

    def get_total_price(self, price_function: SpotPriceFunction) -> float:
        total_price = 0.0
        for task in self.tasks:
            total_price += task.get_price(price_function)
        return total_price

    def copy(self) -> Schedule:
        return Schedule(self.tasks.copy())

class Scheduler:
    def __init__(
        self,
        price_function: SpotPriceFunction,
    ) -> None:
        self.price_function = price_function

    def get_available_start_times(
        self,
        task: Task,
        schedule: Optional[Schedule] = None
    ) -> List[datetime]:
        # Add all price function changes.
        seed_datetimes: List[datetime] = []
        current_datetime = self.price_function.min_domain
        while True:
            seed_datetimes.append(current_datetime)
            if current_datetime == self.price_function.max_domain:
                break

            # Get next start point.
            current_price_point = self.price_function.next_discrete_point_from(
                self.price_function.min_domain, current_datetime, self.price_function.max_domain
            )
            if current_price_point is None: break

            current_datetime = current_price_point.time

        # For each scheduled task add their start and end points.
        if not schedule is None:
            for scheduled_task in schedule.tasks:
                seed_datetimes.append(scheduled_task.start_interval.start)
                seed_datetimes.append(
                    scheduled_task.start_interval.start + scheduled_task.task.duration
                )

        # The optimal is either for a task to start or stop at each start point.
        task_start_points: List[datetime] = []
        for start_time in seed_datetimes:
            current_runtime: timedelta = timedelta()

            while True:
                start_time_offsetted = start_time

                # Given that the start point is valid:
                if self.price_function.is_valid_argument(start_time_offsetted):
                    # 1. We can schedule the start at "start_time" if the task can complete in the timespan.
                    later_start = start_time_offsetted + current_runtime
                    if self.price_function.is_valid_argument(later_start) and \
                        self.price_function.is_valid_argument(later_start + task.duration):
                        if not later_start in task_start_points:
                            task_start_points.append(later_start)

                    # 2. We can start the task earlier such that it completes at this time.
                    earlier_start = start_time_offsetted - current_runtime
                    if self.price_function.is_valid_argument(earlier_start) and \
                        self.price_function.is_valid_argument(earlier_start + task.duration):
                        if not earlier_start in task_start_points:
                            task_start_points.append(earlier_start)
                
                # Get next point.
                next_point = task.power_usage_function.next_discrete_point_from(
                    current_runtime, current_runtime, task.power_usage_function.max_domain
                )
                if next_point is None: break

                # Update the runtime to the next value.
                (next_runtime, _) = next_point
                current_runtime = next_runtime

        return task_start_points
    
    def can_schedule_task_at(self, task: Task, start_time: datetime) -> bool:
        # TODO: Add power consumption limitation.
        return task.is_scheduleable_at(start_time)

    def schedule_task_for(
        self,
        task: Task,
        schedule: Schedule    
    ) -> List[Schedule]:
        schedules = []

        start_times = self.get_available_start_times(task, schedule)
        for start_time in start_times:
            if not self.can_schedule_task_at(task, start_time):
                continue

            scheduled_task = ScheduledTask(
                DatetimeInterval(start_time, timedelta()), 
                task
            )
            new_schedule = schedule.copy()
            new_schedule.add(scheduled_task)
            schedules.append(new_schedule)

        return schedules
    
    def schedule_tasks_starting_with(
        self,
        seed_task: Task,
        tasks: List[Task],
        base_schedule: Schedule = Schedule()
    ) -> List[Schedule]:
        schedules: List[Schedule] = self.schedule_task_for(seed_task, base_schedule)

        # n' = n0 + 1 tasks in schedules
        for task in tasks:
            if task is seed_task: continue

            new_schedules: List[Schedule] = []
            for schedule in schedules:
                extended_schedules = self.schedule_task_for(task, schedule)
                for extended_schedule in extended_schedules:
                    new_schedules.append(extended_schedule)
            
            # We were unable to schedule any tasks to any of the current schedules.
            # This means that the schedule + seed_task disallows any of the tasks to be added.
            # Otherwise, we advance to n' = n + 1 by setting the schedules to the new ones.
            if len(new_schedules) == 0:
                return []
            else: schedules = new_schedules
        
        return schedules

    def schedule_tasks(
        self,
        tasks: List[Task],
        base_schedule: Schedule = Schedule()
    ) -> List[Schedule]:
        schedules: List[Schedule] = []
        for seed_task in tasks:
            for schedule in self.schedule_tasks_starting_with(seed_task, tasks, base_schedule):
                schedules.append(schedule)
        return schedules