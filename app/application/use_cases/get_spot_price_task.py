from typing import Any, List, Optional, Tuple
from application.use_cases.use_Case import UseCase
from infrastructure.eds_requests import EdsRequests
from infrastructure.eds_requests import PricePoint
import psycopg2
from psycopg2 import extras
from datetime import datetime

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

class PostgresDatabase:
    def __init__(self, host: str="db") -> None:
        with tracer.start_as_current_span("InitPostgresDatabase"):
            self.conn = psycopg2.connect(
                host=host,
                port=5432,
                user="postgres",
                password="postgres",
                database="price-info",
            )
            self.cursor = self.conn.cursor()

    def get_prices(self, start_time: datetime, ascending: bool = False) -> List[PricePoint]:
        with tracer.start_as_current_span("get_prices"):
            rounded_earliest_hour = datetime(
                start_time.year, start_time.month, start_time.day, start_time.hour
            )
            print(f'Rounded earliest hour to getprice points from db: {rounded_earliest_hour}')

            query = f"SELECT * FROM pricepoint WHERE _time >= '{rounded_earliest_hour.isoformat()}'"
            if ascending:
                query += " ORDER BY _time ASC"
            else: query += " ORDER BY _time DESC"

            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            price_points: List[PricePoint] = [PricePoint(datetime.fromisoformat(str(row[0])), float(row[1])) for row in rows]

            if len(price_points):
                if ascending:
                    earliest_price_point = price_points[0]
                else:
                    earliest_price_point = price_points[-1]

                print(f'Earliest price point from db: {earliest_price_point.time}: {earliest_price_point.price}')

            return price_points

    def get_last_price_point(self) -> Optional[PricePoint]:
        with tracer.start_as_current_span("get_last_price_point"):
            query = "SELECT * FROM pricepoint ORDER BY _time DESC LIMIT 1"
            self.cursor.execute(query)
            row = self.cursor.fetchone()

            if row is None:
                return None
            return PricePoint(datetime.fromisoformat(str(row[0])), float(row[1]))

    def insert_prices(self, price_points: List[PricePoint]) -> None:
        with tracer.start_as_current_span("insert_prices"):
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
        with tracer.start_as_current_span("InitGetSpotPricesUseCase"):
            self.db = PostgresDatabase()

    def do(self, request: GetSpotPricesRequest) -> GetSpotPricesResponse:
        price_points = self.db.get_prices(request.start_time, request.ascending)
        last_price_point = self.db.get_last_price_point()

        if len(price_points) == 0 or last_price_point is None or (last_price_point.time.day <= request.start_time.day and datetime.now().hour > 13):
            print(f'EDS request price points from {request.start_time}')
            price_points = EdsRequests().get_prices(request.start_time)
            self.db.insert_prices(price_points)

        print(f'price_points: {len(price_points)}')
        for price_point in price_points:
            print(f'{price_point.time}: {price_point.price}')

        return GetSpotPricesResponse(price_points)
