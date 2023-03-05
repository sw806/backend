import requests

class EDSFetcher:
    def __init__(self, endpoint: str, file_path: str) -> None:
        self.endpoint = endpoint
        self.file_path = file_path

    def fetch_data(self):
        try:
            response = requests.get(url=self.endpoint)
        except Exception as e:
            print("Error fetching data: ", e)

        result = response.json()
        records = result.get('records', [])
        records = [record for record in records if record['PriceArea'] == 'DK1']
        records = [{k: v for k, v in record.items() if k in ['HourDK', 'SpotPriceDKK']} for record in records]

        try:
            with open(self.file_path, 'w') as f:
                f.write(str(records))
        except Exception as e:
            print("Error writing to file: ", e)

if __name__ == "__main__":
    endpoint = 'https://api.energidataservice.dk/dataset/Elspotprices?limit=50'
    file_path = '/home/dremacs/github/backend/app/infrastructure/data/spot_prices.json'
    EDSFetcher(endpoint, file_path).fetch_data()
