from datetime import datetime
from typing import List, Dict

from app.infrastructure.eletricity_prices import PricePoint
from app.infrastructure.optimal_time_calculator import OptimalTimeCalculator


class TestEdsEndpointBuilder:
    def test_with_just_dataset(self):
        # Arrange
        price_points: List[Dict[datetime, float]] = [
            {datetime(2021, 1, 1, 23): 10.0},
            {datetime(2021, 1, 1, 22): 10.0},
            {datetime(2021, 1, 1, 21): 10.0},
            {datetime(2021, 1, 1, 20): 5.0},
            {datetime(2021, 1, 1, 19): 10.0},
            {datetime(2021, 1, 1, 18): 10.0},
            {datetime(2021, 1, 1, 17): 10.0},
            {datetime(2021, 1, 1, 16): 10.0},
            {datetime(2021, 1, 1, 15): 10.0}
        ]

        # Act

        # Assert
