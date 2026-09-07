from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from Tiptabs.ForexErrors import InvalidForexRate


@dataclass(frozen=True)
class CurrencyPair:
    base: str
    quote: str

    def __post_init__(self):
        base = _currency_code(self.base)
        quote = _currency_code(self.quote)
        if base == quote:
            raise ValueError("Currency pair must contain two different currencies")
        object.__setattr__(self, "base", base)
        object.__setattr__(self, "quote", quote)

    @property
    def key(self):
        return "{0}/{1}".format(self.base, self.quote)

    @property
    def provider_symbol(self):
        return "{0}-{1}".format(self.base, self.quote)

    @classmethod
    def parse(cls, value):
        if not isinstance(value, str):
            raise ValueError("Currency pair must be a string")
        separator = "/" if "/" in value else "-"
        parts = [part.strip() for part in value.split(separator)]
        if len(parts) != 2:
            raise ValueError("Currency pair must use BASE/QUOTE or BASE-QUOTE format")
        return cls(parts[0], parts[1])

    def inverse(self):
        return CurrencyPair(self.quote, self.base)


@dataclass(frozen=True)
class ForexRate:
    pair: CurrencyPair
    rate: Decimal
    source: str
    observed_at: datetime
    provider_timestamp: int
    bid: Decimal = None
    ask: Decimal = None
    exchange: object = None

    def __post_init__(self):
        if not isinstance(self.pair, CurrencyPair):
            raise InvalidForexRate("ForexRate requires a CurrencyPair")
        rate = _positive_decimal(self.rate, "rate")
        bid = _optional_positive_decimal(self.bid, "bid")
        ask = _optional_positive_decimal(self.ask, "ask")
        if not self.source:
            raise InvalidForexRate("ForexRate requires a source")
        try:
            timestamp = int(self.provider_timestamp)
        except (TypeError, ValueError):
            raise InvalidForexRate("ForexRate requires an integer provider timestamp")
        if timestamp <= 0:
            raise InvalidForexRate("ForexRate requires a positive provider timestamp")
        observed_at = self.observed_at
        if observed_at.tzinfo is None:
            observed_at = observed_at.replace(tzinfo=timezone.utc)
        object.__setattr__(self, "rate", rate)
        object.__setattr__(self, "bid", bid)
        object.__setattr__(self, "ask", ask)
        object.__setattr__(self, "provider_timestamp", timestamp)
        object.__setattr__(self, "observed_at", observed_at.astimezone(timezone.utc))

    @classmethod
    def from_quote(cls, pair, bid, ask, source, provider_timestamp, exchange=None):
        normalized_bid = _optional_positive_decimal(bid, "bid")
        normalized_ask = _optional_positive_decimal(ask, "ask")
        if normalized_bid is None and normalized_ask is None:
            raise InvalidForexRate("Quote requires a positive bid or ask")
        if normalized_bid is not None and normalized_ask is not None:
            rate = (normalized_bid + normalized_ask) / Decimal("2")
        else:
            rate = normalized_bid or normalized_ask
        timestamp = int(provider_timestamp)
        observed_at = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
        return cls(pair, rate, source, observed_at, timestamp, normalized_bid, normalized_ask, exchange)


def _currency_code(value):
    if not isinstance(value, str) or len(value.strip()) != 3 or not value.strip().isalpha():
        raise ValueError("Currency codes must contain exactly three letters")
    return value.strip().upper()


def _positive_decimal(value, name):
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise InvalidForexRate("{0} must be numeric".format(name))
    if not decimal_value.is_finite() or decimal_value <= 0:
        raise InvalidForexRate("{0} must be positive".format(name))
    return decimal_value


def _optional_positive_decimal(value, name):
    if value is None or value == "":
        return None
    return _positive_decimal(value, name)
