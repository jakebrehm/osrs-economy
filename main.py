"""
The main entry point for the project.
"""

import argparse

from src.config import Config
from src.details import generate_item_details
from src.prices import generate_item_prices
from src.structures.enums import Mode


def parse_arguments(config: Config) -> None:
    """Parses the command line arguments."""
    parser = argparse.ArgumentParser(description=config["project_name"])
    parser.add_argument(
        "mode",
        nargs="?",
        choices=[mode.name.lower() for mode in Mode],
        default=Mode.PRICES.name.lower(),
        help="The mode/script to run.",
    )
    args = parser.parse_args()
    args.mode = Mode[args.mode.upper()]
    return args


def main() -> None:
    """The main function."""

    # Create a config object
    config = Config()

    # Parse the command line arguments
    args = parse_arguments(config)

    # Execute the selected function
    match args.mode:
        case Mode.DETAILS:
            generate_item_details(config=config)
        case Mode.PRICES:
            generate_item_prices(config=config)


if __name__ == "__main__":
    main()
