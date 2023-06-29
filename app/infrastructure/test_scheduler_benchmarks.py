import time

from datetime import datetime, timedelta
from typing import List

from infrastructure.must_end_between_validator import MustEndBetweenValidator
from infrastructure.must_start_between_validator import MustStartBetweenValidator
from infrastructure.datetime_interval import DatetimeInterval
from infrastructure.schedule import Schedule
from infrastructure.schedule_task import ScheduledTask
from infrastructure.task import Task
from infrastructure.power_usage_function import PowerUsageFunction
from domain import PricePoint
from infrastructure.spot_price_function import SpotPriceFunction

def test_benchmark_1(benchmark):
    benchmark(time.sleep, 0.000001)
    # Arrange
    # Act
    # Assert
    pass