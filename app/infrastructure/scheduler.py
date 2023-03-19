from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Optional
from infrastructure.spot_price_function import SpotPriceFunction
from infrastructure.power_usage_function import PowerUsageFunction
from infrastructure.power_price_function import PowerPriceFunction


class Task:
    def __init__(self, power_usage_function: PowerUsageFunction) -> None:
        self.power_usage_function = power_usage_function

    @property
    def duration(self) -> timedelta:
        return self.power_usage_function.duration

class DatetimeInterval:
    def __init__(self, start: datetime, duration: timedelta = timedelta()) -> None:
        self.start = start
        self.duration = duration
    
    @property
    def end(self) -> datetime:
        return self.start + self.duration

class ScheduledTask:
    def __init__(self, start_interval: DatetimeInterval, task: Task, price: float) -> None:
        self.start_interval = start_interval
        self.task = task
        self.price = price

class Schedule:
    def __init__(self, tasks: List[ScheduledTask] = []) -> None:
        price = 0.0
        for task in tasks: price += task.price

        self.tasks = tasks
        self.price = price

    def add(self, task: ScheduledTask) -> None:
        self.tasks.append(task)
        self.price += task.price

    def copy(self) -> Schedule:
        return Schedule(self.tasks.copy())

class Scheduler:
    def __init__(self, price_function: SpotPriceFunction) -> None:
        self.price_function = price_function

    def can_schedule(self, schedule: Schedule, task: Task, start_time: datetime) -> bool:
        return True

    def schedule_task_at(self, start_of_interval: datetime, task: Task, schedule: Schedule = Schedule()) -> Optional[ScheduledTask]:
        power_price_function = PowerPriceFunction(
            task.power_usage_function, self.price_function
        )

        last_possible_start_time = self.price_function.max_domain - task.duration
        start_of_interval_price = power_price_function.integrate_from_to(start_of_interval, task.duration)

        # Check if we try to start before or after we have prices.
        if not power_price_function.spot_price_function.is_valid_argument(start_of_interval):
            return None

        # Check that given the price information we have it is possible to run the task.
        if last_possible_start_time < start_of_interval:
            return None
        
        # Check if it is possible to schedule the task at the initial time.
        if not self.can_schedule(schedule, task, start_of_interval):
            return None

        end_of_interval = start_of_interval
        current_end_of_interval = end_of_interval
        while True:
            # Add the smallest possible step from the power price function.
            current_end_of_interval += power_price_function.min_step

            # Check if we exceed the bounds of what is possible.
            if current_end_of_interval > last_possible_start_time:
                break

            # Check that the task can be still be scheduled.
            if not self.can_schedule(schedule, task, current_end_of_interval):
                break

            # Only continue incrementing the end_time if the new bounds does not change in price.
            # TODO: Optimize this integral computation to only be the delta? (Reduced from the start - added to the end)
            current_end_of_interval_price = power_price_function.integrate_from_to(current_end_of_interval, task.duration)
            if start_of_interval_price != current_end_of_interval_price:
                break

            # No checks failed so increase the end_time to be the current_time.
            end_of_interval = current_end_of_interval

        start_interval = DatetimeInterval(start_of_interval, end_of_interval - start_of_interval)
        return ScheduledTask(start_interval, task, start_of_interval_price)

    def schedule_helper(self, schedule: Schedule, task: Task) -> List[Schedule]:
        power_price_function = PowerPriceFunction(
            task.power_usage_function, self.price_function
        )

        schedules: List[Schedule] = []
        current_start_time = self.price_function.min_domain
        last_possible_start_time = self.price_function.max_domain - task.duration
        while current_start_time <= last_possible_start_time:
            # Schedule the task at the current start time.
            scheduled_task = self.schedule_task_at(current_start_time, task, schedule)

            # If None is returned then we have to advance time to not end in a deadlock.
            # This can happen if the start time disallows the scheduling of the task at that time.
            # FIXME: Also, if there is not enough time to finish the task, and time is an invalid argument for spot prices (No data).
            if scheduled_task is None:
                current_start_time += power_price_function.min_step
            
            # Create a copy of the schedule and include the scheduled task.
            new_schedule = schedule.copy()
            new_schedule.add(scheduled_task)
            schedules.append(new_schedule)

            # Increment the current start time with the last possible end time of the scheduled task.
            start_interval = scheduled_task.start_interval
            current_start_time = start_interval.end + task.duration
        return schedules
            # FIXME: Is this possible to reach?

    def schedule(self, task: Task) -> Schedule:
        schedules = self.schedule_helper(Schedule(), task)
        cheapest_schedule = schedules[0]
        for schedule in schedules[1:]:
            if schedule.price < cheapest_schedule.price:
                cheapest_schedule = schedule
        return schedule