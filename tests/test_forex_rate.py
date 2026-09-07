import unittest
from decimal import Decimal, InvalidOperation

from Tiptabs.ForexErrors import InvalidForexRate
from Tiptabs.ForexRate import CurrencyPair, ForexRate


class ForexRateTests(unittest.TestCase):
    def test_pair_is_canonical_and_provider_ready(self):
        pair = CurrencyPair.parse("eur/usd")
        self.assertEqual(pair.key, "EUR/USD")
        self.assertEqual(pair.provider_symbol, "EUR-USD")
        self.assertEqual(pair.inverse().key, "USD/EUR")

    def test_quote_uses_midpoint(self):
        rate = ForexRate.from_quote(CurrencyPair.parse("EUR/USD"), "1.10", "1.12", "massive", 1700000000000)
        self.assertEqual(rate.rate, Decimal("1.11"))
        self.assertEqual(rate.bid, Decimal("1.10"))
        self.assertEqual(rate.ask, Decimal("1.12"))
        self.assertEqual(rate.observed_at.tzinfo.tzname(rate.observed_at), "UTC")

    def test_quote_uses_single_valid_side(self):
        bid_rate = ForexRate.from_quote(CurrencyPair.parse("EUR/USD"), "1.10", None, "massive", 1700000000000)
        ask_rate = ForexRate.from_quote(CurrencyPair.parse("EUR/USD"), None, "1.12", "massive", 1700000000000)
        self.assertEqual(bid_rate.rate, Decimal("1.10"))
        self.assertEqual(ask_rate.rate, Decimal("1.12"))

    def test_invalid_quote_is_rejected(self):
        with self.assertRaises(InvalidForexRate):
            ForexRate.from_quote(CurrencyPair.parse("EUR/USD"), "0", "0", "massive", 1700000000000)

    def test_invalid_pair_is_rejected(self):
        with self.assertRaises(ValueError):
            CurrencyPair.parse("EUR")

    def test_pair_same_base_quote_raises(self):
        with self.assertRaises(ValueError):
            CurrencyPair("EUR", "EUR")

    def test_pair_normalizes_case(self):
        pair = CurrencyPair("eur", "usd")
        self.assertEqual(pair.base, "EUR")
        self.assertEqual(pair.quote, "USD")

    def test_pair_parse_with_hyphen(self):
        pair = CurrencyPair.parse("EUR-USD")
        self.assertEqual(pair.key, "EUR/USD")

    def test_pair_parse_invalid_format(self):
        with self.assertRaises(ValueError):
            CurrencyPair.parse("EUR/USD/GBP")

    def test_forex_rate_requires_currency_pair(self):
        with self.assertRaises(InvalidForexRate):
            ForexRate(pair="not-a-pair", rate="1.0", source="test", observed_at=None, provider_timestamp=1000)

    def test_forex_rate_invalid_rate_not_numeric(self):
        with self.assertRaises(InvalidForexRate):
            ForexRate(pair=CurrencyPair("EUR", "USD"), rate="abc", source="test", observed_at=None, provider_timestamp=1000)

    def test_forex_rate_invalid_rate_not_positive(self):
        with self.assertRaises(InvalidForexRate):
            ForexRate(pair=CurrencyPair("EUR", "USD"), rate="0", source="test", observed_at=None, provider_timestamp=1000)

    def test_forex_rate_invalid_rate_negative(self):
        with self.assertRaises(InvalidForexRate):
            ForexRate(pair=CurrencyPair("EUR", "USD"), rate="-1.5", source="test", observed_at=None, provider_timestamp=1000)

    def test_forex_rate_requires_source(self):
        with self.assertRaises(InvalidForexRate):
            ForexRate(pair=CurrencyPair("EUR", "USD"), rate="1.0", source="", observed_at=None, provider_timestamp=1000)

    def test_forex_rate_invalid_provider_timestamp(self):
        with self.assertRaises(InvalidForexRate):
            ForexRate(pair=CurrencyPair("EUR", "USD"), rate="1.0", source="test", observed_at=None, provider_timestamp="not-int")

    def test_forex_rate_invalid_provider_timestamp_negative(self):
        with self.assertRaises(InvalidForexRate):
            ForexRate(pair=CurrencyPair("EUR", "USD"), rate="1.0", source="test", observed_at=None, provider_timestamp=-1)

    def test_forex_rate_observed_at_utc_normalization(self):
        from datetime import datetime, timezone
        naive_dt = datetime(2024, 1, 15, 12, 0, 0)
        rate = ForexRate(pair=CurrencyPair("EUR", "USD"), rate="1.0", source="test", observed_at=naive_dt, provider_timestamp=1000)
        self.assertEqual(rate.observed_at.tzinfo, timezone.utc)

    def test_from_quote_requires_bid_or_ask(self):
        with self.assertRaises(InvalidForexRate):
            ForexRate.from_quote(CurrencyPair.parse("EUR/USD"), None, None, "test", 1700000000000)

    def test_from_quote_invalid_bid(self):
        with self.assertRaises(InvalidForexRate):
            ForexRate.from_quote(CurrencyPair.parse("EUR/USD"), "abc", "1.12", "test", 1700000000000)

    def test_from_quote_invalid_ask(self):
        with self.assertRaises(InvalidForexRate):
            ForexRate.from_quote(CurrencyPair.parse("EUR/USD"), "1.10", "abc", "test", 1700000000000)

    def test_inverse_pair(self):
        pair = CurrencyPair("EUR", "USD")
        inverse = pair.inverse()
        self.assertEqual(inverse.base, "USD")
        self.assertEqual(inverse.quote, "EUR")

    def test_pair_equality(self):
        pair1 = CurrencyPair("EUR", "USD")
        pair2 = CurrencyPair("EUR", "USD")
        pair3 = CurrencyPair("USD", "EUR")
        self.assertEqual(pair1, pair2)
        self.assertNotEqual(pair1, pair3)

    def test_pair_hash(self):
        pair1 = CurrencyPair("EUR", "USD")
        pair2 = CurrencyPair("EUR", "USD")
        self.assertEqual(hash(pair1), hash(pair2))


if __name__ == "__main__":
    unittest.main()