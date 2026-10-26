"""
ecommerce_pipeline.py
─────────────────────
Airflow DAG — orchestrates the full Bronze ingestion pipeline.

Schedule: runs daily at midnight
Tasks:
  1. generate_data   → creates fresh CSV files
  2. spark_ingest    → loads CSVs into Bronze (Postgres)
  3. validate_counts → checks tables aren't empty
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

# ── Default settings for all tasks ───────────────────────────
DEFAULT_ARGS = {
    "owner":            "meghana",       # your name
    "depends_on_past":  False,           # don't wait for yesterday's run
    "email_on_failure": False,
    "retries":          1,               # retry once if a task fails
    "retry_delay":      timedelta(minutes=5),
}


# ── Task 1: Generate Data ─────────────────────────────────────
def generate_data(**kwargs):
    """
    Runs the data generator script.
    Creates fresh CSV files in the /data folder.
    """
    result = subprocess.run(
        ["python", "/opt/airflow/ingestion/generate_data.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    print(result.stdout)


# ── Task 2: Spark Ingestion ───────────────────────────────────
def spark_ingest(**kwargs):
    """
    Runs the PySpark ingestion job.
    Loads CSV files into Bronze schema in Postgres.
    """
    result = subprocess.run(
        ["python", "/opt/airflow/ingestion/spark_ingest.py"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError("Spark ingestion failed! Check logs above.")


# ── Task 3: Validate Row Counts ───────────────────────────────
def validate_counts(**kwargs):
    """
    Quality gate — checks that Bronze tables actually have data.
    Fails the DAG if any table is empty.

    Uses Airflow's PostgresHook to connect to our warehouse.
    """
    # PostgresHook uses the connection we set up in Airflow UI
    hook = PostgresHook(postgres_conn_id="postgres_retail")

    tables = {
        "bronze.raw_customers": "SELECT COUNT(*) FROM bronze.raw_customers",
        "bronze.raw_products":  "SELECT COUNT(*) FROM bronze.raw_products",
        "bronze.raw_orders":    "SELECT COUNT(*) FROM bronze.raw_orders",
    }

    failed = []
    for table, sql in tables.items():
        count = hook.get_first(sql)[0]
        print(f"   {table}: {count} rows")
        if count == 0:
            failed.append(table)

    if failed:
        raise ValueError(f"❌ Empty tables found: {failed}")

    print("✅ All Bronze tables have data!")


# ── DAG Definition ────────────────────────────────────────────
with DAG(
    dag_id="retail360_bronze_pipeline",      # unique name in Airflow UI
    default_args=DEFAULT_ARGS,
    description="Daily Bronze ingestion: generate → ingest → validate",
    schedule_interval="@daily",              # runs every day at midnight
    start_date=datetime(2024, 1, 1),
    catchup=False,                           # don't backfill old runs
    tags=["retail360", "bronze", "ingestion"],
) as dag:

    # ── Define the 3 tasks ────────────────────────────────────
    t1 = PythonOperator(
        task_id="generate_raw_data",
        python_callable=generate_data,
    )

    t2 = PythonOperator(
        task_id="spark_ingest_bronze",
        python_callable=spark_ingest,
    )

    t3 = PythonOperator(
        task_id="validate_row_counts",
        python_callable=validate_counts,
    )

    # ── Set the order: t1 runs first, then t2, then t3 ───────
    t1 >> t2 >> t3