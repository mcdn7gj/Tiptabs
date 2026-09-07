import unittest
from datetime import datetime, timezone, timedelta

from Tiptabs.ForexCache import ForexCache
from tests.forex_fixtures import FakeClock, forex_rate


class ForexCacheTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.fromtimestamp(1700000100, tz=timezone.utc)
        self.cache = ForexCache(FakeClock(self.now))

    def test_newer_rate_replaces_older_rate(self):
        self.assertTrue(self.cache.put(forex_rate(timestamp=1700000000000)))
        self.assertTrue(self.cache.put(forex_rate(rate="1.20", timestamp=1700000001000)))
        self.assertEqual(str(self.cache.get(forex_rate().pair).rate), "1.20")

    def test_older_rate_does_not_replace_newer_rate(self):
        self.cache.put(forex_rate(rate="1.20", timestamp=1700000001000))
        self.assertFalse(self.cache.put(forex_rate(timestamp=1700000000000)))
        self.assertEqual(str(self.cache.get(forex_rate().pair).rate), "1.20")

    def test_age_and_missing_lookup(self):
        rate = forex_rate(timestamp=1700000000000)
        self.cache.put(rate)
        self.assertEqual(self.cache.age(rate.pair), timedelta(seconds=100))
        self.assertIsNone(self.cache.get(forex_rate("GBP/USD").pair))
        self.assertIsNone(self.cache.age(forex_rate("GBP/USD").pair))

    def test_clear_removes_rates(self):
        rate = forex_rate()
        self.cache.put(rate)
        self.cache.clear()
        self.assertIsNone(self.cache.get(rate.pair))


if __name__ == "__main__":
    unittest.main()
