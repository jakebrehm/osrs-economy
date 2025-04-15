"""
The main entry point for the project.
"""

import argparse

from src.config import Config
from src.details import generate_item_details
from src.prices import generate_item_prices
from src.structures.enums import ExecutionMode, StorageMode


def parse_arguments(config: Config) -> None:
    """Parses the command line arguments."""
    parser = argparse.ArgumentParser(description=config["project_name"])
    parser.add_argument(
        "mode",
        nargs="?",
        choices=[mode.name.lower() for mode in ExecutionMode],
        default=ExecutionMode.PRICES.name.lower(),
        help="The mode/script to run.",
    )
    parser.add_argument(
        "storage",
        nargs="?",
        choices=[mode.name.lower() for mode in StorageMode],
        default=StorageMode.LOCAL.name.lower(),
        help="The location to store resulting data.",
    )
    args = parser.parse_args()
    args.mode = ExecutionMode[args.mode.upper()]
    args.storage = StorageMode[args.storage.upper()]
    return args


def main() -> None:
    """The main function."""

    # Create a config object
    config = Config()

    # Parse the command line arguments
    args = parse_arguments(config)

    # Set the storage mode
    config.storage_mode = args.storage

    # Execute the selected function
    match args.mode:
        case ExecutionMode.DETAILS:
            generate_item_details(config=config)
        case ExecutionMode.PRICES:
            generate_item_prices(config=config)


if __name__ == "__main__":
    main()
