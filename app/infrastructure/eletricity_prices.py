from abc import ABC, abstractmethod
from datetime import time
from typing import List

class PricePoint:
    def __init__(self) -> None:
        pass

class ElectricityPrices(ABC):
    @abstractmethod
    def get_prices(self, start_date: time , end_date: time) -> List[PricePoint]:
        pass