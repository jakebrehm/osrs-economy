"""
Utility functions for the project.
"""

import datetime as dt
import json
import time
from pathlib import Path
from typing import Any, Iterable, Iterator, NoReturn


def validate_directory(path: str) -> Path | NoReturn:
    """Checks if a directory is valid, otherwise raises an exception."""
    if (path_obj := Path(path)).is_dir():
        return path_obj
    raise NotADirectoryError(f"Directory '{path}' does not exist.")


def to_path(path: str | Path | None, default: str) -> Path:
    """Converts the provided object into a Path and returns it.

    If the provided object is None, the default path is returned.
    """
    if path is None:
        path = Path(default)
    elif isinstance(path, str):
        path = Path(path)
    return path


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
