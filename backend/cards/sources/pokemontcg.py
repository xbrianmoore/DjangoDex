"""
pokemontcg.io adapter (fallback).

NOTES:
pokemontcg.io card ids are NOT the same format as TCGdex ids
(e.g. TCGdex "swsh3-136" vs pokemontcg.io "swsh3-136" often line up for
Sword & Shield era sets, but this is not guaranteed across all sets/eras).

Will need to implement label/ID mapping for fallback of common cards
"""

from pokemontcgsdk import Card as SdkCard
from pokemontcgsdk import RestClient

from .base import Card, CardNotFoundError, CardSource, CardSourceUnavailableError


class PokemonTcgIoSource(CardSource):
    name = "pokemontcg"

    def __init__(self, api_key: str | None = None):
        # RestClient.configure() sets the key for the whole process, since
        # the SDK doesn't support a per-instance client. Safe to call with
        # None (falls back to the SDK's default, more limited rate).
        if api_key:
            RestClient.configure(api_key)

    def get_card(self, card_id: str) -> Card:
        try:
            raw = SdkCard.find(card_id)
        except Exception as exc:
            message = str(exc).lower()
            if "404" in message or "not found" in message:
                raise CardNotFoundError(
                    f"No card found for id '{card_id}' in pokemontcg.io"
                ) from exc
            raise CardSourceUnavailableError(
                f"pokemontcg.io request failed: {exc}"
            ) from exc

        if raw is None:
            raise CardNotFoundError(
                f"No card found for id '{card_id}' in pokemontcg.io"
            )

        images = getattr(raw, "images", None)
        card_set = getattr(raw, "set", None)
        hp_raw = getattr(raw, "hp", None)

        return Card(
            id=raw.id,
            name=raw.name,
            set_name=getattr(card_set, "name", None) if card_set else None,
            local_id=getattr(raw, "number", None),
            total_in_set=getattr(card_set, "printedTotal", None) if card_set else None,
            image_url=(getattr(images, "large", None) or getattr(images, "small", None))
            if images
            else None,
            hp=int(hp_raw) if hp_raw and str(hp_raw).isdigit() else None,
            types=list(getattr(raw, "types", None) or []),
            rarity=getattr(raw, "rarity", None),
            source=self.name,
        )
