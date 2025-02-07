"""
All enums used in the project.
"""

from enum import Enum, auto


class Mode(Enum):
    """The available modes for the project."""

    DETAILS = auto()
    PRICES = auto()
