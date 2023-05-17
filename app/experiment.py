from datetime import datetime, timedelta, timezone
import sys
from typing import Dict, List, Optional, Tuple

from infrastructure.eletricity_prices import PricePoint
from infrastructure.eds_requests import EdsRequests
from infrastructure.task import Task
from infrastructure.spot_price_function import SpotPriceFunction
from infrastructure.scheduler import Scheduler
from infrastructure.power_usage_function_factory import PowerUsageFunctionFactory

price_points = EdsRequests().get_prices(
    datetime(2023, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc),
    datetime(2023, 5, 3, 0, 0, 0, 0, tzinfo=timezone.utc)
)

print(f'Found {len(price_points)} price points')
print(f'Earliest price point: {price_points[0].time}')
print(f'Latest price point: {price_points[-1].time}')

# for price_point in price_points:
#     if price_point.price < 0:
#         print(f'Found a negative price :: {price_point.price} at {price_point.time}')

print("Prices")
print(f'Date, Price (dkk/kWh)')
for price_point in price_points:
    print(f'{price_point.time}, {price_point.price}')
print("")

def get_available_price_points_from(start: datetime, include_dayahead: bool = False, end: Optional[datetime] = None) -> List[PricePoint]:
    assert start <= price_points[-1].time

    last_available_spot_price_time = datetime(
        start.year, start.month, start.day, start.hour, 0, 0, 0, tzinfo=timezone.utc
    )
    if end is None:
        if include_dayahead:
            if last_available_spot_price_time.hour > 11:
                # The spot prices have already been released so the next release is tomorrow.
                last_available_spot_price_time = last_available_spot_price_time.replace(
                    day=last_available_spot_price_time.day,
                    hour=21, # It is not 23 because we work with utc
                    minute=0,
                    second=0
                ) + timedelta(days=1)
            else:
                # The spot prices have NOT been released yet.
                last_available_spot_price_time = last_available_spot_price_time.replace(
                    day=last_available_spot_price_time.day,
                    hour=22,
                    minute=0,
                    second=0
                )
        else:
            last_available_spot_price_time = last_available_spot_price_time.replace(
                hour=22
            )
    else: last_available_spot_price_time = end
    
    assert start < last_available_spot_price_time
    assert last_available_spot_price_time <= price_points[-1].time

    included_price_points: List[PricePoint] = []
    for price_point in price_points:
        if price_point.time >= start and price_point.time <= last_available_spot_price_time:
            included_price_points.append(price_point)

    return included_price_points

class Result:
    def __init__(
        self,
        scheduler_time: datetime,
        min_price: float, min_time: datetime,
        max_price: float, max_time: datetime,
        avg_price: float) -> None:
        self.scheduler_time = scheduler_time
        self.min_price = min_price
        self.min_time = min_time
        self.max_price = max_price
        self.max_time = max_time
        self.avg_price = avg_price

def analyse_at_time(start: datetime, task: Task, include_dayahead: bool = False, end: Optional[datetime] = None) -> Result:
    price_points = get_available_price_points_from(start, include_dayahead, end)
    price_function = SpotPriceFunction(price_points)

    scheduler = Scheduler(price_function)
    schedules = scheduler.schedule_tasks([task])

    min_price = sys.float_info.max
    min_time = datetime.now(tz=timezone.utc)
    max_price = sys.float_info.min
    max_time = datetime.now(tz=timezone.utc)
    total_price = 0.0

    for schedule in schedules:
        assert len(schedule.tasks) == 1
        price = schedule.get_total_price(price_function)

        if price < min_price: 
            min_price = price
            min_time = schedule.tasks[0].start_interval.start
        if price > max_price: 
            max_price = price
            max_time = schedule.tasks[0].end_interval.start
        total_price += price

    avg = total_price / len(schedules)

    return Result(start, min_price, min_time, max_price, max_time, avg)

def create_constant_power_task(duration: timedelta, power: float) -> Task:
    power_factory = PowerUsageFunctionFactory()
    power_function = power_factory.create_constant_consumption(duration, power)
    return Task(power_function)


def get_results(step: timedelta, duration: timedelta) -> List[Result]:
    print('')
    print(f'Results from {price_points[0].time} to {price_points[-1].time}')

    min_start_time = price_points[0].time
    max_end_time = datetime(2023, 4, 30, 13, 0, 0, 0, tzinfo=timezone.utc)
    start_time = min_start_time

    results = []

    while start_time < max_end_time:
        result = analyse_at_time(
            start_time,
            create_constant_power_task(duration, 1),
            True
        )
        results.append(result)

        # print(f'Result: Scheduled from={start_time} min={result.min} at={result.min_time}, max={result.max} at={result.max_time}, avg={result.avg}')

        start_time = start_time + step

    return results

