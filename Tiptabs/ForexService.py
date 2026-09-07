from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from Tiptabs.ForexErrors import InvalidForexRate, MissingForexRate
from Tiptabs.ForexRate import CurrencyPair


@dataclass(frozen=True)
class RateResult:
    pair: CurrencyPair
    rate: Decimal
    source: str
    observed_at: object
    age: object
    inverted: bool = False


class ForexService:
    def __init__(self, cache, freshness_seconds=None, clock=None):
        self.cache = cache
        self.freshness_seconds = freshness_seconds
        self.clock = clock

    def get_rate(self, base, quote, allow_inverse=True):
        pair = _pair(base, quote)
        direct = self.cache.get(pair)
        if direct is not None:
            return RateResult(pair, direct.rate, direct.source, direct.observed_at, self._age(pair), False)
        if allow_inverse:
            inverse_pair = pair.inverse()
            inverse = self.cache.get(inverse_pair)
            if inverse is not None and inverse.rate > 0:
                return RateResult(
                    pair,
                    Decimal("1") / inverse.rate,
                    inverse.source,
                    inverse.observed_at,
                    self._age(inverse_pair),
                    True,
                )
        raise MissingForexRate("No usable rate is available for {0}".format(pair.key))

    def convert(self, amount, base, quote, allow_inverse=True):
        try:
            decimal_amount = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError):
            raise InvalidForexRate("Conversion amount must be numeric")
        if not decimal_amount.is_finite() or decimal_amount < 0:
            raise InvalidForexRate("Conversion amount must not be negative")
        result = self.get_rate(base, quote, allow_inverse)
        return decimal_amount * result.rate

    def get_freshness(self, base, quote):
        result = self.get_rate(base, quote)
        stale = self.freshness_seconds is not None and result.age.total_seconds() > self.freshness_seconds
        return {
            "available": True,
            "stale": stale,
            "age": result.age,
            "observed_at": result.observed_at,
            "source": result.source,
            "inverted": result.inverted,
        }

    def available_pairs(self):
        return tuple(self.cache.keys())

    def _age(self, pair):
        return self.cache.age(pair, self.clock() if self.clock else None)


def _pair(base, quote):
    try:
        return CurrencyPair(base, quote)
    except ValueError as error:
        raise InvalidForexRate(str(error))
