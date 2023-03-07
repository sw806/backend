from abc import ABC, abstractmethod
from datetime import time, datetime
from typing import List

class PricePoint:
    def __init__(self, time: datetime, price: float) -> None:
        self.time = time
        self.price = price

class ElectricityPrices(ABC):
    @abstractmethod
    def get_prices(self, start_time: datetime , end_time: datetime) -> List[PricePoint]:
        pass