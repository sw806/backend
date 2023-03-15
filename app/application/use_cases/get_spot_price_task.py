import json
import os.path
from datetime import datetime
from typing import List
from infrastructure import EdsRequests
from infrastructure import PricePoint
import os

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
        if not os.path.isfile("spot_prices.json"):
            price_points: List[PricePoint] = EdsRequests().get_prices(request.start_time)
            with open("spot_prices.json", "w") as file:
                json.dump(price_points, file)
        else:
            with open("spot_prices.json", "r") as file:
                lines = json.load(file)
                price_points = []
                for line in lines:
                    price_points.append(PricePoint(datetime.fromisoformat(line["time"]), line["price"]))
                if price_points[0].time.day <=  request.start_time.day and datetime.now().hour > 15:
                    price_points = EdsRequests().get_prices(request.start_time)
                    with open("spot_prices.json", "w") as file:
                        json.dump(price_points, file)

        return GetSpotPricesResponse(price_points)


if __name__ == '__main__':
    GetSpotPricesUseCase().do(GetSpotPricesRequest(datetime.datetime.now()))

    