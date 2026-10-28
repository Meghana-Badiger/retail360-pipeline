-- ============================================================
-- silver_orders.sql
-- Cleans raw orders and enriches with customer + product info
-- ============================================================

{{
    config(
        materialized='table',
        schema='silver'
    )
}}

SELECT
    -- Order details
    o.order_id,
    o.order_date,
    o.quantity,
    o.unit_price,
    o.status,

    -- Calculated field
    ROUND((o.quantity * o.unit_price)::numeric, 2)  AS revenue,

    -- Customer details (joined from raw_customers)
    c.customer_id,
    c.name         AS customer_name,
    c.email        AS customer_email,
    c.city         AS customer_city,
    c.country      AS customer_country,

    -- Product details (joined from raw_products)
    p.product_id,
    p.product_name,
    p.category     AS product_category,
    p.cost_price,
    p.sell_price,

    -- Margin calculation
    ROUND((o.unit_price - p.cost_price)::numeric, 2) AS margin,

    -- Metadata
    o.ingested_at

FROM bronze.raw_orders o

LEFT JOIN bronze.raw_customers c
    ON o.customer_id = c.customer_id

LEFT JOIN bronze.raw_products p
    ON o.product_id = p.product_id

-- Only keep completed and pending orders
WHERE o.status IN ('completed', 'pending')