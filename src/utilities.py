"""
Utility functions for the project.
"""

import datetime as dt
import json
import time
from typing import Any, Iterable, Iterator


def read_json(filename: str) -> dict:
    """Reads a JSON file and returns the contents as a dictionary."""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(filename: str, data: Any, indent: int = 4) -> None:
    """Writes data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)


def get_iso_datetime() -> dt.datetime:
    """Gets the current date and time in ISO format."""
    return dt.datetime.now(dt.timezone.utc).isoformat()


def as_chunks(sequence: Iterable[int], size: int) -> Iterator[list[str]]:
    """Splits a sequence into chunks of a specified size."""
    return (
        sequence[pos : pos + size] for pos in range(0, len(sequence), size)
    )


def wait_for_okay(wait: float) -> bool:
    """Waits for a specified amount of time and monitors for interrupts.

    Return True if the user has not interrupted the program, False otherwise.
    """
    try:
        time.sleep(wait)
    except KeyboardInterrupt:
        return False
    return True
