"""
Handles the project configuration, including reading the relevant files.
"""

from __future__ import annotations

import datetime as dt
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .cloud import (
    download_json_from_storage,
    get_storage_bucket,
    get_storage_client,
    upload_json_to_storage,
)
from .structures.enums import ResultType, StorageMode
from .utilities import read_json, to_path, write_json

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType
    from typing import Any, Self

    from google.cloud.storage import Client


class Config:
    """Handles the project configuration."""

    CONFIG_FILENAME: str = "config.json"
    SECRETS_FILENAME: str = "secrets.json"
    GOOGLE_CREDENTIALS_FILENAME: str = "gcp-credentials.json"

    CREATED = dt.datetime.now(dt.timezone.utc).strftime(r"%Y-%m-%dT%H:%M:%S")

    def __init__(
        self,
        config_directory: str | Path | None = None,
        data_directory: str | Path | None = None,
        storage_mode: StorageMode = StorageMode.LOCAL,
    ) -> None:
        """Initializes the configuration object.

        Unprotected project configuration data is stored in a config.json file,
        while protected data is stored in a secrets.json file. The location of
        this file is assumed to be in the cfg directory of the project root.

        Additionally, the google credentials file is assumed to be stored in the
        cfg directory and is used to authenticate with Google Cloud Storage.

        The config and data directory paths can be overridden by passing a
        string or Path object; if None is passed, default paths are used.

        A storage mode can be passed as well to control the storage location.
        The default is to use local storage, and resulting files will
        automatically be saved to the data directory.
        """

        # Store arguments as instance variables
        self.config_directory: Path = to_path(config_directory, "./cfg/")
        self.data_directory: Path = to_path(data_directory, "./data/")
        self.storage_mode: StorageMode = storage_mode

        # Load the config and secrets files
        self.refresh()

    def refresh(self) -> None:
        """Refreshes the configuration object."""
        config = read_json(self.get_config_path())
        secrets = read_json(self.get_config_path(self.SECRETS_FILENAME))
        self.config = config | secrets

    def get(self, *keys: list[str]) -> Any:
        """Gets a value from the configuration dictionary.

        Multiple keys can be provided to access nested values.
        """

        # Iterate through the keys and get the value
        value = self.config
        for key in keys:
            value = value[key]
        return value

    def get_config_path(
        self,
        filename: str | None = None,
        as_string: bool = False,
        check_exists: bool = True,
    ) -> Path | str:
        """Gets the path to the config file."""
        return self._get_path_with_base(
            self.config_directory,
            filename if filename is not None else self.CONFIG_FILENAME,
            f"Config file '{filename}' not found.",
            as_string,
            check_exists,
        )

    def get_data_path(
        self,
        filename: str,
        as_string: bool = False,
        check_exists: bool = False,
    ) -> Path | str:
        """Gets the path to a data file."""
        return self._get_path_with_base(
            self.data_directory,
            filename,
            f"Data file '{filename}' not found.",
            as_string,
            check_exists,
        )

    @property
    def google_credentials(self) -> str:
        """Gets the path to the Google credentials file."""
        return self.get_config_path(self.GOOGLE_CREDENTIALS_FILENAME)

    def __getitem__(self, key: str) -> str:
        """Gets a value from the configuration dictionary."""
        return self.config[key]

    def _get_path_with_base(
        self,
        base_path: Path,
        filename: str,
        error_message: str,
        as_string: bool = False,
        check_exists: bool = True,
    ) -> Path | str:
        """Gets the path to the config file."""
        path = base_path / filename
        if check_exists and not path.exists():
            raise FileNotFoundError(error_message)
        return path.resolve() if as_string else path


class DataHandler(ABC):
    """Handles the project data."""

    @abstractmethod
    def save(self, which: ResultType, data: Any) -> None:
        """Saves the data to the desired storage location."""
        ...

    @abstractmethod
    def load(self, which: ResultType) -> Any:
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
        """Creates a new instance of the DataHandler class."""
        match config.storage_mode:
            case StorageMode.LOCAL:
                return LocalDataHandler(config)
            case StorageMode.CLOUD:
                return CloudDataHandler(config)


class LocalDataHandler(DataHandler):
    """Handles the project data for local storage."""

    def __init__(self, config: Config) -> None:
        """Initializes the LocalDataHandler object."""
        self.config = config

    def save(self, which: ResultType, data: Any) -> None:
        """Saves the data to the local storage location."""
        destination = self.config.get_data_path(which.filename(self.config))
        write_json(destination, data)

    def load(self, which: ResultType) -> Any:
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


class CloudDataHandler(DataHandler):
    """Handles the project data for cloud storage."""

    def __init__(self, config: Config) -> None:
        """Initializes the CloudDataHandler object."""
        self.config = config
        self._client: Client | None = None

    def connect(self) -> None:
        """Connects to the cloud storage location."""
        self._client = get_storage_client(self.config.google_credentials)

    def disconnect(self) -> None:
        """Disconnects from the cloud storage location."""
        self._client.close()
        self._client = None

    def save(self, which: ResultType, data: Any) -> None:
        """Saves the data to the cloud storage location."""
        bucket = get_storage_bucket(self._client, which.bucket(self.config))
        upload_json_to_storage(bucket, data, which.filename(self.config))

    def load(self, which: ResultType) -> Any:
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
