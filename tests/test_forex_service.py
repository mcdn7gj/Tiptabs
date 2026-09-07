import unittest
from datetime import datetime, timezone
from decimal import Decimal

from Tiptabs.ForexErrors import InvalidForexRate, MissingForexRate
from Tiptabs.ForexCache import ForexCache
from Tiptabs.ForexService import ForexService
from tests.forex_fixtures import FakeClock, forex_rate


class ForexServiceTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock(datetime.fromtimestamp(1700000100, tz=timezone.utc))
        self.cache = ForexCache(self.clock)
        self.service = ForexService(self.cache, freshness_seconds=300, clock=self.clock)

    def test_direct_lookup(self):
        self.cache.put(forex_rate("EUR/USD", "1.10"))
        result = self.service.get_rate("EUR", "USD")
        self.assertEqual(result.rate, Decimal("1.10"))
        self.assertFalse(result.inverted)

    def test_inverse_lookup(self):
        self.cache.put(forex_rate("EUR/USD", "2"))
        result = self.service.get_rate("USD", "EUR")
        self.assertEqual(result.rate, Decimal("0.5"))
        self.assertTrue(result.inverted)

    def test_missing_rate_is_explicit(self):
        with self.assertRaises(MissingForexRate):
            self.service.get_rate("EUR", "JPY")

    def test_conversion_uses_decimal(self):
        self.cache.put(forex_rate("EUR/USD", "1.10"))
        self.assertEqual(self.service.convert("2.00", "EUR", "USD"), Decimal("2.200"))

    def test_invalid_amount_is_rejected(self):
        with self.assertRaises(InvalidForexRate):
            self.service.convert("not-a-number", "EUR", "USD")

    def test_freshness_reports_age(self):
        self.cache.put(forex_rate("EUR/USD", "1.10"))
        freshness = self.service.get_freshness("EUR", "USD")
        self.assertTrue(freshness["available"])
        self.assertFalse(freshness["stale"])


if __name__ == "__main__":
    unittest.main()
