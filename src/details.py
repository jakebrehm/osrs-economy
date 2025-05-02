"""
Generates a JSON file with all tradeable items in the game.
"""

import datetime as dt
import json
import random

import pandas as pd
import pytz
import requests
from tqdm import tqdm

from .cloud.bigquery.handler import BigQueryHandler
from .cloud.storage.handler import StorageHandler
from .config import Config
from .structures.enums import BigQueryItem, StorageItem, StorageMode
from .utilities import get_iso_datetime, wait_for_okay


def get_item_details(config: Config) -> dict:
    """Gets the details for all tradeable items from a JSON file."""
    result_type = StorageItem.DETAILS
    filename = result_type.filename
    try:
        with StorageHandler.from_config(config) as handler:
            return handler.load(result_type)
    except FileNotFoundError:
        tqdm.write(f"Error occurred while opening JSON file '{filename}'.")
    except json.JSONDecodeError:
        tqdm.write(f"Error occurred while decoding JSON file '{filename}'.")
    return {}


def get_item_ids(config: Config) -> list[int]:
    """Gets a list of IDs for all tradeable items in the game."""
    try:
        response = requests.get(
            url=config.get("endpoints", "wiki"),
            headers={"User-Agent": config.get("user_agent")},
            timeout=config.get("timeout"),
        )
    except requests.exceptions.RequestException:
        tqdm.write("Error occurred while fetching item IDs.")
        return []
    return list(int(item_id) for item_id in response.json()["data"].keys())


def get_item_details_from_id(
    item_id: int,
    config: Config,
) -> dict:
    """Gets the details for a specific item ID.

    Will returned a dictionary with the item details that is cleaned by default.
    When the dictionary is cleaned, trade information is removed. To disable
    cleaning, set the `raw` parameter to `True`.

    Will throw an exception if the request fails.
    """
    response = requests.get(
        url=config.get("endpoints", "details"),
        params={"item": item_id},
        headers={"User-Agent": config.get("user_agent")},
        timeout=config.get("timeout"),
    )
    response.raise_for_status()
    return response.json()["item"]


def randomly_select_ids(items: dict, config: Config) -> list[int]:
    """Randomly selects outdated items from the provided dictionary."""
    threshold_days = config.get("minimum_days_before_update")
    chunk_size = config.get("update_chunk_size")
    outdated_items = []
    for item_id, details in items.items():
        last_updated = dt.datetime.fromisoformat(details["updated_at"])
        cutoff = dt.datetime.now(pytz.utc) - dt.timedelta(days=threshold_days)
        if last_updated < cutoff:
            outdated_items.append(int(item_id))
    population_size = len(outdated_items)
    tqdm.write(f"Found {population_size} outdated items.")
    return random.sample(outdated_items, k=min(chunk_size, population_size))


