from datetime import datetime, timedelta
from random import random
from typing import List

from click import Tuple

from app.infrastructure.eletricity_prices import PricePoint
from app.infrastructure.spot_price_function import SpotPriceFunction
from app.infrastructure.power_usage_function import PowerUsageFunction
from app.infrastructure.power_price_function import PowerPriceFunction


class TestPowerPriceFunction:
    def test_is_in_same_discrete_point(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 2),
            PricePoint(datetime(2021, 1, 1, 17), 3)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
            (timedelta(hours=1), 2),
            (timedelta(hours=2), 3),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        power_price_function = PowerPriceFunction(power_usage_function, spot_price_function)

        # Act
        is_in = power_price_function.is_in_same_discrete_point(
            (datetime(2021, 1, 1, 15), timedelta(hours=0)),
            (datetime(2021, 1, 1, 15), timedelta(hours=0)),
            (datetime(2021, 1, 1, 15), timedelta(hours=random())),
            (datetime(2021, 1, 1, 15), timedelta(hours=1)),
        )

        # Assert
        assert is_in

    def test_integrate_over_the_same_power_point(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 2),
            PricePoint(datetime(2021, 1, 1, 17), 3)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
            (timedelta(hours=1), 1),
            (timedelta(hours=2), 1),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        power_price_function = PowerPriceFunction(power_usage_function, spot_price_function)

        for price_point in price_points:
            for _ in range(1000):
                # Act
                hours: float = random()
                integral = power_price_function.integrate_from_to(
                    price_point.time, timedelta(hours=hours)
                )
                expected = price_point.price * hours

                # Assert
                assert integral - expected < 0.01

    def test_integrate_over_nearly_the_same_power_price_point(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 2),
            PricePoint(datetime(2021, 1, 1, 17), 3)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
            (timedelta(hours=1), 2),
            (timedelta(hours=2), 3),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        power_price_function = PowerPriceFunction(power_usage_function, spot_price_function)

        for idx, end_price_point in enumerate(price_points[1:]):
            # Arrange
            start_price_point = price_points[idx]

            # Act
            integral: float = power_price_function.integrate(
                (start_price_point.time, timedelta(hours=0)),
                (end_price_point.time, timedelta(hours=1))
            )

            # Assert
            assert integral == price_points[idx].price

    def test_integrate_over_multiple_hours(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 2),
            PricePoint(datetime(2021, 1, 1, 17), 3)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
            (timedelta(hours=1), 2),
            (timedelta(hours=2), 3),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        power_price_function = PowerPriceFunction(power_usage_function, spot_price_function)

        # Act
        integral: float = power_price_function.integrate_from_to(
            datetime(2021, 1, 1, 15), timedelta(hours=3)
        )

        # Assert
        assert integral == 14

    def random_property_based_integral(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 1),
            PricePoint(datetime(2021, 1, 1, 17), 1)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 2),
            (timedelta(hours=1), 2),
            (timedelta(hours=2), 2),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        power_price_function = PowerPriceFunction(power_usage_function, spot_price_function)

        for _ in range(1000):
            # Random generation for fuzzing
            duration = random() * 1.5
            start = random()
            offset = int(60 * random())

            # Calculate the expected value (Constant price "2" over time)
            expected = duration * 2

            # Act
            integral = power_price_function.integrate_from_to(
                datetime(2021, 1, 1, 15, minute=offset), timedelta(hours=duration), timedelta(hours=start)
            )

            # Assert
            assert integral - expected < 0.001

    def test_next_discrete_point_with_smaller_power_domain_jumps(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 18), 4)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
            (timedelta(minutes=30), 2),
            (timedelta(hours=1), 4),
            (timedelta(hours=3), 10),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        power_price_function = PowerPriceFunction(power_usage_function, spot_price_function)

        # Act
        initial_start = (datetime(2021, 1, 1, 15), timedelta(minutes=0))
        initial_end = (datetime(2021, 1, 1, 18), timedelta(hours=3))
        next_1 = power_price_function.next_discrete_point_from(initial_start, initial_start, initial_end)
        next_2 = power_price_function.next_discrete_point_from(initial_start, next_1, initial_end)
        next_3 = power_price_function.next_discrete_point_from(initial_start, next_2, initial_end)
        next_4 = power_price_function.next_discrete_point_from(initial_start, next_3, initial_end)
        (next_1_time, next_1_delta) = next_1
        (next_2_time, next_2_delta) = next_2
        (next_3_time, next_3_delta) = next_3
        (next_4_time, next_4_delta) = next_4

        # Assert
        assert next_1_delta == timedelta(minutes=30)
        assert next_1_time == datetime(2021, 1, 1, 15, 30)
        assert next_2_delta == timedelta(hours=1)
        assert next_2_time == datetime(2021, 1, 1, 16)
        assert next_3_delta == timedelta(hours=3)
        assert next_3_time == datetime(2021, 1, 1, 18)
        assert next_4_delta == timedelta(hours=4)
        assert next_4_time == datetime(2021, 1, 1, 19)

    def test_next_discrete_point_with_smaller_spot_price_domain_jumps(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 15, 30), 1),
            PricePoint(datetime(2021, 1, 1, 16, 30), 1),
            PricePoint(datetime(2021, 1, 1, 18), 4)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
            (timedelta(hours=1), 4),
            (timedelta(hours=4), 10),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        power_price_function = PowerPriceFunction(power_usage_function, spot_price_function)

        # Act
        initial_start = (datetime(2021, 1, 1, 15), timedelta(minutes=0))
        initial_end = (datetime(2021, 1, 1, 18), timedelta(hours=4))
        next_1 = power_price_function.next_discrete_point_from(initial_start, initial_start, initial_end)
        next_2 = power_price_function.next_discrete_point_from(initial_start, next_1, initial_end)
        next_3 = power_price_function.next_discrete_point_from(initial_start, next_2, initial_end)
        next_4 = power_price_function.next_discrete_point_from(initial_start, next_3, initial_end)
        next_5 = power_price_function.next_discrete_point_from(initial_start, next_4, initial_end)
        (next_1_time, next_1_delta) = next_1
        (next_2_time, next_2_delta) = next_2
        (next_3_time, next_3_delta) = next_3
        (next_4_time, next_4_delta) = next_4
        (next_5_time, next_5_delta) = next_5

        # Assert
        assert next_1_delta == timedelta(minutes=30)
        assert next_1_time == datetime(2021, 1, 1, 15, 30)
        assert next_2_delta == timedelta(hours=1)
        assert next_2_time == datetime(2021, 1, 1, 16)
        assert next_3_delta == timedelta(hours=1, minutes=30)
        assert next_3_time == datetime(2021, 1, 1, 16, 30)
        assert next_4_delta == timedelta(hours=3)
        assert next_4_time == datetime(2021, 1, 1, 18)
        assert next_5_delta == timedelta(hours=4)
        assert next_5_time == datetime(2021, 1, 1, 19)

    def test_integral_example(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 15, 30), 10),
            PricePoint(datetime(2021, 1, 1, 16, 30), 1),
            PricePoint(datetime(2021, 1, 1, 18), 4)
        ]
        spot_price_function = SpotPriceFunction(price_points, timedelta(hours=2))
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 4),
            (timedelta(hours=1), 1),
            (timedelta(hours=4), 10),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        power_price_function = PowerPriceFunction(power_usage_function, spot_price_function)

        # Formula for sections: (power * Δtime) * price per kWh
        # In SI units: (kW * h) * dkk/kWh = kWh * dkk/kWh
        # Ergo: ∫_(t_0)^(t_f) p(t) dt * c(t)
        #   t_0 and t_f describes the period of time (thereby the difference is Δtime)
        #   p is the power function over time. Where, p(t) is the power consumption at that time.
        #   c is the price in kWh over time. Where, c(t) is the price per kWh at that time.

        # Time: 15:00 - 15:30
        section_1 =  (4 * 0.5) * 1
        # Time: 15:30 - 16:00
        section_2 = (4 * 0.5) * 10
        # Time: 16:00 - 16:30
        section_3 = (1 * 0.5) * 10
        # Time: 16:30 - 18:00
        section_4 =  (1 * 1.5) * 1
        # Time: 18:00 - 19:00
        section_5 =  (1 * 1) * 4
        # Time: 19:00 - 20:00
        section_6 =  (10 * 1) * 4
        section_total = section_1 + section_2 + section_3 + section_4 + section_5 + section_6

        # Act
        integral_1 = power_price_function.integrate(
            (datetime(2021, 1, 1, 15), timedelta(hours=0)),
            (datetime(2021, 1, 1, 15, 30), timedelta(minutes=30)),
        )
        integral_2 = power_price_function.integrate(
            (datetime(2021, 1, 1, 15, 30), timedelta(minutes=30)),
            (datetime(2021, 1, 1, 16), timedelta(hours=1)),
        )
        integral_3 = power_price_function.integrate(
            (datetime(2021, 1, 1, 16), timedelta(hours=1)),
            (datetime(2021, 1, 1, 16, 30), timedelta(hours=1, minutes=30)),
        )
        integral_4 = power_price_function.integrate(
            (datetime(2021, 1, 1, 16, 30), timedelta(hours=1, minutes=30)),
            (datetime(2021, 1, 1, 18), timedelta(hours=3)),
        )
        integral_5 = power_price_function.integrate(
            (datetime(2021, 1, 1, 18), timedelta(hours=3)),
            (datetime(2021, 1, 1, 19), timedelta(hours=4)),
        )
        integral_6 = power_price_function.integrate(
            (datetime(2021, 1, 1, 19), timedelta(hours=4)),
            (datetime(2021, 1, 1, 20), timedelta(hours=5)),
        )
        integral_total = power_price_function.integrate(
            (datetime(2021, 1, 1, 15), timedelta(hours=0)),
            (datetime(2021, 1, 1, 20), timedelta(hours=5)),
        )

        # Assert
        assert integral_1 == section_1
        assert integral_2 == section_2
        assert integral_3 == section_3
        assert integral_4 == section_4
        assert integral_5 == section_5
        assert integral_6 == section_6
        assert integral_total == section_total

    def test_same_intervals(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 2),
            PricePoint(datetime(2021, 1, 1, 17), 3),
            PricePoint(datetime(2021, 1, 1, 18), 4),
            PricePoint(datetime(2021, 1, 1, 19), 5),
            PricePoint(datetime(2021, 1, 1, 20), 6),
            PricePoint(datetime(2021, 1, 1, 21), 7),
            PricePoint(datetime(2021, 1, 1, 22), 8)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
            (timedelta(hours=1), 2),
            (timedelta(hours=2), 3),
            (timedelta(hours=3), 4),
            (timedelta(hours=4), 5),
            (timedelta(hours=5), 6),
            (timedelta(hours=6), 7),
            (timedelta(hours=7), 8)
        ]
        power_usage_function = PowerUsageFunction(power_points)
        power_price_function = PowerPriceFunction(power_usage_function, spot_price_function)
        expected = (1 * 1) + (2 * 2) + (3 * 3) + (4 * 4) + (5 * 5) + (6 * 6) + (7 * 7) + (8 * 8)

        # Act
        integral = power_price_function.integrate(
            (datetime(2021, 1, 1, 15), timedelta(hours=0)),
            (datetime(2021, 1, 1, 23), timedelta(hours=8)),
        )

        # Assert
        assert integral == expected

    def test_next_point_should_not_be_is_same_discrete_point(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 16), 2),
            PricePoint(datetime(2021, 1, 1, 17), 3),
            PricePoint(datetime(2021, 1, 1, 18), 4),
            PricePoint(datetime(2021, 1, 1, 19), 5),
            PricePoint(datetime(2021, 1, 1, 20), 6),
            PricePoint(datetime(2021, 1, 1, 21), 7),
            PricePoint(datetime(2021, 1, 1, 22), 8)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 1),
            (timedelta(hours=1), 2),
            (timedelta(hours=2), 3),
            (timedelta(hours=3), 4),
            (timedelta(hours=4), 5),
            (timedelta(hours=5), 6),
            (timedelta(hours=6), 7),
            (timedelta(hours=7), 8)
        ]
        power_usage_function = PowerUsageFunction(power_points)
        power_price_function = PowerPriceFunction(power_usage_function, spot_price_function)

        # Act
        initial_start = (datetime(2021, 1, 1, 15), timedelta(minutes=0))
        initial_end = (datetime(2021, 1, 1, 22), timedelta(hours=7))
        
        next_1 = power_price_function.next_discrete_point_from(
            initial_start, initial_start, initial_end
        )
        next_2 = power_price_function.next_discrete_point_from(
            initial_start, next_1, initial_end
        )
        next_3 = power_price_function.next_discrete_point_from(
            initial_start, next_2, initial_end
        )
        next_4 = power_price_function.next_discrete_point_from(
            initial_start, next_3, initial_end
        )
        next_5 = power_price_function.next_discrete_point_from(
            initial_start, next_4, initial_end
        )
        next_6 = power_price_function.next_discrete_point_from(
            initial_start, next_5, initial_end
        )
        next_7 = power_price_function.next_discrete_point_from(
            initial_start, next_6, initial_end
        )
        next_8 = power_price_function.next_discrete_point_from(
            initial_start, next_7, initial_end
        )

        # Assert
        assert next_1 == (datetime(2021, 1, 1, 16), timedelta(hours=1))
        assert not power_price_function.is_in_same_discrete_point(
            initial_start, initial_start, next_1, initial_end
        )
        assert next_2 == (datetime(2021, 1, 1, 17), timedelta(hours=2))
        assert not power_price_function.is_in_same_discrete_point(
            initial_start, next_1, next_2, initial_end
        )
        assert next_3 == (datetime(2021, 1, 1, 18), timedelta(hours=3))
        assert not power_price_function.is_in_same_discrete_point(
            initial_start, next_2, next_3, initial_end
        )
        assert next_4 == (datetime(2021, 1, 1, 19), timedelta(hours=4))
        assert not power_price_function.is_in_same_discrete_point(
            initial_start, next_3, next_4, initial_end
        )
        assert next_5 == (datetime(2021, 1, 1, 20), timedelta(hours=5))
        assert not power_price_function.is_in_same_discrete_point(
            initial_start, next_4, next_5, initial_end
        )
        assert next_6 == (datetime(2021, 1, 1, 21), timedelta(hours=6))
        assert not power_price_function.is_in_same_discrete_point(
            initial_start, next_5, next_6, initial_end
        )
        assert next_7 == (datetime(2021, 1, 1, 22), timedelta(hours=7))
        assert not power_price_function.is_in_same_discrete_point(
            initial_start, next_6, next_7, initial_end
        )
        assert next_8 == (datetime(2021, 1, 1, 23), timedelta(hours=8))
        assert not power_price_function.is_in_same_discrete_point(
            initial_start, next_7, next_8, initial_end
        )

    def test_n_version_test_over_integrate_and_integrate_from_to(self):
        # Arrange
        price_points: List[PricePoint] = [
            PricePoint(datetime(2021, 1, 1, 15), 1),
            PricePoint(datetime(2021, 1, 1, 15, 30), 10),
            PricePoint(datetime(2021, 1, 1, 16, 30), 1),
            PricePoint(datetime(2021, 1, 1, 18), 4)
        ]
        spot_price_function = SpotPriceFunction(price_points)
        power_points: List[Tuple[timedelta, float]] = [
            (timedelta(hours=0), 4),
            (timedelta(hours=1), 1),
            (timedelta(hours=4), 10),
        ]
        power_usage_function = PowerUsageFunction(power_points)
        power_price_function = PowerPriceFunction(power_usage_function, spot_price_function)

        # Act
        integral_1_1 = power_price_function.integrate(
            (datetime(2021, 1, 1, 15), timedelta(hours=0)),
            (datetime(2021, 1, 1, 15, 30), timedelta(minutes=30)),
        )
        integral_2_1 = power_price_function.integrate_from_to(
            datetime(2021, 1, 1, 15), timedelta(minutes=30)
        )

        integral_1_2 = power_price_function.integrate(
            (datetime(2021, 1, 1, 15, 30), timedelta(minutes=30)),
            (datetime(2021, 1, 1, 16), timedelta(hours=1)),
        )
        integral_2_2 = power_price_function.integrate_from_to(
            datetime(2021, 1, 1, 15, 30), timedelta(minutes=30), timedelta(minutes=30)
        )

        integral_1_3 = power_price_function.integrate(
            (datetime(2021, 1, 1, 16), timedelta(hours=1)),
            (datetime(2021, 1, 1, 16, 30), timedelta(hours=1, minutes=30)),
        )
        integral_2_3 = power_price_function.integrate_from_to(
            datetime(2021, 1, 1, 16), timedelta(minutes=30), timedelta(hours=1)
        )

        integral_1_4 = power_price_function.integrate(
            (datetime(2021, 1, 1, 16, 30), timedelta(hours=1, minutes=30)),
            (datetime(2021, 1, 1, 19), timedelta(hours=4)),
        )
        integral_2_4 = power_price_function.integrate_from_to(
            datetime(2021, 1, 1, 16, 30), timedelta(hours=2, minutes=30), timedelta(hours=1, minutes=30)
        )

        integral_1_total = power_price_function.integrate(
            (datetime(2021, 1, 1, 15), timedelta(hours=0)),
            (datetime(2021, 1, 1, 19), timedelta(hours=4)),
        )

        integral_2_total = power_price_function.integrate_from_to(
            datetime(2021, 1, 1, 15), timedelta(hours=4)
        )

        # Assert
        assert integral_1_1 == integral_2_1
        assert integral_1_2 == integral_2_2
        assert integral_1_3 == integral_2_3
        assert integral_1_4 == integral_2_4
        assert integral_1_total == integral_2_total