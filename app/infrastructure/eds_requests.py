import requests
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from requests import Response
from .eletricity_prices import ElectricityPrices, PricePoint
from .co2_emission_point import Co2EmissionPoint, CO2EmissionsRepository
from .eds_url_builder import EdsUrlBuilder

from opentelemetry import trace
tracer = trace.get_tracer(__name__)

class EdsRequests(ElectricityPrices, CO2EmissionsRepository):
    def __init__(self) -> None:
        pass

    def get_co2_emission_prognosis(self, start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[Co2EmissionPoint]:
        if start is not None:
            start = start.replace(
                minute=0,
                second=0,
                microsecond=0
            )

        # Builds URL for "CO2EmisProg" dataset.
        builder = EdsUrlBuilder("CO2EmisProg") \
            .add_to_filter("PriceArea", "DK1") \
            .set_sort_on_key("Minutes5UTC", False) \

        if not start is None:
            builder.set_start(start)

        if not end is None:
            builder.set_end(end)

        url = builder.build()

        print(f'EDS get emissions url: {url}')

        try:
            response: Response = requests.get(url)
        except Exception as e:
            print("Error fetching data: ", e)
            raise e

        # Get all records (PricePoints) from the request
        result = response.json()
        records: List[Dict[str, Any]] = result.get('records', [])

        return self.create_emission_points_from_json(records)[::-1]

    def create_emission_points_from_json(self, json: List[Dict[str, Any]]) -> List[Co2EmissionPoint]:
        emission_points: List[Co2EmissionPoint] = []
        for record in json:
            try:
                time: datetime = datetime.fromisoformat(record['Minutes5UTC']) \
                    .astimezone(timezone.utc)
            except KeyError as exc:
                raise KeyError("Missing 'Minutes5UTC' in price point record", record) from exc
            except ValueError as exc:
                raise ValueError("'Minutes5UTC' is not iso format", record) from exc

            try:
                emission: float = float(record['CO2Emission'])
            except KeyError as exc:
                raise KeyError("Missing 'CO2Emission' in price point record", record) from exc
            except ValueError as exc:
                raise ValueError("'CO2Emission' is not a floating point number", record) from exc

            emission_point = Co2EmissionPoint(time, emission)
            emission_points.append(emission_point)

        return emission_points


    def get_prices(self, start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[PricePoint]:
        with tracer.start_as_current_span("GetPrices"):
            if start is not None:
                start = start.replace(
                    minute=0,
                    second=0,
                    microsecond=0
                )

            # Builds URL for Eds "Elspotprices" dataset.
            builder = EdsUrlBuilder("Elspotprices") \
                .add_to_filter("PriceArea", "DK1") \
                .set_sort_on_key("HourUTC", False) \

            if not start is None:
                builder.set_start(start)

            if not end is None:
                builder.set_end(end)

            url = builder.build()

            print(f'EDS get prices url: {url}')

            try:
                response: Response = requests.get(url)
            except Exception as e:
                print("Error fetching data: ", e)
                raise e

            # Get all records (PricePoints) from the request
            result =  response.json()
            records: List[Dict[str, Any]] = result.get('records', [])

            return self.create_price_points_from_json(records)[::-1]

    def create_price_points_from_json(self, json: List[Dict[str, Any]]) -> List[PricePoint]:
        with tracer.start_as_current_span("CreatePricePointsFromJson"):
            # For each record in records, create a PricePoint object and add it to the list
            price_points: List[PricePoint] = []
            for record in json:
                try:
                    time: datetime = datetime.fromisoformat(record['HourUTC'])
                    time = time.replace(tzinfo=timezone.utc)
                except KeyError as exc:
                    raise KeyError("Missing 'HourUTC' in price point record", record) from exc
                except ValueError as exc:
                    raise ValueError("'HourUTC' is not iso format", record) from exc

                try:
                    # Convert from DKK per MWh to DKK per KWh
                    asd = float(record['SpotPriceDKK'])
                    price: float = float(record['SpotPriceDKK']) / 1000
                except KeyError as exc:
                    raise KeyError("Missing 'SpotPriceDKK' in price point record", record) from exc
                except ValueError as exc:
                    raise ValueError("'SpotPriceDKK' is not a floating point number", record) from exc

                price_point = PricePoint(time, price)
                price_points.append(price_point)

            return price_points
