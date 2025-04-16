"""
Contains the BigQueryHandler and related classes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.cloud import bigquery

from ...structures.enums import BigQueryItem
from .helper import (
    get_bigquery_client,
    truncate_bigquery_table,
    upload_to_bigquery,
)

if TYPE_CHECKING:
    from types import TracebackType
    from typing import Self

    import pandas as pd
    from google.cloud.bigquery import Client

    from ...config import Config


class BigQueryHandler:
    """Handles the project data."""

    def __init__(self, config: Config) -> None:
        """Initializes the BigQueryHandler object."""
        self.config = config
        self._client: Client | None = None

    def connect(self) -> None:
        """Connects to the cloud storage location."""
        self._client = get_bigquery_client(self.config.google_credentials)

    def disconnect(self) -> None:
        """Disconnects from the cloud storage location."""
        self._client.close()
        self._client = None

    def upload(self, which: BigQueryItem, df: pd.DataFrame) -> None:
        """Uploads the data to the desired table."""
        upload_to_bigquery(self._client, which.table(self.config), df)

    def truncate(self, which: BigQueryItem) -> bigquery.QueryJob:
        """Truncates the data from the desired storage location."""
        return truncate_bigquery_table(self._client, which.table(self.config))

    def __enter__(self) -> Self:
        """Enters the context manager."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exits the context manager."""
        self.disconnect()
