"""
All enums used in the project.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import Config


class ExecutionMode(Enum):
    """The available execution modes for the project."""

    DETAILS = auto()
    PRICES = auto()


class StorageMode(Enum):
    """The available storage modes for the project."""

    LOCAL = auto()
    CLOUD = auto()


class ResultType(Enum):
    """The available result types for the project."""

    DETAILS = auto()
    PRICES = auto()

    def filename(self, config: Config) -> str:
        """Gets the filename for the result."""
        match self:
            case ResultType.DETAILS:
                return "details.json"
            case ResultType.PRICES:
                return f"prices_{config.CREATED}.json"

    def bucket(self, config: Config) -> str:
        """Gets the bucket name for the result."""
        return config.get("buckets", self.name.lower())
