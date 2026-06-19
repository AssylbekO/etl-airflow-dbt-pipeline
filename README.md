# Currency Exchange Rate Pipeline

An end-to-end ELT pipeline that automatically extracts daily currency exchange rates, loads them into PostgreSQL, and transforms them into analytics-ready data marts using dbt — all orchestrated by Apache Airflow running in Docker.

---

## Architecture

```
exchangerate-api.com
       ↓
CurrencyExtractor (Python)           ← Fetches USD → CZK, KZT, EUR rates
       ↓
raw_exchange_rates (PostgreSQL)      ← Raw load, upserted daily
       ↓
stg_exchange_rates (dbt view)        ← Cleaned, renamed, inverse_rate calculated
       ↓
mart_daily_avg_rates (dbt table)     ← Aggregated daily averages per currency pair
       ↓
mart_currency_comparison (dbt table) ← Pivoted: one row per date, one column per currency
       ↓
Apache Airflow DAG                   ← Schedules and orchestrates everything daily
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Infrastructure | Docker, Docker Compose |
| Database | PostgreSQL 15 |
| Orchestration | Apache Airflow 2.8 |
| Transformation | dbt 1.8 (dbt-postgres) |
| Language | Python 3.8 |
| Data Source | exchangerate-api.com |

---

## Project Structure

```
PythonProject/
├── dags/
│   └── currency_pipeline_dag.py   # Airflow DAG: extract → load → dbt run → dbt test
├── scripts/
│   ├── CurrencyExtractor.py       # API extraction logic
│   └── CurrencyLoader.py          # PostgreSQL upsert logic
├── currency_project/              # dbt project
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_exchange_rates.sql
│   │   │   └── schema.yml
│   │   ├── marts/
│   │   │   ├── mart_daily_avg_rates.sql
│   │   │   ├── mart_currency_comparison.sql
│   │   │   └── schema.yml
│   │   └── sources.yml
│   └── dbt_project.yml
└── docker-compose.yml
```

---

## Pipeline DAG

The Airflow DAG runs on a `@daily` schedule with the following task order:

```
extract_and_load_postgres → dbt_run_marts → dbt_test_marts
```

- **extract_and_load_postgres** — calls the exchange rate API, filters target currencies, upserts into PostgreSQL
- **dbt_run_marts** — builds all three dbt models in dependency order
- **dbt_test_marts** — runs 20 data quality tests across all models

---

## dbt Models

### `stg_exchange_rates` (view)
- Source: `raw_exchange_rates`
- Renames `extraction_date` → `rate_date`
- Adds `inverse_rate` column: `ROUND(1.0 / rate, 4)`

### `mart_daily_avg_rates` (table)
- Groups by `rate_date`, `base_currency`, `target_currency`
- Computes `avg_rate` and `avg_inverse_rate`

### `mart_currency_comparison` (table)
- Pivots currency pairs into columns using conditional aggregation
- One row per date with `czk_rate`, `kzt_rate`, `eur_rate` and their inverses

---

## Data Quality

20 dbt tests across all models covering:
- `not_null` on all columns
- `accepted_values` for `base_currency` (USD) and `target_currency` (CZK, KZT, EUR)
- `unique` on `rate_date` in the comparison mart

---

## Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.8+
- dbt-postgres

### Run locally

```bash
# Start containers
docker-compose up -d

# Trigger pipeline manually via Airflow UI
http://localhost:8080
```

### Run dbt manually

```bash
cd currency_project
dbt run
dbt test
dbt docs serve --port 8081
```

---

## Environment Variables

Create a `.env` file in the project root:

```
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
EXCHANGE_RATE_API_KEY=your_api_key_here
```
