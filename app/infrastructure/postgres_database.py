from typing import List, Optional
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

    def get_prices(self, start_time: datetime, ascending: bool = False) -> List[PricePoint]:
        query = f"SELECT * FROM pricepoint WHERE _time >= '{start_time.isoformat()}'"
        if ascending:
            query += " ORDER BY _time ASC"
        else: query += " ORDER BY _time DESC"

        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        price_points: List[PricePoint] = [PricePoint(datetime.fromisoformat(str(row[0])), float(row[1])) for row in rows]

        return price_points

    def get_latest_price_point(self) -> Optional[PricePoint]:
        query = "SELECT * FROM pricepoint ORDER BY _time DESC LIMIT 1"
        self.cursor.execute(query)
        row = self.cursor.fetchone()

        if row is None:
            return None
        return PricePoint(datetime.fromisoformat(str(row[0])), float(row[1]))

    def get_earliest_price_point(self) -> Optional[PricePoint]:
        query = "SELECT * FROM pricepoint ORDER BY _time ASC LIMIT 1"
        self.cursor.execute(query)
        row = self.cursor.fetchone()

        if row is None:
            return None
        return PricePoint(datetime.fromisoformat(str(row[0])), float(row[1]))

    def insert_prices(self, price_points: List[PricePoint]) -> None:
        query = "INSERT INTO pricepoint (_time, _price) VALUES %s ON CONFLICT DO NOTHING"
        values = [(price_point.time.isoformat(), price_point.price) for price_point in price_points]
        extras.execute_values(self.cursor, query, values)
        self.conn.commit()