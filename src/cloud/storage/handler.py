"""
Contains the StorageHandler and related classes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Self

from ...structures.enums import StorageItem, StorageMode
from ...utilities import read_json, write_json
from .helper import (
    download_json_from_storage,
    get_storage_bucket,
    get_storage_client,
    upload_json_to_storage,
)

if TYPE_CHECKING:
    from types import TracebackType
    from typing import Any, Self

    from google.cloud.storage import Client

from ...config import Config


class StorageHandler(ABC):
    """Handles the project data."""

    @abstractmethod
    def save(self, which: StorageItem, data: Any) -> None:
        """Saves the data to the desired storage location."""
        ...

    @abstractmethod
    def load(self, which: StorageItem) -> Any:
        """Loads the data from the desired storage location."""
        ...

    @abstractmethod
    def __enter__(self) -> Self:
        """Enters the context manager."""
        ...

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exits the context manager."""
        ...

    @classmethod
    def from_config(cls, config: Config) -> Self:
        """Creates a new instance of the StorageHandler class."""
        match config.storage_mode:
            case StorageMode.LOCAL:
                return LocalStorageHandler(config)
            case StorageMode.CLOUD:
                return CloudStorageHandler(config)


class LocalStorageHandler(StorageHandler):
    """Handles the project data for local storage."""

    def __init__(self, config: Config) -> None:
        """Initializes the LocalStorageHandler object."""
        self.config = config

    def save(self, which: StorageItem, data: Any) -> None:
        """Saves the data to the local storage location."""
        destination = self.config.get_data_path(which.filename(self.config))
        write_json(destination, data)

    def load(self, which: StorageItem) -> Any:
        """Loads the data from the local storage location."""
        destination = self.config.get_data_path(which.filename(self.config))
        return read_json(destination)

    def __enter__(self) -> Self:
        """Enters the context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exits the context manager."""
        pass


class CloudStorageHandler(StorageHandler):
    """Handles the project data for cloud storage."""

    def __init__(self, config: Config) -> None:
        """Initializes the CloudStorageHandler object."""
        self.config = config
        self._client: Client | None = None

    def connect(self) -> None:
        """Connects to the cloud storage location."""
        self._client = get_storage_client(self.config.google_credentials)

    def disconnect(self) -> None:
        """Disconnects from the cloud storage location."""
        self._client.close()
        self._client = None

    def save(self, which: StorageItem, data: Any) -> None:
        """Saves the data to the cloud storage location."""
        bucket = get_storage_bucket(self._client, which.bucket(self.config))
        upload_json_to_storage(bucket, data, which.filename(self.config))

    def load(self, which: StorageItem) -> Any:
        """Loads the data from the cloud storage location."""
        bucket = get_storage_bucket(self._client, which.bucket(self.config))
        return download_json_from_storage(bucket, which.filename(self.config))

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
