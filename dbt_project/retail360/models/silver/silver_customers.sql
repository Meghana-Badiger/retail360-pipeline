-- ============================================================
-- silver_customers.sql
-- Cleans raw customer data and adds derived fields
-- ============================================================

{{
    config(
        materialized='table',
        schema='silver'
    )
}}

SELECT
    customer_id,
    name            AS customer_name,
    email           AS customer_email,
    city,
    country,
    signup_date,

    -- How many days since they signed up
    CURRENT_DATE - signup_date::date   AS days_since_signup,

    -- Metadata
    ingested_at

FROM bronze.raw_customers

-- Remove duplicates — keep the latest record per customer
WHERE customer_id IN (
    SELECT DISTINCT customer_id
    FROM bronze.raw_customers
)