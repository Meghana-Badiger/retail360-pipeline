-- ============================================================
-- gold_customer_summary.sql
-- Summary of each customer's purchase behaviour
-- ============================================================

{{
    config(
        materialized='table',
        schema='gold'
    )
}}

SELECT
    customer_id,
    customer_name,
    customer_email,
    customer_city,
    customer_country,

    -- Order metrics
    COUNT(order_id)                           AS total_orders,
    ROUND(SUM(revenue)::numeric, 2)           AS total_spent,
    ROUND(AVG(revenue)::numeric, 2)           AS avg_order_value,

    -- First and last order dates
    MIN(order_date)                           AS first_order_date,
    MAX(order_date)                           AS last_order_date,

    -- Days between first and last order
    MAX(order_date::date) - MIN(order_date::date)  AS customer_lifetime_days

FROM {{ ref('silver_orders') }}

GROUP BY
    customer_id,
    customer_name,
    customer_email,
    customer_city,
    customer_country

ORDER BY total_spent DESC