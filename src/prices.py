"""
Generates a JSON file with curent prices for all tradeable items in the game.
"""

import time
import uuid

import pandas as pd
import requests
from tqdm import tqdm

from .cloud.bigquery.handler import BigQueryHandler
from .cloud.storage.handler import StorageHandler
from .config import Config
from .details import get_item_details
from .structures.enums import BigQueryItem, StorageItem, StorageMode
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
    with StorageHandler.from_config(config) as handler:
        handler.save(StorageItem.PRICES, data)
    return data


def upload_item_prices(data: dict, config: Config) -> None:
    """Uploads the item prices to BigQuery."""
    records = list(data.values())
    df = pd.DataFrame.from_records(records)
    df.columns = ["item_id", "timestamp", "price", "volume"]
    df["uuid"] = df.apply(lambda _: str(uuid.uuid4()), axis=1)
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        format="ISO8601",
        utc=True,
    )
    df["recorded_at"] = config.CREATED
    with BigQueryHandler(config) as handler:
        errors = handler.upload(BigQueryItem.PRICES, df)
        if any(item for item in errors):
            tqdm.write("Errors occurred while handling prices.")
            tqdm.write(errors)


def generate_item_prices(config: Config) -> dict:
    """Generates the item prices file from start to finish."""
    details_data = get_item_details(config=config)
    item_ids = list(details_data["items"].keys())
    result = fetch_item_prices(item_ids, config=config)
    if config.storage_mode == StorageMode.CLOUD:
        upload_item_prices(result, config=config)
    return result
