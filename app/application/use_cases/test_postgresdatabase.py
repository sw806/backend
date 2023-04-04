from datetime import datetime
import psycopg2 as psycopg2
import os


from infrastructure.eletricity_prices import PricePoint
from application.use_cases.get_spot_price_task import PostgresDatabase


class TestPostgresDatabase:
    def test_insert_prices(self):
        db = PostgresDatabase(host="localhost") # kommentar om det...
        price_points = [PricePoint(datetime(2022, 1, 1), 100.0), PricePoint(datetime(2022, 1, 2), 101.0)]
        db.insert_prices(price_points)
        db.cursor.execute("SELECT COUNT(*) FROM pricepoint")
        pre_result = db.cursor.fetchone()
        if pre_result is None:
            assert False
        result = pre_result[0]
        db.cursor.execute("TRUNCATE TABLE pricepoint")
        db.conn.commit()
        assert result == 2

    # def test_get_prices(self):
    #     db = PostgresDatabase()
    #
    #     # Insert some data
    #     price_points = [PricePoint(datetime(2022, 1, 1), 100.0), PricePoint(datetime(2022, 1, 2), 101.0)]
    #     db.insert_prices(price_points)
    #
    #     # Test get_prices with start_time parameter
    #     start_time = datetime(2022, 1, 1)
    #     result = db.get_prices(start_time)
    #     assert len(result) == 2
    #     assert result[0].time == datetime(2022, 1, 2)
    #     assert result[1].time == datetime(2022, 1, 1)
    #     assert result[0].price == 101.0
    #     assert result[1].price == 100.0
    #
    #     # Test get_prices with start_time parameter that has no data
    #     start_time = datetime(2022, 1, 3)
    #     result = db.get_prices(start_time)
    #     assert len(result) == 0
