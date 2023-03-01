from abc import ABC, abstractmethod
from datetime import time

class ElectricityPrices(ABC):
    @abstractmethod
    def get_prices(self, start_date: time , end_date: time) -> list:
        pass