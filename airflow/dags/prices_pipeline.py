"""
Contains the DAG for the prices pipeline. Extracts data from the relevant APIs,
stores the data in json format in Storage Buckets, and then loads it into
BigQuery.

This DAG is scheduled to run every 4 hours using the CRON format. For more
information on the CRON format, see:
http://www.nncron.ru/help/EN/working/cron-format.htm
"""

import datetime as dt

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

with DAG(
    dag_id="prices",
    description="Ingest price information for OSRS items.",
    schedule=dt.timedelta(hours=2),
    start_date=dt.datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["prices"],
) as dag:
    # Add operator to ingest price data
    t1 = BashOperator(
        task_id="ingest_prices",
        bash_command=(
            "python3 /app/main.py prices cloud "
            "--config /app/cfg --data /app/data"
        ),
    )
    t1.doc_md = "Ingest data from the APIs."

# Define the order of the operators
t1
