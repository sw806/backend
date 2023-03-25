from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Generic, List, Optional
from collections.abc import Iterator
from infrastructure.function import TDomain, TCodomain, TIntegral
from infrastructure.discrete_function import DiscreteFunction, TDiscretePoint
from infrastructure.power_price_function import PowerPriceFunction
from infrastructure.spot_price_function import SpotPriceFunction
from infrastructure.power_usage_function import PowerUsageFunction

class TaskValidator(ABC):
    def __init__(self) -> None:
        super().__init__()

    def datetimes_of_interest(self, task: Task, start_time: datetime) -> List[datetime]:
        return []

    @abstractmethod
    def validate(self, task: Task, start_time: datetime) -> bool:
        pass

class MustStartBetweenValidator(TaskValidator):
    def __init__(self, start_time_interval: DatetimeInterval) -> None:
        super().__init__()
        self.start_time_interval = start_time_interval
    
    def datetimes_of_interest(self, task: Task, start_time: datetime) -> List[datetime]:
        return [self.start_time_interval.start, self.start_time_interval.end]

    def validate(self, task: Task, start_time: datetime) -> bool:
        return start_time >= self.start_time_interval.start and \
            start_time <= self.start_time_interval.end

class MustEndBetweenValidator(TaskValidator):
    def __init__(self, end_time_interval: DatetimeInterval) -> None:
        super().__init__()
        self.end_time_interval = end_time_interval
    
    def datetimes_of_interest(self, task: Task, start_time: datetime) -> List[datetime]:
        return [self.end_time_interval.start, self.end_time_interval.end]

    def validate(self, task: Task, start_time: datetime) -> bool:
        end_time = start_time + task.duration
        return end_time >= self.end_time_interval.start and \
            end_time <= self.end_time_interval.end

class ScheduleValidator(ABC):
    def __init__(self) -> None:
        super().__init__()

    def datetimes_of_interest(self, schedule: Schedule, task: Task, start_time: datetime) -> List[datetime]:
        return []

    @abstractmethod
    def validate(self, schedule: Schedule, task: Task, start_time: datetime) -> bool:
        pass

class MaximumPowerConsumptionValidator(ScheduleValidator):
    def __init__(self, maximum_consumption: float) -> None:
        super().__init__()
        self.maximum_consumption = maximum_consumption

    def power_consumption_at(self, tasks: List[ScheduledTask], time: datetime) -> float:
        power_consumption = 0.0
        for scheduled_task in tasks:
            power_consumption += scheduled_task.get_power_consumption_at(time)
        return power_consumption

    def next_power_consumption_from(self, tasks: List[ScheduledTask], time: datetime) -> Optional[datetime]:
        next = None

        for scheduled_task in tasks:
            # Check if the schedule is running at the given "time".
            if not scheduled_task.runs_at(time):
                continue

            # We know it is running then we have to get the succeeding point from the given "time".
            runtime = time - scheduled_task.start_interval.start
            next_point = scheduled_task.task.power_usage_function.next_discrete_point_from(
                scheduled_task.task.power_usage_function.min_domain, runtime, scheduled_task.task.power_usage_function.max_domain
            )

            # It might be that there are no succeeding point from the given "time".
            if next_point is None:
                continue

            # There was a next point but we have to check if the task is running.
            #   The complex reason for this is that the end time of the task is exclusive to its running time.
            #   This solves the problem of starting a task immediately when a task finish.
            #   If we did not do this then there sum time immediately at the start and finish could easily exceed the limit.
            next_domain = scheduled_task.task.power_usage_function.get_domain(next_point)
            next_datetime = time + next_domain
            if not scheduled_task.runs_at(next_datetime):
                continue

            # However, if there was one we have to check if that is the "closest" if so then we replace "next" with it.
            if next is None or next_datetime < next:
                next = next_datetime

        return next

    def validate(self, schedule: Schedule, task: Task, start_time: datetime) -> bool:
        current_time = start_time
        while not current_time is None:
            # Calculate runtime for task to schedule and check if it exceeds the task's duration.
            runtime = current_time - start_time
            if runtime > task.duration:
                break

            # Get the task power consumption.
            task_consumption = task.power_usage_function.apply(runtime)

            # Get power consumption at the current time.
            established_consumption = self.power_consumption_at(schedule.tasks, current_time)
            total_consumption = established_consumption + task_consumption
            
            # Check if we exceed the limit.
            if total_consumption > self.maximum_consumption:
                return False

            # We did not exceed the power consumption limit so we proceed to the next point.
            next_time = self.next_power_consumption_from(
                schedule.tasks, current_time
            )

            # Check if there was one if so then set current to be that.
            if next_time is None:
                break
            current_time = next_time

        return True