class AggregatedResults():
    def __init__(
            self,
            duration: timedelta,
            avg_min_max_saving: float,
            avg_min_avg_saving: float,
            min_max_and_min_avg_saving_per_time: Dict[timedelta, Tuple[float, float]],
            results_per_time: Dict[timedelta, List[Result]]
        ) -> None:
        self.duration = duration
        self.avg_min_max_saving = avg_min_max_saving
        self.avg_min_avg_saving = avg_min_avg_saving
        self.min_max_and_min_avg_saving_per_time = min_max_and_min_avg_saving_per_time
        self.results_per_time = results_per_time

def compute_aggregate_result(duration: timedelta) -> AggregatedResults:
    results = get_results(
        step=timedelta(hours=1),
        duration=duration
    )
    total_min_max_saving = 0.0
    total_min_avg_saving = 0.0

    results_per_time: Dict[timedelta, List[Result]] = {}

    for result in results:
        total_min_max_saving += result.max_price - result.min_price
        total_min_avg_saving += result.avg_price - result.min_price

        time_into_day: timedelta = result.scheduler_time - result.scheduler_time.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        if time_into_day not in results_per_time:
            results_per_time[time_into_day] = [result]

    avg_min_max_saving = total_min_max_saving / len(results)
    avg_min_avg_saving = total_min_avg_saving / len(results)

    min_max_and_min_avg_saving_per_time: Dict[timedelta, Tuple[float, float]] = {}
    for time in results_per_time:
        time_results = results_per_time[time]

        avg_min_max_saving = 0.0
        avg_min_avg_saving = 0.0

        for (idx, result) in enumerate(time_results):
            min_max_saving = result.max_price - result.min_price
            avg_min_max_saving = (avg_min_max_saving * idx + min_max_saving) / (idx + 1)

            min_avg_saving = result.avg_price - result.min_price
            avg_min_avg_saving = (avg_min_avg_saving * idx + min_avg_saving) / (idx + 1)

        min_max_and_min_avg_saving_per_time[time] = (avg_min_max_saving, avg_min_avg_saving)

    return AggregatedResults(
        duration, avg_min_max_saving, avg_min_avg_saving, min_max_and_min_avg_saving_per_time, results_per_time
    )

duration = timedelta(minutes=15)
duration_step = timedelta(minutes=15)

while duration <= timedelta(hours=6):
    aggregated_result = compute_aggregate_result(duration)
    t = create_constant_power_task(duration, 1)

    print('')
    print(f'Task with duration of: {aggregated_result.duration}')
    print('')
    print('Test the amount of savings by scheduling action time')
    print(f'avg_min_max_saving: {aggregated_result.avg_min_max_saving}')
    print(f'avg_min_avg_saving: {aggregated_result.avg_min_avg_saving}')

    print('Time, avg_min_max_savings, avg_min_avg_savings')
    for time in aggregated_result.min_max_and_min_avg_saving_per_time:
        (avg_min_max_savings, avg_min_avg_savings) = aggregated_result.min_max_and_min_avg_saving_per_time[time]
        print(f'{time}, {avg_min_max_savings}, {avg_min_avg_savings}')

    print('')

    print('Test the cost of running appliances in "sleep", "work", "off"')

    initial_start = datetime(2023, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
    initial_end = datetime(2023, 4, 30, 13, 0, 0, 0, tzinfo=timezone.utc)
    current = initial_start
    
    print('The cost of running it either when sleeping, working, or off')
    print(', Sleep (0-8),,,,, Work (8-16),,,,, Off (16-24)')
    print('Time, min price (dkk), min time, max price (dkk), max time, avg price, min price (dkk), min time, max price (dkk), max time, avg price, min price (dkk), min time, max price (dkk), max time, avg price')
    while current < initial_end:
        # Sleep 24-8
        sleep_start = current.replace(hour=0)
        sleep_end = current.replace(hour=7)
        sleep_result: Result = analyse_at_time(sleep_start, t, end=sleep_end)

        # Work 8-16
        work_start = current.replace(hour=8)
        work_end = current.replace(hour=15)
        work_result: Result = analyse_at_time(work_start, t, end=work_end)

        # Off 16-24
        off_start = current.replace(hour=16)
        off_end = current.replace(hour=23)
        off_result: Result = analyse_at_time(off_start, t, end=off_end)

        print(f'{current}, {sleep_result.min_price}, {sleep_result.min_time}, {sleep_result.max_price}, {sleep_result.max_time}, {sleep_result.avg_price}, {work_result.min_price}, {work_result.min_time}, {work_result.max_price}, {work_result.max_time}, {work_result.avg_price}, {off_result.min_price}, {off_result.min_time}, {off_result.max_price}, {off_result.max_time}, {off_result.avg_price}')

        current += timedelta(days=1)

    print('')

    duration += duration_step
