"""
Handles the project configuration, including reading the relevant files.
"""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from .structures.enums import StorageMode
from .utilities import read_json, to_path

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any


class Config:
    """Handles the project configuration."""

    CONFIG_FILENAME: str = "config.json"
    SECRETS_FILENAME: str = "secrets.json"
    GOOGLE_CREDENTIALS_FILENAME: str = "gcp-credentials.json"

    CREATED = dt.datetime.now(dt.timezone.utc)

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
