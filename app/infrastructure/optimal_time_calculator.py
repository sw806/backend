import math
import datetime
from typing import List, Optional
from eletricity_prices import PricePoint
from edsfetcher import EDSFetcher

class OptimalTimeCalculator:
    def __init__(self):
        pass

    def calculate_optimal_time(self, price_points: List[PricePoint], energy: Optional[int], power: Optional[int],
                               duration: Optional[datetime.time]) -> datetime:
        # Har lige et par ting vi kan tale om ang. energy, power og duration
        if duration is None:
            if energy is None or power is None:
                raise ValueError("Both energy and power must be provided if duration is not specified")
            duration_hours = energy / power
            duration = datetime.timedelta(hours=duration_hours)

        no_of_intervals = math.ceil(duration.total_seconds() / 3600)
        lowestSum = float('inf')
        optimal_start_time = None
        for i in range(len(price_points) - (no_of_intervals - 1)):
            currentSum = 0
            for j in range(no_of_intervals):
                currentSum += price_points[i + j].price
            averageSum = currentSum / no_of_intervals
            if averageSum < lowestSum:
                lowestSum = averageSum
                optimal_start_time = price_points[i].time

        return optimal_start_time

if __name__ == "__main__":
    price_points = EDSFetcher('https://api.energidataservice.dk/dataset/Elspotprices?limit=50').get_prices()
    optimal_time_calculator = OptimalTimeCalculator()
    optimal_time = optimal_time_calculator.calculate_optimal_time(price_points, 3, 1, None)
    print("Optimal start time: ", optimal_time)

