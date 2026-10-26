-- ============================================================
-- Retail360 Data Warehouse Initialisation
-- Runs automatically when Postgres container starts
-- ============================================================

-- BRONZE: raw data exactly as it arrives, no changes
CREATE SCHEMA IF NOT EXISTS bronze;

-- SILVER: cleaned, typed, deduplicated data
CREATE SCHEMA IF NOT EXISTS silver;

-- GOLD: aggregated, business-ready tables for dashboards
CREATE SCHEMA IF NOT EXISTS gold;

-- ── Bronze Tables (raw ingested data) ────────────────────────

CREATE TABLE IF NOT EXISTS bronze.raw_orders (
    order_id        VARCHAR(50),
    customer_id     VARCHAR(50),
    product_id      VARCHAR(50),
    quantity        INT,
    unit_price      NUMERIC(10,2),
    order_date      TIMESTAMP,
    status          VARCHAR(20),
    ingested_at     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bronze.raw_customers (
    customer_id     VARCHAR(50),
    name            VARCHAR(100),
    email           VARCHAR(100),
    city            VARCHAR(100),
    country         VARCHAR(100),
    signup_date     DATE,
    ingested_at     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bronze.raw_products (
    product_id      VARCHAR(50),
    product_name    VARCHAR(200),
    category        VARCHAR(100),
    cost_price      NUMERIC(10,2),
    sell_price      NUMERIC(10,2),
    ingested_at     TIMESTAMP DEFAULT NOW()
);

-- Grant access
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA bronze TO retail;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA silver TO retail;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA gold TO retail;