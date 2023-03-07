import requests
from typing import List
from eletricity_prices import ElectricityPrices, PricePoint


class EDSFetcher(ElectricityPrices):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def get_prices(self, start_time=None, end_time=None) -> List[PricePoint]: # start_time and end_time not used in MVP
        try:
            response = requests.get(url=self.endpoint)
        except Exception as e:
            print("Error fetching data: ", e)

        # We are only interested in the records that are in the DK1 price area
        result =  response.json()
        records = result.get('records', [])
        records = [record for record in records if record['PriceArea'] == 'DK1']
        records = [{k: v for k, v in record.items() if k in ['HourDK', 'SpotPriceDKK']} for record in records]

        # For each record in records, create a PricePoint object and add it to the list
        price_points = []
        for record in records:
            price_point = PricePoint()
            price_point.time = record['HourDK']
            price_point.price = record['SpotPriceDKK']
            price_points.append(price_point)

        rev_price_points = price_points[::-1]
        return rev_price_points


if __name__ == "__main__":
    endpoint = 'https://api.energidataservice.dk/dataset/Elspotprices?limit=50'
    price_points = EDSFetcher(endpoint).get_prices()
