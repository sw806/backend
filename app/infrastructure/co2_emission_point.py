from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic.dataclasses import dataclass


@dataclass
class Co2EmissionPoint:
    time: datetime
    emission: float
    
    def __init__(self, time: datetime, emission: float) -> None:
        self.time = time
        self.emission = emission

    def to_dict(self) -> Dict[str, Any]:
        return {
            'time': self.time.isoformat(),
            'CO2 emission (g/kWh)': self.emission
        }

class CO2EmissionsRepository(ABC):
    @abstractmethod
    def get_co2_emission_prognosis(self, start: Optional[datetime] = None , end: Optional[datetime] = None) -> List[Co2EmissionPoint]:
        pass