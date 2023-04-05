from typing import List
from .schedule import Schedule
from .schedules_recommender import SchedulesRecommender
from .spot_price_function import SpotPriceFunction

class LowestPriceRecommender(SchedulesRecommender[Schedule]):
    def __init__(self, price_function: SpotPriceFunction) -> None:
        super().__init__()
        self.price_function = price_function

    def recommend(self, schedules: List[Schedule]) -> Schedule:
        lowest = schedules[0]
        for schedule in schedules[1:]:
            if schedule.get_total_price(self.price_function) < lowest.get_total_price(self.price_function):
                lowest = schedule
        return lowest