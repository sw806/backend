from abc import ABC, abstractmethod
from datetime import time, datetime
from typing import List, Optional

class PricePoint:
    def __init__(self, time: datetime, price: float) -> None:
        self.time = time
        self.price = price

    def to_dict(self):
        return {
            'time': self.time.isoformat(),
            'price': self.price
        }

class ElectricityPrices(ABC):
    @abstractmethod
    def get_prices(self, start: Optional[datetime] = None , end: Optional[datetime] = None) -> List[PricePoint]:
        pass