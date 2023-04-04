from typing import List
from application.use_cases.use_Case import UseCase
from infrastructure.eds_requests import EdsRequests
from infrastructure.eds_requests import PricePoint
import psycopg2
from psycopg2 import extras
from datetime import datetime

class PostgresDatabase:
    def __init__(self, host = "db") -> None:
        self.conn = psycopg2.connect(
            host=host,
            port=5432,
            user="postgres",
            password="postgres",
            database="price-info"
        )
        self.cursor = self.conn.cursor()

    def get_prices(self, start_time: datetime) -> List[PricePoint]:
        query = f"SELECT * FROM pricepoint WHERE _time >= '{start_time.isoformat()}' ORDER BY _time DESC"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [PricePoint(datetime.fromisoformat(str(row[1])), float(row[2])) for row in rows]

    def insert_prices(self, price_points: List[PricePoint]) -> None:
        query = "INSERT INTO pricepoint (_time, _price) VALUES %s"
        values = [(price_point.time.isoformat(), price_point.price) for price_point in price_points]
        extras.execute_values(self.cursor, query, values)
        self.conn.commit()

class GetSpotPricesRequest:
    start_time: datetime

    def __init__(self, start_time: datetime):
        self.start_time = start_time

class GetSpotPricesResponse:
    def __init__(self, price_points: List[PricePoint]):
        self.price_points = price_points

class GetSpotPricesUseCase(UseCase[GetSpotPricesRequest, GetSpotPricesResponse]):
    def __init__(self) -> None:
        self.db = PostgresDatabase()

    def do(self, request: GetSpotPricesRequest) -> GetSpotPricesResponse:
        price_points = self.db.get_prices(request.start_time)

        if len(price_points) == 0 or (price_points[0].time.day <= request.start_time.day and datetime.now().hour > 15):
            price_points = EdsRequests().get_prices(request.start_time)
            self.db.insert_prices(price_points)

        return GetSpotPricesResponse(price_points)




# if __name__ == "__main__":
#     result = GetSpotPricesUseCase().do(GetSpotPricesRequest(datetime.now()))
#     for item in result.price_points:
#         print(item.time, item.price)
#
#     print("Done")

#
# class GetSpotPricesUseCase:
#     def __init__(self) -> None:
#         pass
#
#     def do(self, request: GetSpotPricesRequest) -> GetSpotPricesResponse:
#         file_path = path.join(path.dirname(__file__), "spot_prices.json")
#
#         if not path.isfile(file_path):
#             price_points = EdsRequests().get_prices(request.start_time)
#             with open(file_path, "w") as file:
#                 dump([price_point.to_dict() for price_point in price_points], file)
#         else:
#             with open(file_path, "r") as file:
#                 lines = load(file)
#                 price_points = []
#                 for line in lines:
#                     price_points.append(PricePoint(datetime.fromisoformat(line["time"]), line["price"]))
#                 if price_points[0].time.day <= request.start_time.day and datetime.now().hour > 15:
#                     price_points = EdsRequests().get_prices(request.start_time)
#                     with open(file_path, "w") as file:
#                         dump(price_points, file)
#
#         return GetSpotPricesResponse(price_points)


