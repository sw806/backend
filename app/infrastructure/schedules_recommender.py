from abc import ABC, abstractmethod
from typing import List, Generic, TypeVar
from .schedule import Schedule

TRecommendation = TypeVar("TRecommendation")

class SchedulesRecommender(ABC, Generic[TRecommendation]):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def recommend(self, schedules: List[Schedule]) ->TRecommendation:
        pass