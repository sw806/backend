from typing import Dict, List
from .schedule import Schedule
from .schedules_recommender import SchedulesRecommender
from .spot_price_function import SpotPriceFunction
from infrastructure.co2_emission_function import Co2EmissionFunction

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

class LowestPriceRecommender(SchedulesRecommender[Schedule]):
    highest_scheduled_task_prices: Dict[str, float]
    highest_scheduled_emission: Dict[str, float]

    def __init__(
            self,
            price_function: SpotPriceFunction,
            emission_function: Co2EmissionFunction
        ) -> None:
        super().__init__()
        self.price_function = price_function
        self.emission_function = emission_function
        self.highest_scheduled_task_prices = {}
        self.highest_scheduled_emission = {}

    def recommend(self, schedules: List[Schedule]) -> Schedule:
        with tracer.start_as_current_span("RecommendLowestPrice"):
            lowest = schedules[0]

            for schedule in schedules[1:]:
                if schedule.get_total_price(self.price_function) < lowest.get_total_price(self.price_function):
                    lowest = schedule

                # Go through and see if the task prices are new highs.
                for scheduled_task in schedule.tasks:
                    if scheduled_task.task.id is not None:
                        # It is the first entry of the scheduled task price
                        # Or we have an existing price and wont to check if this one is worse.
                        if scheduled_task.task.id not in self.highest_scheduled_task_prices:
                            self.highest_scheduled_task_prices[scheduled_task.task.id] = scheduled_task.cost
                        else:
                            if self.highest_scheduled_task_prices[scheduled_task.task.id] < scheduled_task.cost:
                                self.highest_scheduled_task_prices[scheduled_task.task.id] = scheduled_task.cost

            return lowest