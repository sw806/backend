from typing import List
from application.use_cases.use_Case import UseCase
from infrastructure.eds_requests import EdsRequests
from infrastructure.eds_requests import PricePoint
from datetime import datetime
from infrastructure.postgres_database import PostgresDatabase

class GetSpotPricesRequest:
    start_time: datetime
    ascending: bool

    def __init__(self, start_time: datetime, ascending: bool = False):
        self.start_time = start_time
        self.ascending = ascending

class GetSpotPricesResponse:
    def __init__(self, price_points: List[PricePoint]):
        self.price_points = price_points

class GetSpotPricesUseCase(UseCase[GetSpotPricesRequest, GetSpotPricesResponse]):
    def __init__(self) -> None:
        super().__init__()
        self.db = PostgresDatabase()

    def do(self, request: GetSpotPricesRequest) -> GetSpotPricesResponse:
        price_points = self.db.get_prices(request.start_time, request.ascending)
        last_price_point = self.db.get_last_price_point()

        if len(price_points) == 0 or last_price_point is None or (last_price_point.time.day <= request.start_time.day and datetime.now().hour > 13):
            print(f'EDS request price points from {request.start_time}')
            price_points = EdsRequests().get_prices(request.start_time)
            self.db.insert_prices(price_points)

        return GetSpotPricesResponse(price_points)
