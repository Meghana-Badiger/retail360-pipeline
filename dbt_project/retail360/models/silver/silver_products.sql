-- ============================================================
-- silver_products.sql
-- Cleans raw product data and adds margin calculation
-- ============================================================

{{
    config(
        materialized='table',
        schema='silver'
    )
}}

SELECT
    product_id,
    product_name,
    category,
    cost_price,
    sell_price,

    -- Profit margin percentage
    ROUND(
        ((sell_price - cost_price) / sell_price * 100)::numeric,
        2
    )                AS margin_pct,

    -- ingestion metadata
    ingested_at

FROM bronze.raw_products