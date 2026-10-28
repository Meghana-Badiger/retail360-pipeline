"""
ecommerce_pipeline.py
Airflow DAG: generate raw CSVs → load into Bronze → validate row counts.
Runs daily.
"""

from __future__ import annotations                 # Allows modern type-hint syntax on Python 3.8

import subprocess                                  # Runs other Python scripts as separate processes
from datetime import datetime, timedelta           # Dates for start_date and retry_delay

from airflow import DAG                            # The DAG object = the pipeline definition
from airflow.operators.python import PythonOperator            # Task type that runs a Python function
from airflow.providers.postgres.hooks.postgres import PostgresHook   # Ready-made Postgres connector

# Settings applied to every task in this DAG
DEFAULT_ARGS = {
    "owner": "meghana",                            # Shown in the UI
    "depends_on_past": False,                      # Today's run doesn't wait for yesterday's to succeed
    "email_on_failure": False,                     # No email alerts
    "retries": 1,                                  # Retry a failed task once
    "retry_delay": timedelta(minutes=5),           # Wait 5 min before retrying
}


def run_script(path: str) -> None:
    """Runs a Python script inside the container and fails loudly with the real error."""
    result = subprocess.run(
        ["python", path],                          # Command to run
        capture_output=True,                       # Capture stdout/stderr so we can print them
        text=True,                                 # Return output as str, not bytes
        cwd="/opt/airflow",                        # Working dir → relative "data/" = /opt/airflow/data (mounted)
    )
    print(result.stdout)                           # Normal output → task log
    print(result.stderr)                           # Error output → task log (this was missing before)
    if result.returncode != 0:                     # 0 = success, anything else = failure
        raise RuntimeError(f"{path} failed with exit code {result.returncode}")


# Task 1: create fresh CSVs
def generate_data(**kwargs):
    run_script("/opt/airflow/ingestion/generate_data.py")


# Task 2: load CSVs into bronze schema
def spark_ingest(**kwargs):
    run_script("/opt/airflow/ingestion/spark_ingest.py")


# Task 3: quality gate — fail if any Bronze table is empty
def validate_counts(**kwargs):
    hook = PostgresHook(postgres_conn_id="postgres_retail")   # Uses the connection saved in Airflow UI
    tables = ["bronze.raw_customers", "bronze.raw_products", "bronze.raw_orders"]

    empty = []
    for table in tables:
        count = hook.get_first(f"SELECT COUNT(*) FROM {table}")[0]   # First row, first column
        print(f"{table}: {count} rows")
        if count == 0:
            empty.append(table)

    if empty:
        raise ValueError(f"Empty tables: {empty}")
    print("All Bronze tables have data")


with DAG(
    dag_id="retail360_bronze_pipeline",            # Name shown in Airflow UI
    default_args=DEFAULT_ARGS,
    description="Daily Bronze ingestion: generate → ingest → validate",
    schedule_interval="@daily",                    # Every day at 00:00 UTC
    start_date=datetime(2024, 1, 1),               # Earliest date the DAG is valid from
    catchup=False,                                 # Don't backfill runs since 2024
    tags=["retail360", "bronze", "ingestion"],
) as dag:

    t1 = PythonOperator(task_id="generate_raw_data", python_callable=generate_data)
    t2 = PythonOperator(task_id="spark_ingest_bronze", python_callable=spark_ingest)
    t3 = PythonOperator(task_id="validate_row_counts", python_callable=validate_counts)

    t1 >> t2 >> t3                                 # Run order: t1, then t2, then t3