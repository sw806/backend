from datetime import datetime, timedelta
from typing import List, Optional
from infrastructure.schedule import Schedule, ScheduleValidator
from infrastructure.schedule_task import ScheduledTask
from infrastructure.task import Task


class MaximumPowerConsumptionValidator(ScheduleValidator):
    def __init__(self, maximum_consumption: float) -> None:
        super().__init__()
        self.maximum_consumption = maximum_consumption

    def power_consumption_at(self, tasks: List[ScheduledTask], time: datetime) -> float:
        power_consumption = 0.0
        for scheduled_task in tasks:
            power_consumption += scheduled_task.get_max_power_consumption_at(time)
        return power_consumption

    def next_power_consumption_from(self, tasks: List[ScheduledTask], time: datetime) -> Optional[datetime]:
        next = None

        for scheduled_task in tasks:
            # Either the ext point for the task is that it is starting or that it has been running.
            runtime = time - scheduled_task.start_interval.start

            # Either the task has not started yet and the enxt point is its start or it ccontinues from runtime.
            if runtime < timedelta():
                next_datetime = scheduled_task.start_interval.start
            else:
                next_point = scheduled_task.task.power_usage_function.next_discrete_point_from(
                    scheduled_task.task.power_usage_function.min_domain, runtime, scheduled_task.task.power_usage_function.max_domain
                )

                # It might be that there are no succeeding point from the given "time".
                if next_point is None:
                    continue

                next_domain = scheduled_task.task.power_usage_function.get_domain(next_point)

                # There was a next point but we have to check if the task is running.
                #   The complex reason for this is that the end time of the task is exclusive to its running time.
                #   This solves the problem of starting a task immediately when a task finish.
                #   If we did not do this then there sum time immediately at the start and finish could easily exceed the limit.
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
            if runtime >= task.duration:
                break

            # Get the task power consumption.
            task_consumption = task.power_usage_function.apply(runtime)

            # Get power consumption at the current time.
            established_consumption = self.power_consumption_at(schedule.tasks, current_time)
            total_consumption = established_consumption + task_consumption

            # Check if we exceed the limit.
            if total_consumption > self.maximum_consumption:
                return False

            # The next point might be the next power usage point and not schedule power usage point.
            next_power_consumption_point = task.power_usage_function.next_discrete_point_from(
                timedelta(), runtime, task.duration
            )

            # We did not exceed the power consumption limit so we proceed to the next point.
            next_time = self.next_power_consumption_from(
                schedule.tasks, current_time
            )

            # If we have a succeeding power consumption point then we should consider it
            if next_power_consumption_point is not None:
                next_runtime = next_power_consumption_point[0]
                next_runtime_time = next_runtime + current_time

                # Either we dont have a next time and can just use next runtime time or
                # the power consumption point is the closest then that is the next step.
                if next_time is None:
                    next_time = next_runtime_time
                elif next_runtime_time < current_time:
                    next_time = next_runtime_time

            # Check if there was one if so then set current to be that.
            if next_time is None:
                break
            current_time = next_time

        return True