from abc import ABC, abstractmethod
from datetime import time, datetime
from typing import List

class PricePoint:
    def __init__(self) -> None:
        self.time: datetime
        self.price: float

class ElectricityPrices(ABC):
    @abstractmethod
    def get_prices(self, start_time: time , end_time: time) -> List[PricePoint]:
        pass