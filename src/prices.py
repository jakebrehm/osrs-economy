"""
Generates a JSON file with curent prices for all tradeable items in the game.
"""

import time

import requests
from tqdm import tqdm

from .config import Config, DataHandler
from .details import get_item_details
from .structures.enums import ResultType
from .utilities import as_chunks


def get_current_prices_for_ids(
    item_ids: list[int | str],
    config: Config,
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
    config: Config,
    wait: float = 1.0,
    chunk_size: int = 100,
) -> dict:
    """Gets the current prices for all tradeable items."""

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
        save_item_prices(all_prices, config=config)
        # Wait to avoid any potential rate limiting
        time.sleep(wait)
    tqdm.write("Finished fetching prices.")
    return all_prices


def save_item_prices(data: dict, config: Config) -> dict:
    """Saves the item prices to a JSON file and returns the dictionary."""
    with DataHandler.from_config(config) as handler:
        handler.save(ResultType.PRICES, data)
    return data


def generate_item_prices(config: Config) -> dict:
    """Generates the item prices file from start to finish."""
    details_data = get_item_details(config=config)
    item_ids = list(details_data["items"].keys())
    return fetch_item_prices(item_ids, config=config)
