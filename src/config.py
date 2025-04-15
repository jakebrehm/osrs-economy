"""
Handles the project configuration, including reading the relevant files.
"""

from pathlib import Path
from typing import Any

from .utilities import read_json


class Config:
    """Handles the project configuration."""

    CONFIG_FILENAME: str = "config.json"
    SECRETS_FILENAME: str = "secrets.json"
    GOOGLE_CREDENTIALS_FILENAME: str = "gcp-credentials.json"
    DETAILS_FILENAME: str = "details.json"
    PRICES_FILENAME: str = "prices.json"

    def __init__(
        self,
        config_directory: str | Path | None = None,
        data_directory: str | Path | None = None,
    ) -> None:
        """Initializes the configuration object.

        Project configuration is stored in a config.json file. The location of
        this file is assumed to be in the data directory of the project root.

        This path can be overridden by passing a string or Path object; if
        None is passed, the default path is used.
        """

        # Set default config path
        if config_directory is None:
            config_directory = Path("./cfg/")
        # Convert provided path to Path object if necessary
        elif isinstance(config_directory, str):
            config_directory = Path(config_directory)

        # Set default data path
        if data_directory is None:
            data_directory = Path("./data/")
        # Convert provided path to Path object if necessary
        elif isinstance(data_directory, str):
            data_directory = Path(data_directory)

        # Store arguments as instance variables
        self.config_directory: Path = config_directory
        self.data_directory: Path = data_directory

        # Load the config and secrets files
        config = read_json(self.get_config_path())
        secrets = read_json(self.get_secrets_path())
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
        return self._get_path(
            self.config_directory,
            filename if filename is not None else self.CONFIG_FILENAME,
            f"Config file '{filename}' not found.",
            as_string,
            check_exists,
        )

    def get_secrets_path(
        self,
        filename: str | None = None,
        as_string: bool = False,
        check_exists: bool = True,
    ) -> Path | str:
        """Gets the path to the secrets file."""
        return self._get_path(
            self.config_directory,
            filename if filename is not None else self.SECRETS_FILENAME,
            f"Secrets file '{filename}' not found.",
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
        return self._get_path(
            self.data_directory,
            filename,
            f"Data file '{filename}' not found.",
            as_string,
            check_exists,
        )

    @property
    def google_credentials(self) -> str:
        """Gets the path to the Google credentials file."""
        return self.config_directory / self.GOOGLE_CREDENTIALS_FILENAME

    def __getitem__(self, key: str) -> str:
        """Gets a value from the configuration dictionary."""
        return self.config[key]

    def _get_path(
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
