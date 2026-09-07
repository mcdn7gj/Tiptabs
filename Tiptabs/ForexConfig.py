import os
from dataclasses import dataclass

from Tiptabs.ForexRate import CurrencyPair


@dataclass(frozen=True)
class ForexConfig:
    frankfurter_endpoint: str = ""
    pairs: tuple = ("EUR-USD",)
    refresh_seconds: int = 300
    freshness_seconds: int = 300

    @classmethod
    def from_env(cls, environ=None):
        values = os.environ if environ is None else environ
        raw_pairs = values.get("MASSIVE_FOREX_PAIRS", "EUR-USD")
        pairs = tuple(CurrencyPair.parse(item).provider_symbol for item in raw_pairs.split(",") if item.strip())
        if not pairs:
            raise ValueError("MASSIVE_FOREX_PAIRS must contain at least one currency pair")

        refresh_seconds = _positive_int(values.get("FOREX_REFRESH_SECONDS", "300"), "FOREX_REFRESH_SECONDS")
        freshness_seconds = _positive_int(
            values.get("FOREX_FRESHNESS_SECONDS", str(refresh_seconds)),
            "FOREX_FRESHNESS_SECONDS",
        )
        return cls(
            frankfurter_endpoint=values.get("FRANKFURTER_ENDPOINT", "").strip(),
            pairs=pairs,
            refresh_seconds=refresh_seconds,
            freshness_seconds=freshness_seconds,
        )


def _positive_int(value, name):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError("{0} must be a positive integer".format(name))
    if parsed <= 0:
        raise ValueError("{0} must be a positive integer".format(name))
    return parsed
