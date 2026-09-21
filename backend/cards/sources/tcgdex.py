"""
This is the ONLY file that should import `tcgdexsdk` directly. Everywhere
else in the app should depend on `card_sources.base.Card` and
`card_sources.base.CardSource` instead.
"""

from tcgdexsdk import TCGdex

from .base import Card, CardNotFoundError, CardSource, CardSourceUnavailableError


class TCGdexSource(CardSource):
    name = "tcgdex"

    def __init__(self, language: str = "en"):
        self._sdk = TCGdex(language)

    def get_card(self, card_id: str) -> Card:
        try:
            raw = self._sdk.card.getSync(card_id)
        except Exception as exc:
            """
            tcgdex-sdk doesn't currently raise a "not found" type, so treat a None/empty
            resultd as not-found and anything else
            as the source unavailable.
            """
            raise CardSourceUnavailableError(f"TCGdex request failed: {exc}") from exc

        if raw is None:
            raise CardNotFoundError(f"No card found for id '{card_id}' in TCGdex")

        return Card(
            id=raw.id,
            name=raw.name,
            set_name=getattr(raw.set, "name", None)
            if getattr(raw, "set", None)
            else None,
            local_id=getattr(raw, "localId", None),
            total_in_set=getattr(raw.set.cardCount, "total", None)
            if getattr(raw, "set", None) and getattr(raw.set, "cardCount", None)
            else None,
            image_url=getattr(raw, "image", None),
            hp=getattr(raw, "hp", None),
            types=list(getattr(raw, "types", None) or []),
            rarity=getattr(raw, "rarity", None),
            source=self.name,
        )