class DiscreteFunctionIterator(Iterator, Generic[TDomain, TCodomain, TIntegral, TDiscretePoint]):
    current: Optional[TDomain]

    def __init__(
        self,
        functions: List[DiscreteFunction[TDomain, TCodomain, TIntegral, TDiscretePoint]],
        start: Optional[TDomain] = None,
        end: Optional[TDomain] = None
    ) -> None:
        self.functions = functions

        # If start is None then it is the min domain for all functions.
        if start is None:
            start = functions[0].min_domain
        if end is None:
            end = functions[0].max_domain

        if len(functions) > 0:
            for function in functions[1:]:
                if not start is None:
                    min_domain = function.min_domain
                    if function.domain_order(min_domain, start) < 0:
                        start = min_domain
                    
                    max_domain = function.max_domain
                    if function.domain_order(max_domain, end) > 0:
                        end = max_domain

        self.current = start
        self.start = start
        self.end = end


    def get_next_from(self, argument: Optional[TDomain]) -> Optional[TDomain]:
        if argument is None: return None

        smallest_domain: Optional[TDomain] = None
        for function in self.functions:
            # Get the next point and check if there was one.
            next_point = function.next_discrete_point_from(
                function.min_domain, argument, function.max_domain
            )
            if next_point is None: continue

            # Deconstruct the point and check if it is the first or smaller than the smallest.
            next_domain = function.get_domain(next_point)
            if function.domain_order(next_domain, self.end) > 0:
                continue

            if smallest_domain is None or \
                function.domain_order(next_domain, smallest_domain) < 0:
                smallest_domain = next_domain
        return smallest_domain

    def __next__(self) -> Optional[TDomain]:
        if self.current is None:
            raise StopIteration

        temp = self.current
        self.current = self.get_next_from(self.current)
        return temp

class Task:
    def __init__(
        self,
        power_usage_function: PowerUsageFunction,
        earliest_possible_start_time: Optional[datetime] = None,
        latest_possible_end_time: Optional[datetime] = None,
    ) -> None:
        self.power_usage_function = power_usage_function
        self.earliest_possible_start_time = earliest_possible_start_time
        self.latest_possible_end_time = latest_possible_end_time

    @property
    def duration(self) -> timedelta:
        return self.power_usage_function.duration
    
    def is_scheduleable_at(self, start_time: datetime) -> bool:
        # TODO: Use the Validator pattern here instead.
        # Check that the start time is not before the earliest time.
        if not self.earliest_possible_start_time is None:
            if start_time < self.earliest_possible_start_time:
                return False

        # Check that the end time does not exceed the latest time.
        if not self.latest_possible_end_time is None:
            end_time: datetime = start_time + self.power_usage_function.duration
            if end_time > self.latest_possible_end_time:
                return False

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
        else: return False

class ScheduledTask:
    def __init__(self, start_interval: DatetimeInterval, task: Task) -> None:
        self.start_interval = start_interval
        self.task = task

    @property
    def end_interval(self) -> DatetimeInterval:
        return DatetimeInterval(
            self.start_interval.start + self.task.duration,
            self.start_interval.duration
        )

    def runs_at(self, time: datetime) -> bool:
        earliest_start_time = self.start_interval.start
        last_end_time = (earliest_start_time + self.start_interval.duration) + self.task.duration
        return time >= earliest_start_time and time < last_end_time

    def get_power_consumption_at(self, time: datetime) -> float:
        if not self.runs_at(time):
            return 0

        duration = time - self.start_interval.start
        return self.task.power_usage_function.apply(duration)

    def get_next_power_usage_date(self, time: datetime) -> Optional[datetime]:
        if not self.runs_at(time):
            return None
        
        duration = time - self.start_interval.start
        next_point = self.task.power_usage_function.next_discrete_point_from(
            self.task.power_usage_function.min_domain, duration, self.task.power_usage_function.max_domain
        )
        
        if next_point is None:
            return None

        next_domain = self.task.power_usage_function.get_domain(next_point)
        return time + next_domain

    def get_price(self, price_function: SpotPriceFunction) -> float:
        power_price_function = PowerPriceFunction(
            self.task.power_usage_function, price_function
        )
        return power_price_function.integrate_from_to(
            self.start_interval.start, self.task.duration
        )

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

    def can_schedule_task_at(self, task: Task, start_time: datetime) -> bool:
        # TODO: Use the validator pattern here.
        if not task.is_scheduleable_at(start_time):
            return False

        # Check that we dont exceed the maximum power consumption.
        if not MaximumPowerConsumptionValidator(3).validate(self, task, start_time):
            return False

        return True

    def copy(self) -> Schedule:
        return Schedule(self.tasks.copy())

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

        # For each scheduled task add their start and end points as seeds.
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

            # TODO: Refactor to use DiscreteFunctionIterator.
            while True:
                # Given that the start point is valid:
                if self.price_function.is_valid_argument(start_time):
                    # 1. We can schedule the start at "start_time" if the task can complete in the timespan.
                    later_start = start_time + current_runtime
                    if self.price_function.is_valid_argument(later_start) and \
                        self.price_function.is_valid_argument(later_start + task.duration):
                        if not later_start in task_start_points:
                            task_start_points.append(later_start)

                    # 2. We can start the task earlier such that it completes at this time.
                    earlier_start = start_time - current_runtime
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