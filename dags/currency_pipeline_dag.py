import sys
import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# 1. Path hack for Docker: Ensure Airflow can find your 'scripts' folder
sys.path.append('/opt/airflow')

from scripts.CurrencyExtractor import CurrencyExtractor
from scripts.CurrencyLoader import PostgresLoader

logger = logging.getLogger(__name__)


# 2. Wrap your pipeline into a callable function for the PythonOperator
def run_extraction_and_load():
    extractor = CurrencyExtractor("USD")
    raw_data = extractor.fetch_rates()

    if not raw_data:
        # Throwing an error automatically tells Airflow to mark the task as FAILED and retry
        raise ValueError("API returned no data! Triggering Airflow retry.")

    targets = ["CZK", "KZT", "EUR"]
    filtered_rates = extractor.filter_target_currencies(raw_data, targets)
    logger.info(f"Extracted Rates: {filtered_rates}")

    loader = PostgresLoader()
    loader.create_table()
    loader.upsert_rates('USD', filtered_rates)
    logger.info("Postgres load complete.")


# 3. Define the DAG scheduling and retry logic
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2026, 6, 17),  # Set to yesterday so it triggers immediately upon unpausing
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
        'daily_currency_marts_pipeline',
        default_args=default_args,
        description='End-to-end ELT pipeline generating currency data marts',
        schedule_interval='@daily',
        catchup=False
) as dag:
    # TASK 1: Run the custom Python pipeline
    extract_load_task = PythonOperator(
        task_id='extract_and_load_postgres',
        python_callable=run_extraction_and_load
    )

    # TASK 2: Run dbt models (Staging -> Marts)
    # Assumes your dbt_project.yml is located in the root of your mapped Docker volume
    dbt_run_task = BashOperator(
        task_id='dbt_run_marts',
        bash_command='cd /opt/airflow/currency_project && dbt run'
    )

    dbt_test_task = BashOperator(
        task_id='dbt_test_marts',
        bash_command='cd /opt/airflow/currency_project && dbt test'
    )

    # 4. Define the execution order
    extract_load_task >> dbt_run_task >> dbt_test_task