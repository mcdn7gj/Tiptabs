import unittest
import os
from Tiptabs.ForexConfig import ForexConfig


class ForexConfigTests(unittest.TestCase):
    def setUp(self):
        self.default_env = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.default_env)

    def test_from_env_with_defaults(self):
        os.environ["MASSIVE_FOREX_PAIRS"] = "EUR-USD"
        config = ForexConfig.from_env()
        self.assertEqual(config.pairs, ("EUR-USD",))
        self.assertEqual(config.refresh_seconds, 300)
        self.assertEqual(config.freshness_seconds, 300)
        self.assertEqual(config.frankfurter_endpoint, "")

    def test_from_env_with_custom_values(self):
        os.environ["MASSIVE_FOREX_PAIRS"] = "EUR-USD,USD-JPY,GBP-EUR"
        os.environ["FOREX_REFRESH_SECONDS"] = "600"
        os.environ["FOREX_FRESHNESS_SECONDS"] = "900"
        os.environ["FRANKFURTER_ENDPOINT"] = "https://custom.api/v2/"
        config = ForexConfig.from_env()
        self.assertEqual(config.pairs, ("EUR-USD", "USD-JPY", "GBP-EUR"))
        self.assertEqual(config.refresh_seconds, 600)
        self.assertEqual(config.freshness_seconds, 900)
        self.assertEqual(config.frankfurter_endpoint, "https://custom.api/v2/")

    def test_from_env_with_custom_environ_dict(self):
        environ = {
            "MASSIVE_FOREX_PAIRS": "EUR-GBP",
            "FOREX_REFRESH_SECONDS": "120",
            "FOREX_FRESHNESS_SECONDS": "180",
            "FRANKFURTER_ENDPOINT": "https://test.api/v2/",
        }
        config = ForexConfig.from_env(environ)
        self.assertEqual(config.pairs, ("EUR-GBP",))
        self.assertEqual(config.refresh_seconds, 120)
        self.assertEqual(config.freshness_seconds, 180)
        self.assertEqual(config.frankfurter_endpoint, "https://test.api/v2/")

    def test_from_env_pairs_with_spaces(self):
        os.environ["MASSIVE_FOREX_PAIRS"] = " EUR-USD , USD-JPY "
        config = ForexConfig.from_env()
        self.assertEqual(config.pairs, ("EUR-USD", "USD-JPY"))

    def test_from_env_empty_pairs_raises(self):
        os.environ["MASSIVE_FOREX_PAIRS"] = ""
        with self.assertRaises(ValueError) as cm:
            ForexConfig.from_env()
        self.assertIn("at least one currency pair", str(cm.exception))

    def test_from_env_pairs_only_whitespace_raises(self):
        os.environ["MASSIVE_FOREX_PAIRS"] = "   ,  , "
        with self.assertRaises(ValueError) as cm:
            ForexConfig.from_env()
        self.assertIn("at least one currency pair", str(cm.exception))

    def test_from_env_refresh_seconds_invalid_int(self):
        os.environ["MASSIVE_FOREX_PAIRS"] = "EUR-USD"
        os.environ["FOREX_REFRESH_SECONDS"] = "not-a-number"
        with self.assertRaises(ValueError) as cm:
            ForexConfig.from_env()
        self.assertIn("positive integer", str(cm.exception))

    def test_from_env_refresh_seconds_zero_raises(self):
        os.environ["MASSIVE_FOREX_PAIRS"] = "EUR-USD"
        os.environ["FOREX_REFRESH_SECONDS"] = "0"
        with self.assertRaises(ValueError) as cm:
            ForexConfig.from_env()
        self.assertIn("positive integer", str(cm.exception))

    def test_from_env_refresh_seconds_negative_raises(self):
        os.environ["MASSIVE_FOREX_PAIRS"] = "EUR-USD"
        os.environ["FOREX_REFRESH_SECONDS"] = "-100"
        with self.assertRaises(ValueError) as cm:
            ForexConfig.from_env()
        self.assertIn("positive integer", str(cm.exception))

    def test_from_env_freshness_seconds_invalid_int(self):
        os.environ["MASSIVE_FOREX_PAIRS"] = "EUR-USD"
        os.environ["FOREX_FRESHNESS_SECONDS"] = "not-a-number"
        with self.assertRaises(ValueError) as cm:
            ForexConfig.from_env()
        self.assertIn("positive integer", str(cm.exception))

    def test_from_env_freshness_seconds_zero_raises(self):
        os.environ["MASSIVE_FOREX_PAIRS"] = "EUR-USD"
        os.environ["FOREX_FRESHNESS_SECONDS"] = "0"
        with self.assertRaises(ValueError) as cm:
            ForexConfig.from_env()
        self.assertIn("positive integer", str(cm.exception))

    def test_from_env_freshness_defaults_to_refresh(self):
        os.environ["MASSIVE_FOREX_PAIRS"] = "EUR-USD"
        os.environ["FOREX_REFRESH_SECONDS"] = "500"
        if "FOREX_FRESHNESS_SECONDS" in os.environ:
            del os.environ["FOREX_FRESHNESS_SECONDS"]
        config = ForexConfig.from_env()
        self.assertEqual(config.freshness_seconds, 500)

    def test_frozen_dataclass(self):
        config = ForexConfig(pairs=("EUR-USD",), refresh_seconds=300)
        with self.assertRaises(AttributeError):
            config.pairs = ("USD-JPY",)


if __name__ == "__main__":
    unittest.main()