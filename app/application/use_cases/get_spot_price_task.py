from typing import List
from application.use_cases.use_Case import UseCase
from infrastructure.eds_requests import EdsRequests
from infrastructure.eds_requests import PricePoint
import psycopg2
from psycopg2 import extras
from datetime import datetime

class PostgresDatabase:
    def __init__(self, host: str="db") -> None:
        self.conn = psycopg2.connect(
            host=host,
            port=5432,
            user="postgres",
            password="postgres",
            database="price-info",
        )
        self.cursor = self.conn.cursor()

    def row_to_price_point(self, row: List[tuple]) -> PricePoint:
        return PricePoint(
            datetime.fromisoformat(str(row[0])),
            float(row[1])
        )

    def price_points_count(self) -> int:
        query = "SELECT COUNT(*) FROM pricepoint"
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        print(row)
        return int(row[0])

    def get_prices(self, start_time: datetime, ascending: bool = False) -> List[PricePoint]:
        query = f"SELECT * FROM pricepoint WHERE _time >= '{start_time.isoformat()}'"
        if ascending:
            query += " ORDER BY _time ASC"
        else: query += " ORDER BY _time DESC"

        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [self.row_to_price_point(row) for row in rows]

    def get_last_price_point(self) -> PricePoint:
        query = "SELECT * FROM pricepoint ORDER BY _time DESC LIMIT 1"
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        return self.row_to_price_point(row)

    def insert_prices(self, price_points: List[PricePoint]) -> None:
        query = "INSERT INTO pricepoint (_time, _price) VALUES %s ON CONFLICT DO NOTHING"
        values = [(price_point.time.isoformat(), price_point.price) for price_point in price_points]
        extras.execute_values(self.cursor, query, values)
        self.conn.commit()

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
        self.db = PostgresDatabase()

    def do(self, request: GetSpotPricesRequest) -> GetSpotPricesResponse:
        price_points = self.db.get_prices(request.start_time, request.ascending)
        last_price_point = self.db.get_last_price_point()

        if len(price_points) == 0 or (last_price_point.time.day <= request.start_time.day and datetime.now().hour > 15):
            price_points = EdsRequests().get_prices(request.start_time)
            self.db.insert_prices(price_points)

        return GetSpotPricesResponse(price_points)
