SELECT
    rate_date,
    base_currency,
    target_currency,
    ROUND(AVG(rate), 4) AS avg_rate,
    ROUND(AVG(inverse_rate), 4) AS avg_inverse_rate
FROM {{ ref('stg_exchange_rates')}}
GROUP BY rate_date, base_currency, target_currency
