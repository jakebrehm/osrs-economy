"""
Generates a JSON file with all tradeable items in the game.
"""

import datetime as dt
import json
import time

import requests
from tqdm import tqdm

# Define constants
USER_AGENT = "OSRS Economy Tracker - Personal Project (jake.m.brehm@gmail.com)"
TIMEOUT = 10  # seconds

# Define API URLs
BASE_URL_WIKI = "https://prices.runescape.wiki/api/v1/osrs/latest"
BASE_URL_DETAIL = (
    "https://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json"
)


def get_item_details_from_json(filename: str) -> dict:
    """Gets the details for all tradeable items from a JSON file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        tqdm.write(f"Error occurred while opening JSON file '{filename}'.")
        return {}
    except json.JSONDecodeError:
        tqdm.write(f"Error occurred while decoding JSON file '{filename}'.")
        return {}


def get_item_ids() -> list[int]:
    """Gets a list of IDs for all tradeable items in the game."""

    try:
        response = requests.get(
            url=BASE_URL_WIKI,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        tqdm.write("Error occurred while fetching item IDs.")
        return []
    return list(int(item_id) for item_id in response.json()["data"].keys())


def get_item_details_from_id(item_id: int, raw: bool = False) -> dict:
    """Gets the details for a specific item ID.

    Will returned a dictionary with the item details that is cleaned by default.
    When the dictionary is cleaned, trade information is removed. To disable
    cleaning, set the `raw` parameter to `True`.

    Will throw an exception if the request fails.
    """

    response = requests.get(
        url=BASE_URL_DETAIL,
        params={"item": item_id},
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    result = response.json()["item"]
    return result if raw else clean_item_details(result)


def fetch_item_details(
    data: dict,
    filename: str,
    wait: float = 5.0,
    chunk_size: int = 20,
) -> dict:
    """Gets details for all tradeable items as well as a list of invalid IDs.

    Wait is the amount of time to wait between requests.
    Chunk size is the number of items to fetch before saving intermittently.
    """

    # Determine which items are missing
    all_ids = get_item_ids()
    details = data["items"]
    invalid_ids = data["invalid"]
    existing_ids = [int(item_id) for item_id in details]
    missing_ids = list(set(all_ids) - set(existing_ids) - set(invalid_ids))

    # Return if there are no missing items
    if not missing_ids:
        tqdm.write("All items are up to date.")
        return data

    # Initialize the progress bar
    tqdm_bar = tqdm(
        total=len(all_ids),
        initial=len(existing_ids),
        desc="Fetching",
        unit="item",
        leave=False,
    )

    # Continuously fetch missing item details until all items are fetched
    okay_to_proceed = True
    unsaved_count = 0
    max_length = len(str(max(missing_ids)))
    for item_id in missing_ids:
        try:
            missing_details = get_item_details_from_id(item_id)
        except KeyboardInterrupt:
            wait = 0.0
            okay_to_proceed = False
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            tqdm_bar.set_description("Skipping")
            tqdm.write(f"✖️ {item_id:>{max_length}}: Error")
            tqdm_bar.update(1)
            unsaved_count += 1
            data["invalid"].append(item_id)
        else:
            data["items"][item_id] = missing_details
            tqdm_bar.set_description("Fetching")
            tqdm.write(f"✔️ {item_id:>{max_length}}: {missing_details['name']}")
            tqdm_bar.update(1)
            unsaved_count += 1
        # Save the unsaved details if the chunk size is reached
        if unsaved_count >= chunk_size:
            unsaved_count = 0
            tqdm.write("Writing unsaved details to JSON file...")
            save_item_details_to_json(data, filename)
        # Wait to avoid rate limiting while monitoring for interrupts
        okay_to_proceed = wait_for_okay(wait)
        if not okay_to_proceed:
            tqdm_bar.set_description("Stopping")
            tqdm_bar.close()
            tqdm.write("Stopping fetch due to user interrupt.")
            break
    else:
        tqdm_bar.close()
        save_item_details_to_json(data, filename)
    return data


def wait_for_okay(wait: float) -> bool:
    """Waits for a specified amount of time and monitors for interrupts.

    Return True if the user has not interrupted the program, False otherwise.
    """
    try:
        time.sleep(wait)
    except KeyboardInterrupt:
        return False
    return True


def clean_item_details(item_details: dict) -> dict:
    """Cleans the item details dictionary.

    Removes unnecessary fields and adds the time that the item was updated.
    """

    # Define a list of undesired keys
    undesired_keys = [
        "icon",
        "icon_large",
        "type",
        "typeIcon",
        "current",
        "today",
        "day30",
        "day90",
        "day120",
        "day180",
    ]
    # Remove any undesired keys and return
    for key in undesired_keys:
        try:
            del item_details[key]
        except KeyError:
            pass

    # Convert boolean values
    item_details["members"] = {
        "true": True,
        "false": False,
    }.get(item_details["members"], None)

    # Add the time that the item was updated
    item_details["updated_at"] = dt.datetime.now().isoformat()

    # Return the cleaned item details
    return item_details


def save_item_details_to_json(
    data: dict,
    filename: str,
    indent: int = 4,
) -> dict:
    """Saves the item details to a JSON file and returns the dictionary."""

    # Add the time that the data was updated
    data["updated_at"] = dt.datetime.now().isoformat()

    # Sort the appropriate structures by ID
    data["invalid"] = sorted(data["invalid"])
    data["items"] = dict(sorted(data["items"].items(), key=lambda i: i[1]["id"]))

    # Save the data to a JSON file and return
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)
    return data


def main() -> None:
    """Main function."""
    details_filename = "details.json"
    details_data = get_item_details_from_json(details_filename)
    fetch_item_details(details_data, details_filename)
    tqdm.write("Finished fetching items.")


if __name__ == "__main__":
    main()
