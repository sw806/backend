from json import load, dump
from datetime import datetime
from typing import List
from infrastructure.eds_requests import EdsRequests
from infrastructure.eds_requests import PricePoint
from os import path

class GetSpotPricesRequest:
    start_time: datetime

    def __init__(self, start_time: datetime):
        self.start_time = start_time

class GetSpotPricesResponse:
    def __init__(self, price_points: List[PricePoint]):
        self.price_points = price_points

class GetSpotPricesUseCase:
    def __init__(self) -> None:
        pass

    def do(self, request: GetSpotPricesRequest) -> GetSpotPricesResponse:
        file_path = path.join(path.dirname(__file__), "spot_prices.json")

        if not path.isfile(file_path):
            price_points = EdsRequests().get_prices(request.start_time)
            with open(file_path, "w") as file:
                dump([price_point.to_dict() for price_point in price_points], file)
        else:
            with open(file_path, "r") as file:
                lines = load(file)
                price_points = []
                for line in lines:
                    price_points.append(PricePoint(datetime.fromisoformat(line["time"]), line["price"]))
                if price_points[0].time.day <= request.start_time.day and datetime.now().hour > 15:
                    price_points = EdsRequests().get_prices(request.start_time)
                    with open(file_path, "w") as file:
                        dump(price_points, file)

        return GetSpotPricesResponse(price_points)
