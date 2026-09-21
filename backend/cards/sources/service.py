"""
CardService: the single entry point the rest of the Django app should use.

Nowhere else in the app should import TCGdexSource or PokemonTcgIoSource
directly or use and SDK/API.
"""

import logging

from .base import Card, CardNotFoundError, CardSource, CardSourceUnavailableError

logger = logging.getLogger(__name__)


class CardService:
    def __init__(self, sources: list[CardSource]):
        if not sources:
            raise ValueError("CardService needs at least one CardSource")
        self._sources = sources

    def get_card(self, card_id: str) -> Card:
        """
        Try each source in order. Move to the next source only if the
        current one is UNAVAILABLE (network/server error). If a source
        is reachable but genuinely has no such card, that's treated as
        a real "not found" and we stop rather than masking it by trying
        every other source with a mismatched id.

        Can only use a mirror-like system if we implement ID-mapping across sources
        """
        last_error: Exception | None = None

        for source in self._sources:
            try:
                return source.get_card(card_id)
            except CardNotFoundError as exc:
                logger.info("Card '%s' not found in %s", card_id, source.name)
                last_error = exc
                # Deliberately does NOT fall through automatically here —
                # see note in pokemontcg_source.py about id mismatches.
                # If you want "not found" to also trigger fallback, change
                # this to `continue` — but be aware ids may not line up.
                # >> options: raise | continue
                raise
            except CardSourceUnavailableError as exc:
                logger.warning(
                    "%s is unavailable (%s), trying next source", source.name, exc
                )
                last_error = exc
                continue

        raise CardNotFoundError(
            f"Card '{card_id}' could not be retrieved from any source"
        ) from last_error


# Need to implement an array to streamline
def build_default_card_service() -> CardService:
    from .pokemontcg import PokemonTcgIoSource
    from .tcgdex import TCGdexSource

    return CardService(sources=[TCGdexSource(), PokemonTcgIoSource()])
