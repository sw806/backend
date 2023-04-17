import requests
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
from requests import Response
from .eletricity_prices import ElectricityPrices, PricePoint
from .eds_url_builder import EdsUrlBuilder

class EdsRequests(ElectricityPrices):
    def __init__(self) -> None:
        pass

    def get_prices(self, start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[PricePoint]:
        # Builds URL for Eds "Elspotprices" dataset.
        builder = EdsUrlBuilder("Elspotprices") \
            .add_to_filter("PriceArea", "DK1") \
            .set_sort_on_key("HourUTC", False) \

        if not start is None:
            builder.set_start(start)

        if not end is None:
            builder.set_end(end)

        url = builder.build()

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
        # For each record in records, create a PricePoint object and add it to the list
        price_points: List[PricePoint] = []
        for record in json:
            try:
                time: datetime = datetime.fromisoformat(record['HourUTC']) \
                    .astimezone(timezone.utc)
            except KeyError as exc:
                raise KeyError("Missing 'HourUTC' in price point record", record) from exc
            except ValueError as exc:
                raise ValueError("'HourUTC' is not iso format", record) from exc

            try:
                # Convert from DKK per MWh to DKK per KWh
                price: float = float(record['SpotPriceDKK']) / 1000
            except KeyError as exc:
                raise KeyError("Missing 'SpotPriceDKK' in price point record", record) from exc
            except ValueError as exc:
                raise ValueError("'SpotPriceDKK' is not a floating point number", record) from exc

            price_point = PricePoint(time, price)
            price_points.append(price_point)

        return price_points
