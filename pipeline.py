from scripts.CurrencyExtractor import CurrencyExtractor
from scripts.CurrencyLoader import PostgresLoader
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    extractor = CurrencyExtractor("USD")
    raw_data = extractor.fetch_rates()
    targets = ["CZK", "KZT", "EUR"]
    filtered_rates = extractor.filter_target_currencies(raw_data, targets)
    logger.info(f"Extracted Rates: {filtered_rates}")

    loader = PostgresLoader()
    loader.create_table()
    loader.upsert_rates('USD', filtered_rates)