"""
Handles interactions with Google BigQuery.
"""

from typing import Sequence

import pandas as pd
from google.cloud import bigquery


def get_bigquery_client(credentials: str) -> bigquery.Client:
    """Gets an instance of the BigQuery client.

    The only parameter is the path to the credentials JSON file as a string.
    """
    return bigquery.Client.from_service_account_json(credentials)


def get_bigquery_table(
    client: bigquery.Client,
    table_id: str,
) -> bigquery.Table:
    """Gets the requested BigQuery table."""
    return client.get_table(table_id)


def upload_to_bigquery(
    client: bigquery.Client,
    table_id: str,
    df: pd.DataFrame,
) -> Sequence[Sequence[dict]]:
    """Uploads data to a BigQuery table and returns any errors."""
    table = get_bigquery_table(client, table_id=table_id)
    return client.insert_rows_from_dataframe(table, dataframe=df)


def truncate_bigquery_table(
    client: bigquery.Client,
    table_id: str,
) -> bigquery.QueryJob:
    """Truncates a BigQuery table."""
    return client.query(f"TRUNCATE TABLE {table_id}")
