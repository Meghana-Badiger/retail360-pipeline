"""
spark_ingest.py
───────────────
PySpark job: reads CSV files from /data folder and loads
them into the Bronze schema in our Postgres data warehouse.

This is the ingestion layer — Bronze = raw data, no transformations.

Run: python ingestion/spark_ingest.py
"""

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp

# ── Config ────────────────────────────────────────────────────
# These match what we set in docker-compose.yml
PG_HOST     = os.getenv("PG_HOST",     "localhost")
PG_PORT     = os.getenv("PG_PORT",     "5432")
PG_DB       = os.getenv("PG_DB",       "retail_dw")
PG_USER     = os.getenv("PG_USER",     "retail")
PG_PASSWORD = os.getenv("PG_PASSWORD", "retail123")
DATA_DIR    = os.getenv("DATA_DIR",    "data")

# JDBC = Java Database Connectivity — how Spark talks to Postgres
JDBC_URL = f"jdbc:postgresql://{PG_HOST}:{PG_PORT}/{PG_DB}"
JDBC_PROPS = {
    "user":     PG_USER,
    "password": PG_PASSWORD,
    "driver":   "org.postgresql.Driver",  # Postgres JDBC driver
}


# ── Create Spark Session ──────────────────────────────────────
def get_spark() -> SparkSession:
    """
    SparkSession = the entry point to everything Spark.
    Think of it like a database connection but for Spark.
    """
    return (
        SparkSession.builder
        .appName("Retail360_Bronze_Ingestion")   # name shows in Spark UI
        .config(
            # This downloads the Postgres JDBC driver automatically
            "spark.jars.packages",
            "org.postgresql:postgresql:42.7.1",
        )
        .getOrCreate()
    )


# ── Ingest one table ──────────────────────────────────────────
def ingest_table(
    spark: SparkSession,
    filename: str,    # e.g. "customers.csv"
    table: str        # e.g. "bronze.raw_customers"
) -> None:
    """
    Reads a CSV file into a Spark DataFrame,
    adds an ingested_at timestamp,
    then writes it to Postgres Bronze layer.
    """
    path = f"{DATA_DIR}/{filename}"
    print(f"\n📥 Reading {path}...")

    # Read CSV into a Spark DataFrame
    df = (
        spark.read
        .option("header", "true")        # first row is column names
        .option("inferSchema", "true")   # auto-detect data types
        .csv(path)
    )

    # Add ingested_at column = when this data was loaded
    df = df.withColumn("ingested_at", current_timestamp())

    print(f"   Rows: {df.count()}")
    print(f"   Columns: {df.columns}")

    # Write to Postgres
    # mode="append" = add rows, don't overwrite existing data
    (
        df.write
        .jdbc(
            url=JDBC_URL,
            table=table,
            mode="append",
            properties=JDBC_PROPS,
        )
    )
    print(f"   ✅ Loaded into {table}")


# ── Main ──────────────────────────────────────────────────────
def main():
    spark = get_spark()
    spark.sparkContext.setLogLevel("WARN")  # reduce noisy logs

    ingest_table(spark, "customers.csv", "bronze.raw_customers")
    ingest_table(spark, "products.csv",  "bronze.raw_products")
    ingest_table(spark, "orders.csv",    "bronze.raw_orders")

    spark.stop()
    print("\n🎉 Bronze ingestion complete!")


if __name__ == "__main__":
    main()