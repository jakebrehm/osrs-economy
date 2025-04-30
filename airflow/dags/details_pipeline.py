"""
Contains the DAG for the details pipeline. Extracts data from the relevant APIs,
stores the data and images in json format in Storage Buckets, and then loads the
data into BigQuery.
"""

import datetime as dt

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

with DAG(
    dag_id="details",
    description="Ingest price information for OSRS items.",
    schedule=dt.timedelta(hours=1),
    start_date=dt.datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["details"],
) as dag:
    # Add operator to ingest price data
    t1 = BashOperator(
        task_id="ingest_details",
        bash_command=(
            "python3 /app/main.py details cloud "
            "--config /app/cfg --data /app/data"
        ),
    )
    t1.doc_md = "Ingest item details data from the APIs and download icons."

# Define the order of the operators
t1
