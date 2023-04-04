from datetime import datetime
import psycopg2 as psycopg2
import os
import testing.postgresql


from infrastructure.eletricity_prices import PricePoint
from application.use_cases.get_spot_price_task import PostgresDatabase


def get_database():
    return testing.postgresql.Postgresql(port=7654)


def initailise_database(postgresql):
    with psycopg2.connect(**postgresql.dsn()) as conn:
        with conn.cursor() as cursor:
            file_path = os.path.dirname(__file__)
            init_file_path = os.path.join(file_path, "./../../db/init.sql")
            with open(init_file_path, "r") as f: cursor.execute(f.read())
            conn.commit()


class TestPostgresDatabase:
    def test_insert_prices(self):
        db = PostgresDatabase(host="localhost") # kommentar om det...
        price_points = [PricePoint(datetime(2022, 1, 1), 100.0), PricePoint(datetime(2022, 1, 2), 101.0)]
        db.insert_prices(price_points)
        db.cursor.execute("SELECT COUNT(*) FROM pricepoint")
        result = db.cursor.fetchone()[0]
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
