SELECT
    rate_date,
    MAX(CASE WHEN target_currency = 'CZK' THEN avg_rate END) AS czk_rate,
    MAX(CASE WHEN target_currency = 'KZT' THEN avg_rate END) AS kzt_rate,
    MAX(CASE WHEN target_currency = 'EUR' THEN avg_rate END) AS eur_rate,
    MAX(CASE WHEN target_currency = 'CZK' THEN avg_inverse_rate END) AS czk_inverse_rate,
    MAX(CASE WHEN target_currency = 'KZT' THEN avg_inverse_rate END) AS kzt_inverse_rate,
    MAX(CASE WHEN target_currency = 'EUR' THEN avg_inverse_rate END) AS eur_inverse_rate
FROM {{ ref('mart_daily_avg_rates')}}
GROUP BY rate_date