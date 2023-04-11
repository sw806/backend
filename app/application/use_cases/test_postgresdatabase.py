from datetime import datetime
from typing import List
import psycopg2 as psycopg2
from psycopg2.errors import UniqueViolation
import pytest
from infrastructure.eletricity_prices import PricePoint
from application.use_cases.get_spot_price_task import PostgresDatabase

class TestPostgresDatabase:
    def test_insert_prices_success(self):
        # Arrange
        db = PostgresDatabase()

        # Act
        price_points = [PricePoint(datetime(2022, 1, 1), 100.0), PricePoint(datetime(2022, 1, 2), 101.0)]
        db.insert_prices(price_points)
        db.cursor.execute("SELECT COUNT(*) FROM pricepoint")
        pre_result = db.cursor.fetchone()
        if pre_result is None:
            assert False
        result = pre_result[0]
        db.cursor.execute("TRUNCATE TABLE pricepoint")
        db.conn.commit()

        # Assert
        assert result == 2

    def test_get_prices_success(self):
        # Arrange
        db = PostgresDatabase()
        price_points = [PricePoint(datetime(2022, 1, 1), 100.0), PricePoint(datetime(2022, 1, 2), 101.0)]
        db.insert_prices(price_points)

        # Act
        start_time = datetime(2022, 1, 1)
        result = db.get_prices(start_time)
        db.cursor.execute("TRUNCATE TABLE pricepoint")
        db.conn.commit()

        # Assert
        assert len(result) == 2
        assert result[0].price == 101.0
        assert result[1].price == 100.0

    def test_get_prices_failure(self):
        # Arrange
        db = PostgresDatabase()
        price_points = [PricePoint(datetime(2022, 1, 1), 100.0), PricePoint(datetime(2022, 1, 2), 101.0)]
        db.insert_prices(price_points)

        # Act
        start_time = datetime(2022, 1, 3)
        result = db.get_prices(start_time)
        db.cursor.execute("TRUNCATE TABLE pricepoint")
        db.conn.commit()

        # Assert
        assert len(result) == 0

    def test_insert_prices_empty_input(self):
        # Arrange
        db = PostgresDatabase()

        # Act
        price_points: List[PricePoint] = []
        db.insert_prices(price_points)
        db.cursor.execute("SELECT COUNT(*) FROM pricepoint")
        pre_result = db.cursor.fetchone()
        if pre_result is None:
            assert False
        result = pre_result[0]
        db.cursor.execute("TRUNCATE TABLE pricepoint")
        db.conn.commit()

        # Assert
        assert result == 0

    def test_get_prices_empty_db(self):
        # Arrange
        db = PostgresDatabase()

        # Act
        start_time = datetime(2022, 1, 1)
        result = db.get_prices(start_time)
        db.cursor.execute("TRUNCATE TABLE pricepoint")
        db.conn.commit()

        # Assert
        assert len(result) == 0


    def test_insert_prices_duplicate_entries(self):
        # Arrange
        db = PostgresDatabase()

        # Act
        price_point = PricePoint(datetime(2022, 1, 1), 100.0)
        db.insert_prices([price_point])

        # Assert
        db.cursor.execute("SELECT COUNT(*) FROM pricepoint")
        result = db.cursor.fetchone()[0]
        assert result == 1

        # Try to insert another point with the same time
        try:
            db.insert_prices([price_point])
        except psycopg2.errors.UniqueViolation as e:
            print("UniqueViolation")
            db.conn.rollback()  # Rollback the transaction to the previous valid state

        db.cursor.execute("SELECT COUNT(*) FROM pricepoint")
        result = db.cursor.fetchone()[0]
        assert result == 1

        # Cleanup
        db.cursor.execute("TRUNCATE TABLE pricepoint")
        db.conn.commit()
