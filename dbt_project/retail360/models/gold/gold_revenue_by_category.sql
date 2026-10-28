-- ============================================================
-- gold_revenue_by_category.sql
-- Total revenue and orders per product category
-- This is what the dashboard will show
-- ============================================================

{{
    config(
        materialized='table',
        schema='gold'
    )
}}

SELECT
    product_category,

    -- Total revenue per category
    ROUND(SUM(revenue)::numeric, 2)          AS total_revenue,

    -- Total number of orders
    COUNT(order_id)                          AS total_orders,

    -- Average order value
    ROUND(AVG(revenue)::numeric, 2)          AS avg_order_value,

    -- Total units sold
    SUM(quantity)                            AS total_units_sold,

    -- Average margin
    ROUND(AVG(margin)::numeric, 2)           AS avg_margin
FROM {{ ref('silver_orders') }}

GROUP BY product_category
ORDER BY total_revenue DESC