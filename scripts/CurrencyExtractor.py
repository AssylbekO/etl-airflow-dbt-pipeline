import requests
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class CurrencyExtractor:
    def __init__(self, base_currency="USD"):
        self.base_currency = base_currency
        self.base_url = "https://api.exchangerate-api.com/v4/latest/"

    def fetch_rates(self):
        try:
            url = f"{self.base_url}{self.base_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.info(f"Request failed: {e}")
            return None

    def filter_target_currencies(self, raw_data, targets):
        if not raw_data:
            return {}

        rates = raw_data.get("rates", {})
        return {c: rates.get(c) for c in targets if c in rates}


    if __name__ == "__main__":
        extractor = CurrencyExtractor("USD")
        raw_data = extractor.fetch_rates()
        if raw_data:
            targets = ["CZK", "KZT", "EUR"]

        result = extractor.filter_target_currencies(data, targets)

        logger.info(result)