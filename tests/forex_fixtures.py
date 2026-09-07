from datetime import datetime, timezone
from decimal import Decimal

from Tiptabs.ForexRate import CurrencyPair, ForexRate


def quote_message(pair="EUR/USD", bid="1.1000", ask="1.1002", timestamp=1700000000000):
    return {"ev": "C", "p": pair, "b": bid, "a": ask, "x": 48, "t": timestamp}


def forex_rate(pair="EUR/USD", rate="1.10", timestamp=1700000000000):
    currency_pair = CurrencyPair.parse(pair)
    observed_at = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
    return ForexRate(currency_pair, Decimal(rate), "massive", observed_at, timestamp)


class FakeClock:
    def __init__(self, current):
        self.current = current

    def __call__(self):
        return self.current
