SELECT
    extraction_date AS rate_date,
    base_currency,
    target_currency,
    rate,
    ROUND(1.0 / rate, 4) AS inverse_rate
FROM {{ source('public', 'raw_exchange_rates') }}