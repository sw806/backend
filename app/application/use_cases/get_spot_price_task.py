from typing import List
from application.use_cases.use_Case import UseCase
from infrastructure.eds_requests import EdsRequests
from infrastructure.eds_requests import PricePoint
from datetime import datetime, timedelta, timezone
from infrastructure.postgres_database import PostgresDatabase
from pydantic.dataclasses import dataclass

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

@dataclass
class GetSpotPricesRequest:
    start_time: datetime
    ascending: bool

    def __init__(self, start_time: datetime, ascending: bool = False):
        self.start_time = start_time
        self.ascending = ascending

@dataclass
class GetSpotPricesResponse:
    price_points: List[PricePoint]
    latest_available_spot_price: datetime

    def __init__(
        self,
        price_points: List[PricePoint],
        latest_available_spot_price: datetime
    ):
        self.price_points = price_points
        self.latest_available_spot_price = latest_available_spot_price

class GetSpotPricesUseCase(UseCase[GetSpotPricesRequest, GetSpotPricesResponse]):
    def __init__(self) -> None:
        with tracer.start_as_current_span("InitGetSpotPricesUseCase"):
            super().__init__()
            self.db = PostgresDatabase()

    def do(self, request: GetSpotPricesRequest) -> GetSpotPricesResponse:
        latest_price_point = self.db.get_latest_price_point()
        latest_price_point_time = None if latest_price_point is None else latest_price_point.time + timedelta(hours=1)
        earliest_price_point = self.db.get_earliest_price_point()
        earliest_price_point_time = None if earliest_price_point is None else earliest_price_point.time

        # Spot prices updates everyday at 13.00 danish time or 11.00 utc.
        latest_available_spot_price = datetime.utcnow()
        latest_available_spot_price = latest_available_spot_price.replace(tzinfo=timezone.utc)
        if latest_available_spot_price.hour > 11:
            # The spot prices have already been released so the next release is tomorrow.
            latest_available_spot_price = latest_available_spot_price.replace(
                day=latest_available_spot_price.day + 1,
                hour=21, # It is not 23 because we work with utc
                minute=0,
                second=0
            )
        else:
            # The spot prices have NOT been released yet.
            latest_available_spot_price = latest_available_spot_price.replace(
                day=latest_available_spot_price.day,
                hour=22,
                minute=0,
                second=0
            )

        print(f'Get spot prices with latest {latest_available_spot_price} for {request.start_time}')

        # Case 0: The spot prices we are asking for have not been released yet.
        if request.start_time > latest_available_spot_price:
            raise Exception("Requesting spot prices exceeeding elspot prices")

        # Case 1: The requested time is earlier than what we have.
        elif earliest_price_point_time is not None and request.start_time < earliest_price_point_time:
            print(f'Requested prices earlier than stored: {request.start_time} -> {earliest_price_point_time}')
            price_points = EdsRequests().get_prices(request.start_time, earliest_price_point_time)
            self.db.insert_prices(price_points)

        # Case 2: The requested time is later than what we have
        elif latest_price_point_time is not None and request.start_time > latest_price_point_time:
            print(f'Requested prices later than stored: {request.start_time} -> {latest_price_point_time}')
            price_points = EdsRequests().get_prices(latest_price_point_time)
            self.db.insert_prices(price_points)

        # Case 3: We have no price points yet.
        elif latest_price_point is None and earliest_price_point is None:
            print(f'Initial spot price EDS request')
            price_points = EdsRequests().get_prices(request.start_time)
            self.db.insert_prices(price_points)

        # Case 4: Latest price point is earlier than avaialble point.
        elif latest_price_point_time is not None and latest_price_point_time < latest_available_spot_price:
            print(f'Latest price point is earlier than avaialble point')
            price_points = EdsRequests().get_prices(latest_price_point_time)
            self.db.insert_prices(price_points)

        price_points = self.db.get_prices(request.start_time, request.ascending)
        print(f'Found {len(price_points)} price points after {request.start_time}')
        return GetSpotPricesResponse(
            price_points, latest_available_spot_price
        )
