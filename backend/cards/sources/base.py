"""
base.py

Base interface for ADAPTER PATTERN. Sources (TCGdex, pokemontcg.io, etc.)
are translated from respective API/SDK here using 'CardSource' Abstract Class.

NOTES:
NEVER import SDK or use API calls here (breaks pattern)

'service.py' calls these cards as an entry point into django framework
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Card:
    id: str
    name: str
    set_name: str | None = None
    local_id: str | None = None  # card number within its set
    total_in_set: int | None = None
    image_url: str | None = None
    hp: int | None = None
    types: list[str] = field(default_factory=list)
    rarity: str | None = None
    source: str = ""  # card origin source


class CardNotFoundError(Exception):
    """Raised when a source successfully responds but has no such card."""


class CardSourceUnavailableError(Exception):
    """Raised when a source fails to respond at all (network error, 5xx, timeout, etc.)."""


class CardSource(ABC):
    """Abstract interface every card data source must implement."""

    name: str = "base"

    @abstractmethod
    def get_card(self, card_id: str) -> Card:
        """
        Raises:
            CardNotFoundError: the source responded but has no such card.
            CardSourceUnavailableError: the source could not be reached at all.
        """
        raise NotImplementedError
