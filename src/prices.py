"""
Generates a JSON file with curent prices for all tradeable items in the game.
"""

import json
import time
from pathlib import Path
from typing import Iterable, Iterator

import requests
from tqdm import tqdm

from .config import Config
from .details import get_item_details_from_json


def as_chunks(sequence: Iterable[int], size: int) -> Iterator[list[str]]:
    """Splits a sequence into chunks of a specified size."""
    return (sequence[pos : pos + size] for pos in range(0, len(sequence), size))


def get_current_prices_for_ids(
    item_ids: list[int | str],
    config: Config | None = None,
) -> dict:
    """Gets the current prices for a list of item IDs.

    Note that the IDs must be in the format "item_id|item_id|...", and that
    there is a limit of 100 IDs per request.
    """

    try:
        response = requests.get(
            url=config.get("endpoints", "weirdgloop"),
            params={"id": "|".join(str(item_id) for item_id in item_ids)},
            headers={"User-Agent": config.get("user_agent")},
            timeout=config.get("timeout"),
        )
    except requests.exceptions.RequestException:
        tqdm.write("Error occurred while fetching item prices.")
        return {}
    return response.json()


def fetch_item_prices(
    item_ids: list[int | str],
    filename: str,
    wait: float = 1.0,
    chunk_size: int = 100,
    config: Config | None = None,
) -> dict:
    """Gets the current prices for all tradeable items."""

    # Create a default config object if none is provided
    if config is None:
        config = Config(Path("./cfg/"))

    # Initialize the progress bar
    tqdm_bar = tqdm(
        total=len(item_ids),
        initial=0,
        desc="Fetching",
        unit="item",
        leave=False,
    )

    # Get current prices for all items in chunks
    all_prices = {}
    for chunk in tqdm(as_chunks(item_ids, size=chunk_size)):
        chunk_prices = get_current_prices_for_ids(chunk, config=config)
        all_prices.update(chunk_prices)
        tqdm_bar.update(len(chunk))
        # Save the price data itermittently
        save_item_prices_to_json(all_prices, filename)
        # Wait to avoid any potential rate limiting
        time.sleep(wait)
    return all_prices


def save_item_prices_to_json(
    data: dict,
    filename: str,
    indent: int = 4,
) -> dict:
    """Saves the item prices to a JSON file and returns the dictionary."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)
    return data


def generate_item_prices(config: Config | None = None) -> None:
    """Generates the item prices file from start to finish."""

    # Create a default config object if none is provided
    if config is None:
        config = Config(Path("./cfg/"))
    details_filename = config.get_data_path(config.DETAILS_FILENAME)
    prices_filename = config.get_data_path(config.PRICES_FILENAME)

    # Fetch the item prices
    details_data = get_item_details_from_json(details_filename)
    item_ids = list(details_data["items"].keys())
    fetch_item_prices(item_ids, prices_filename, config=config)
    tqdm.write("Finished fetching prices.")
