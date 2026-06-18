import psycopg2
import os
from datetime import date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgresLoader:
    def __init__(self):
        self.conn_params = {
            "host": "postgres",
            "port": 5432,
            "dbname": os.getenv("POSTGRES_DB"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD")
        }

    def _get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def create_table(self):
        create_sql = """
        CREATE TABLE IF NOT EXISTS raw_exchange_rates (
            extraction_date DATE,
            base_currency VARCHAR(3),
            target_currency VARCHAR(3),
            rate NUMERIC(10, 4),
            PRIMARY KEY (extraction_date, base_currency, target_currency)
        );
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(create_sql)
            conn.commit()
            print("Table verified/created successfully.")

    def upsert_rates(self, base_currency, rates_dict):
        sql = """
              INSERT INTO raw_exchange_rates
                  (extraction_date, base_currency, target_currency, rate)
              VALUES 
                  (%s, %s, %s, %s) 
              ON CONFLICT (extraction_date, base_currency, target_currency)
              DO UPDATE SET rate = EXCLUDED.rate; 
              """

        extraction_date = date.today()

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                for target_currency, rate in rates_dict.items():
                    cur.execute(sql, (extraction_date, base_currency, target_currency, rate))

            conn.commit()
            logger.info(f"Successfully loaded {len(rates_dict)} rates into the database.")
