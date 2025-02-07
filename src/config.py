"""
Handles the project configuration, including reading the relevant files.
"""

import json
from pathlib import Path
from typing import Any


class Config:
    """Handles the project configuration."""

    CONFIG_FILENAME: str = "config.json"
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

        # Load the config file
        with open(self.get_config_path(), "r", encoding="utf-8") as f:
            self.config = json.load(f)

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
        if filename is None:
            filename = self.CONFIG_FILENAME
        path = self.config_directory / filename
        if check_exists and not path.exists():
            raise FileNotFoundError(f"Config file '{path}' not found.")
        return path.resolve() if as_string else path

    def get_data_path(
        self,
        filename: str,
        as_string: bool = False,
        check_exists: bool = False,
    ) -> Path | str:
        """Gets the path to a data file."""
        path = self.data_directory / filename
        if check_exists and not path.exists():
            raise FileNotFoundError(f"Data file '{path}' not found.")
        return path.resolve() if as_string else path

    def __getitem__(self, key: str) -> str:
        """Gets a value from the configuration dictionary."""
        return self.config[key]
