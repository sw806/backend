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
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

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

    def get_potential_power_consumption_at(self, time: datetime) -> float:
        pass

class Scheduler:
    def __init__(self, price_function: SpotPriceFunction) -> None:
        self.price_function = price_function

    def can_schedule(self, schedule: Schedule, task: Task, start_time: datetime) -> bool:
        # Check that given the price information we have it is possible to run the task to completion.
        last_possible_start_time = self.price_function.max_domain - task.duration
        if start_time > last_possible_start_time:
            return False

        # Check if we try to start before or after we have prices.
        if not self.price_function.is_valid_argument(start_time):
            return False  

        # TODO: Check that we don't exceed the power consumption.

        return True

    def get_nearest_proceeding_datetime(
            self,
            start: datetime,
            min_step: timedelta,
            power_price_function: PowerPriceFunction
        ) -> Optional[datetime]:
        min_steped_next_domain = start + min_step

        # Get the next discrete point for the power price function.
        # We use (start, timedelta()) to denote the starting point where the task has not run yet.
        min_point = (start, timedelta())
        next_point = power_price_function.next_discrete_point_from(min_point, min_point, power_price_function.max_domain)

        # If we have a next point. Then, check if the next point is closer than the "min_step".
        if not next_point is None:
            (next_power_datetime, _) = power_price_function.get_domain(next_point)
            if power_price_function.spot_price_function.domain_order(next_power_datetime, min_steped_next_domain) < 0:
                min_steped_next_domain = next_power_datetime
        
        if not self.price_function.is_valid_argument(min_steped_next_domain):
            return None

        return min_steped_next_domain

    def schedule_task_at(
            self,
            start_of_interval: datetime,
            task: Task,
            schedule: Schedule = Schedule(),
            global_min_step: Optional[timedelta] = None
        ) -> List[ScheduledTask]:
        scheduled_tasks: List[ScheduledTask] = []

        power_price_function = PowerPriceFunction(
            task.power_usage_function, self.price_function
        )

        start_of_interval_price = power_price_function.integrate_from_to(start_of_interval, task.duration)
        
        # If we dont have a global min step then use the local one.
        if global_min_step is None:
            global_min_step = power_price_function.min_step

        end_of_interval = start_of_interval
        current_end_of_interval = end_of_interval

        # Check if it is possible to schedule the task at the initial time.
        if not self.can_schedule(schedule, task, current_end_of_interval):
            return scheduled_tasks

        while True:
            start_interval = DatetimeInterval(start_of_interval, end_of_interval - start_of_interval)
            scheduled_task = ScheduledTask(start_interval, task, start_of_interval_price)
            scheduled_tasks.append(scheduled_task)

            current_end_of_interval = self.get_nearest_proceeding_datetime(
                current_end_of_interval, global_min_step, power_price_function
            )

            if current_end_of_interval is None:
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

        return scheduled_tasks

    def schedule_task_for(
            self,
            schedule: Schedule,
            task: Task,
            global_min_step: Optional[timedelta] = None
        ) -> List[Schedule]:
        power_price_function = PowerPriceFunction(
            task.power_usage_function, self.price_function
        )

        # If we dont have a global min step then use the local one.
        if global_min_step is None:
            global_min_step = power_price_function.min_step

        schedules: List[Schedule] = []
        current_start_time = self.price_function.min_domain
        last_possible_start_time = self.price_function.max_domain - task.duration

        # Create a scheduled task for all possible timeslots.
        while current_start_time <= last_possible_start_time:

            # Schedule the task at the current start time.
            scheduled_tasks = self.schedule_task_at(current_start_time, task, schedule, global_min_step)
            for scheduled_task in scheduled_tasks:

                # Create a copy of the schedule and include the scheduled task.
                new_schedule = schedule.copy()
                new_schedule.add(scheduled_task)
                schedules.append(new_schedule)

                # Increment the current start time with the last possible end time of the scheduled task.
                start_interval = scheduled_task.start_interval
                current_start_time = start_interval.end

            current_start_time = self.get_nearest_proceeding_datetime(
                current_start_time, global_min_step, power_price_function
            )

            if current_start_time is None:
                break
        return schedules

    def schedule_tasks_starting_with(self, seed_task: Task, tasks: List[Task]) -> List[Schedule]:
        # Get the smallest duration of all tasks and use that as the globa minimum step
        global_min_step: timedelta = tasks[0].duration
        for task in tasks[1:]:
            if task.duration < global_min_step:
                global_min_step = task.duration

        # n = 0 tasks in schedule
        schedules: List[Schedule] = self.schedule_task_for(Schedule(), seed_task, global_min_step)
        for task in tasks:
            if task is seed_task: continue

            new_schedules: List[Schedule] = []

            # n' = n + 1 tasks in schedules.
            # Iterate all schedules and add all the possible new schdules with the extra task.
            for schedule in schedules:
                # Extend schedule (n) to (n+1) and add the new extended schedules.
                extended_schedules = self.schedule_task_for(schedule, task, global_min_step)
                new_schedules.append(extended_schedules)
            
            # If the amount of len of "new_schedules" is 0 then we cannot schedule the task.
            if len(new_schedules) == 0:
                schedules = []
                break

            # Advance n' to n + 1 be assign next iteration schedules.
            schedules = new_schedules
        
        return schedules
    
    def schedule_tasks(self, tasks: List[Task]) -> List[Schedule]:
        schedules: List[Schedule] = []
        for seed_task in tasks:
            for schedule in self.schedule_tasks_starting_with(seed_task, tasks):
                schedules.append(schedule)
        return schedules