def fetch_item_details(
    data: dict,
    config: Config,
    wait: float = 5.0,
    chunk_size: int = 20,
) -> dict:
    """Gets details for all tradeable items as well as a list of invalid IDs.

    Wait is the amount of time to wait between requests (defaults to 5 seconds,
    which will avoid rate limiting).
    Chunk size is the number of items to fetch before saving intermittently.
    """

    # Verify that the data has the necessary format
    if "items" not in data:
        data["items"] = {}
    if "invalid" not in data:
        data["invalid"] = []

    # Determine which items are missing
    all_ids = get_item_ids(config=config)
    details = data["items"]
    invalid_ids = data["invalid"]
    existing_ids = [int(item_id) for item_id in details]
    outdated_ids = randomly_select_ids(details, config=config)
    missing_ids = list(set(all_ids) - set(existing_ids) - set(invalid_ids))
    ids_to_fetch = missing_ids + outdated_ids

    # Return if there are no missing items
    if not ids_to_fetch:
        tqdm.write("All items are up to date.")
        return data

    # Initialize the progress bar
    TQDM_TOTAL = len(all_ids) - len(invalid_ids)
    TQDM_START = TQDM_TOTAL - len(ids_to_fetch)
    tqdm_bar = tqdm(
        total=TQDM_TOTAL,
        initial=TQDM_START,
        desc="Fetching",
        unit="item",
        leave=False,
    )

    # Continuously fetch missing item details until all items are fetched
    interrupted = False
    unsaved_count = 0
    max_length = len(str(max(ids_to_fetch)))
    for item_id in ids_to_fetch:
        try:
            item_details = get_item_details_from_id(item_id, config=config)
            icon_url = item_details.get("icon", None)
            item_details = clean_item_details(item_details)
        except KeyboardInterrupt:
            interrupted = True
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            tqdm_bar.set_description("Skipping")
            tqdm.write(f"✖️ {item_id:>{max_length}}: Error")
            tqdm_bar.update(1)
            unsaved_count += 1
            data["invalid"].append(item_id)
        else:
            data["items"][str(item_id)] = item_details
            tqdm_bar.set_description("Fetching")
            tqdm.write(f"✔️ {item_id:>{max_length}}: {item_details['name']}")
            tqdm_bar.update(1)
            unsaved_count += 1
        # Save each image to Cloud Storage
        if config["save_icons"] and (icon_url is not None):
            tqdm.write("Saving item icon...")
            upload_item_icon(icon_url, item_id, config=config)
        # Save the unsaved details if the chunk size is reached
        if unsaved_count >= chunk_size:
            unsaved_count = 0
            tqdm.write("Writing unsaved details to JSON file...")
            save_item_details(data, config=config)
        # Wait to avoid rate limiting while monitoring for interrupts
        if not interrupted and not wait_for_okay(wait):
            tqdm_bar.set_description("Stopping")
            tqdm_bar.close()
            tqdm.write("Stopping fetch due to user interrupt.")
            break
    else:
        tqdm_bar.close()
        save_item_details(data, config=config)
    tqdm.write("Finished fetching items.")
    return data


def clean_item_details(item_details: dict) -> dict:
    """Cleans the item details dictionary.

    Removes unnecessary fields and adds the time that the item was updated.
    """

    # Define a list of desired keys
    desired_keys = [
        "id",
        "name",
        "description",
        "members",
    ]
    # Remove any undesired keys and return
    item_details = {
        key: value
        for key, value in item_details.items()
        if key in desired_keys
    }

    # Convert boolean values
    item_details["members"] = {
        "true": True,
        "false": False,
    }.get(item_details["members"], None)

    # Add the time that the item was updated
    item_details["updated_at"] = get_iso_datetime()

    # Return the cleaned item details
    return item_details


def save_item_details(data: dict, config: Config) -> dict:
    """Saves the item details to a JSON file and returns the dictionary."""

    # Add the time that the data was updated
    data["updated_at"] = get_iso_datetime()

    # Sort the appropriate structures by ID
    data["invalid"] = sorted(data["invalid"])
    data["items"] = dict(
        sorted(data["items"].items(), key=lambda i: i[1]["id"])
    )

    # Save the data to a JSON file and return
    with StorageHandler.from_config(config) as handler:
        handler.save(StorageItem.DETAILS, data)
    return data


def upload_item_icon(url: str, item_id: int, config: Config) -> None:
    """Uploads the item icons to Cloud Storage."""
    response = requests.get(url)
    response.raise_for_status()
    filename = f"images/{item_id}.gif"
    with StorageHandler.from_config(config) as handler:
        handler.save_image(StorageItem.DETAILS, response.content, filename)


def upload_item_details(data: dict, config: Config) -> None:
    """Uploads the item prices to BigQuery."""
    records = list(data["items"].values())
    df = pd.DataFrame.from_records(records)
    df.columns = ["id", "name", "description", "is_members", "updated_at"]
    df["updated_at"] = pd.to_datetime(
        df["updated_at"],
        format="ISO8601",
        utc=True,
    )
    with BigQueryHandler(config) as handler:
        handler.truncate(BigQueryItem.ITEMS)
        errors = handler.upload(BigQueryItem.ITEMS, df)
        if any(item for item in errors):
            tqdm.write("Errors occurred while handling details.")
            tqdm.write(errors)


def generate_item_details(config: Config) -> dict:
    """Generates the item details file from start to finish."""
    details_data = get_item_details(config=config)
    result = fetch_item_details(details_data, config=config)
    if config.storage_mode == StorageMode.CLOUD:
        upload_item_details(result, config=config)
    return result
