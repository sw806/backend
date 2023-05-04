import math
from datetime import datetime, timedelta
from typing import List, Optional
from .eletricity_prices import PricePoint

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

class OptimalTimeCalculator:
    def __init__(self) -> None:
        pass

    def calculate_optimal_time(self, price_points: List[PricePoint], duration: timedelta) -> int:
        with tracer.start_as_current_span("CalculateOptimalTime"):
            has_incomplete_interval = False
            no_of_complete_intervals = int(duration.seconds / 3600)
            size_of_incomplete_intervals = duration.seconds % 3600
            if size_of_incomplete_intervals != 0:
                no_of_intervals = no_of_complete_intervals + 1
                has_incomplete_interval = True
            else:
                no_of_intervals = no_of_complete_intervals
            lowestSum = float('inf')
            optimal_start_time: datetime = price_points[0].time

            # Begin from earliest start time
            for i in range(len(price_points) - (no_of_intervals - 1)):
                sum: float = 0.0
                for j in range(no_of_intervals):
                    if has_incomplete_interval and j != no_of_intervals - 1:
                        sum += price_points[i + j].price
                    elif has_incomplete_interval and j == no_of_intervals - 1:
                        sum += price_points[i + j].price * (size_of_incomplete_intervals / 3600)
                    elif not has_incomplete_interval:
                        sum += price_points[i + j].price
                if sum < lowestSum:
                    lowestSum = sum
                    optimal_start_time = price_points[i].time

            # Begin from latest start time
            if has_incomplete_interval:
                for i in range(len(price_points) - 1, no_of_intervals - 2, -1):
                    sum = 0
                    for j in range(no_of_intervals):
                        if has_incomplete_interval and j != no_of_intervals - 1:
                            sum += price_points[i - j].price
                        elif has_incomplete_interval and j == no_of_intervals - 1:
                            sum += price_points[i - j].price * (size_of_incomplete_intervals / 3600)
                    if sum < lowestSum:
                        lowestSum = sum
                        optimal_start_time = price_points[i - no_of_intervals + 1].time + \
                            (timedelta(hours=1) - timedelta(seconds=size_of_incomplete_intervals))

            return int(optimal_start_time.timestamp())
