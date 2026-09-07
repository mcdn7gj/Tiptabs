import unittest

from Tiptabs.ForexCache import ForexCache
from Tiptabs.ForexRefresh import ForexRefresh
from Tiptabs.ForexService import ForexService
from tests.forex_fixtures import forex_rate


class FakeProvider:
    def __init__(self, connected=True, error=None):
        self.connected = connected
        self.last_error = error
        self.starts = 0
        self.stops = 0

    def start(self):
        self.starts += 1

    def stop(self):
        self.stops += 1


class ForexRefreshTests(unittest.TestCase):
    def test_reconcile_reports_cache_and_provider_status(self):
        cache = ForexCache()
        cache.put(forex_rate())
        provider = FakeProvider()
        refresh = ForexRefresh(provider, ForexService(cache), interval_seconds=300)

        status = refresh.reconcile()

        self.assertTrue(status["provider_connected"])
        self.assertEqual(status["cached_pairs"], ("EUR/USD",))

    def test_reconcile_does_not_reconnect_on_interval(self):
        provider = FakeProvider()
        refresh = ForexRefresh(provider, ForexService(ForexCache()), interval_seconds=300)

        refresh.reconcile()
        refresh.reconcile()

        self.assertEqual(provider.starts, 0)

    def test_start_and_stop_are_controlled(self):
        provider = FakeProvider()
        refresh = ForexRefresh(provider, ForexService(ForexCache()), interval_seconds=300)

        refresh.start()
        refresh.stop()

        self.assertEqual(provider.starts, 1)
        self.assertEqual(provider.stops, 1)


if __name__ == "__main__":
    unittest.main()
