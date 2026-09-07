import unittest

from Tiptabs.ForexCache import ForexCache
from Tiptabs.ForexRefresh import ForexRefresh, ForexProviderProtocol
from Tiptabs.ForexService import ForexService
from tests.forex_fixtures import forex_rate


class FakeProvider:
    def __init__(self, on_rate):
        self.on_rate = on_rate
        self.connected = True
        self.last_error = None
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True
        self.on_rate(forex_rate("EUR/USD", "1.10"))

    def stop(self):
        self.stopped = True


class ForexProviderContractTests(unittest.TestCase):
    def test_fake_provider_can_supply_normalized_rates(self):
        cache = ForexCache()
        provider = FakeProvider(cache.put)

        # Verify it matches the protocol
        self.assertTrue(hasattr(provider, 'start'))
        self.assertTrue(hasattr(provider, 'stop'))
        self.assertTrue(hasattr(provider, 'connected'))
        self.assertTrue(hasattr(provider, 'last_error'))

        provider.start()

        self.assertIsNotNone(cache.get(forex_rate("EUR/USD").pair))
        self.assertTrue(provider.started)

    def test_refresh_accepts_provider_without_massive_types(self):
        cache = ForexCache()
        provider = FakeProvider(cache.put)
        refresh = ForexRefresh(provider, ForexService(cache))

        refresh.start()
        refresh.stop()

        self.assertTrue(provider.started)
        self.assertTrue(provider.stopped)


if __name__ == "__main__":
    unittest.main()