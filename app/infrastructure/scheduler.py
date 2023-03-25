from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Generic, List, Optional
from collections.abc import Iterator
from infrastructure.datetime_interval import DatetimeInterval
from infrastructure.schedule import Schedule
from infrastructure.schedule_task import ScheduledTask
from infrastructure.task import Task
from infrastructure.function import TDomain, TCodomain, TIntegral
from infrastructure.discrete_function import DiscreteFunction, TDiscretePoint
from infrastructure.power_price_function import PowerPriceFunction
from infrastructure.spot_price_function import SpotPriceFunction
from infrastructure.power_usage_function import PowerUsageFunction


class Scheduler:
    def __init__(
        self,
        price_function: SpotPriceFunction,
    ) -> None:
        self.price_function = price_function

    def get_all_possible_start_times(
        self,
        task: Task,
        schedule: Optional[Schedule] = None
    ) -> List[datetime]:
        # Add all price function changes as seeds.
        seed_datetimes = [
            self.price_function.get_domain(point)
            for point in self.price_function.get_all_discrete_points()
        ]

        # For each scheduled task we also use there relevant datetimes as seeds.
        if not schedule is None:
            for scheduled_task in schedule.tasks:
                for relevant_time in scheduled_task.derieve_start_times():
                    seed_datetimes.append(relevant_time)

        # Calculate all the relevant datetimes for the task relvative to the seeds.
        relevant_datetimes = []
        for start_time in seed_datetimes:
            for relevant_time in task.derieve_start_times(start_time):
                if not (self.price_function.is_valid_argument(relevant_time) and \
                        self.price_function.is_valid_argument(relevant_time + task.duration)):
                    continue

                if not relevant_time in relevant_datetimes:
                    relevant_datetimes.append(relevant_time)

        return relevant_datetimes

    def schedule_task_for(
        self,
        task: Task,
        schedule: Schedule
    ) -> List[Schedule]:
        schedules = []

        # For each of the start times we can create a new schedule with the task schduled at that time.
        start_times = self.get_all_possible_start_times(task, schedule)
        for start_time in start_times:
            # If the task cannot be scheduled because of e.g. time and total power constraint.
            if not schedule.can_schedule_task_at(task, start_time):
                continue

            scheduled_task = ScheduledTask(
                DatetimeInterval(start_time, timedelta()), 
                task
            )

            # Create a copy of the schdule and add the new scheduled task to the copy.
            # We create a copy such that it is a new schedule we are working on.
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