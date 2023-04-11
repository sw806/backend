from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from infrastructure.eletricity_prices import PricePoint
from infrastructure.datetime_interval import DatetimeInterval
from infrastructure.schedule import Schedule
from infrastructure.schedule_task import ScheduledTask
from infrastructure.task import Task
from infrastructure.spot_price_function import SpotPriceFunction
from infrastructure.discrete_function_iterator import DiscreteFunctionIterator
from infrastructure.power_price_function import PowerPriceFunction


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

        # The task can possibly also be cosntrained in such a way that it has custom starting points.
        for start_time in task.start_times():
            seed_datetimes.append(start_time)

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

    def get_all_possible_extrapolated_start_times(
        self,
        task: Task,
        schedule: Optional[Schedule] = None
    ) -> List[DatetimeInterval]:
        if schedule is None:
            schedule = Schedule()

        intervals: List[DatetimeInterval] = []
        all_start_points = self.get_all_possible_start_times(task, schedule)

        # Make sure that the times are sorted in ascending order.
        all_start_points.sort(reverse=False)

        if len(all_start_points) == 0:
            return []

        for start_time in all_start_points:
            if not schedule.can_schedule_task_at(task, start_time):
                continue

            for end_time in all_start_points:
                if end_time < start_time:
                    continue

                scheduleable = schedule.can_schedule_task_at(task, end_time)

                if start_time is None and scheduleable:
                    start_time = end_time

                if start_time is not None and scheduleable:
                    interval = DatetimeInterval(start_time, end_time - start_time)
                    intervals.append(interval)

        return intervals

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

            power_price_function = PowerPriceFunction(
                task.power_usage_function, self.price_function
            )
            scheduled_task = ScheduledTask(
                DatetimeInterval(start_time, timedelta()), 
                task,
                power_price_function.integrate_from_to(start_time, task.duration)
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
        tasks: List[Task] = [],
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
        schedule: Schedule = Schedule()
    ) -> List[Schedule]:
        schedules: List[Schedule] = []
        for seed_task in tasks:
            for schedule in self.schedule_tasks_starting_with(seed_task, tasks, schedule):
                schedules.append(schedule)
        return schedules