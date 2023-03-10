import math
import datetime
from typing import List, Optional
from .eletricity_prices import PricePoint


class OptimalTimeCalculator2:
    def __init__(self):
        pass

    def calculate_optimal_time(price_points: List[PricePoint], power: Optional[int],
                               duration: Optional[datetime.time]) -> int:

        no_of_intervals = math.ceil(duration / 3600)
        lowestSum = float('inf')
        optimal_start_time = None

        # Earliest start time
        for i in range(len(price_points) - (no_of_intervals - 1)):
            currentSum = 0
            for j in range(no_of_intervals):
                currentSum += price_points[i + j].price
            averageSum = currentSum / no_of_intervals
            if averageSum < lowestSum:
                lowestSum = averageSum
                optimal_start_time = price_points[i].time

        # Latest start time
        for i in range(len(price_points) - 1, no_of_intervals - 2, -1):
            currentSum = 0
            for j in range(no_of_intervals):
                currentSum += price_points[i - j].price
            averageSum = currentSum / no_of_intervals
            if averageSum < lowestSum:
                lowestSum = averageSum
                optimal_start_time = price_points[i - no_of_intervals + 1].time

        return int(optimal_start_time.timestamp())


