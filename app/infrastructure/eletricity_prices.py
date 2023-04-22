from abc import ABC, abstractmethod
from datetime import time, datetime
from typing import Any, Dict, List, Optional
from pydantic.dataclasses import dataclass

@dataclass
class PricePoint:
    time: datetime
    price: float

    def __init__(self, time: datetime, price: float) -> None:
        self.time = time
        self.price = price

    def to_dict(self) -> Dict[str, Any]:
        return {
            'time': self.time.isoformat(),
            'price': self.price
        }

class ElectricityPrices(ABC):
    @abstractmethod
    def get_prices(self, start: Optional[datetime] = None , end: Optional[datetime] = None) -> List[PricePoint]:
        pass