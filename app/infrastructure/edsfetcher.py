import requests
from typing import Any, Dict, List, Optional
from datetime import datetime
from requests import Response
from .eletricity_prices import ElectricityPrices, PricePoint
from .eds_url_builder import EdsUrlBuilder

class EDSFetcher(ElectricityPrices):
    def __init__(self):
        pass

    def get_prices(self, start_time: datetime, end_time: Optional[datetime]) -> List[PricePoint]:
        # Builds URL for Eds "Elspotprices" dataset.
        builder = EdsUrlBuilder("Elspotprices") \
            .set_start(start_time) \
            .add_to_filter("PriceArea", "DK1") \
            .set_sort_on_key("HourDK", True) \

        if not end_time is None:
            builder.set_end(end_time)

        url = builder.build()

        try:
            response: Response = requests.get(url)
        except Exception as e:
            print("Error fetching data: ", e)
            raise e

        # Get all records (PricePoints) from the request
        result =  response.json()
        records: List[Dict[str, Any]] = result.get('records', [])

        return self.create_price_points_from_json(records)

    def create_price_points_from_json(self, json: List[Dict[str, Any]]) -> List[PricePoint]:
        # For each record in records, create a PricePoint object and add it to the list
        price_points: List[PricePoint] = []
        for record in json:
            price_point = PricePoint(
                datetime.fromisoformat(record['HourDK']),
                float(record['SpotPriceDKK'])
            )
            price_points.append(price_point)

        return price_points
