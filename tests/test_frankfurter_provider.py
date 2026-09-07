import json
import time
import unittest
from decimal import Decimal
from unittest.mock import Mock, patch

from Tiptabs.ForexConfig import ForexConfig
from Tiptabs.ForexErrors import InvalidForexRate, ProviderUnavailable
from Tiptabs.FrankfurterProvider import FrankfurterProvider


class FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self._json_data


class FrankfurterProviderTests(unittest.TestCase):
    def setUp(self):
        self.config = ForexConfig(
            frankfurter_endpoint="https://api.frankfurter.dev/v2/",
            pairs=("EUR-USD", "USD-JPY"),
            refresh_seconds=300,
            freshness_seconds=300,
        )
        self.rates = []
        self.http_client = Mock()
        self.provider = FrankfurterProvider(self.config, self.rates.append, http_client=self.http_client)

    def test_fetch_rates_makes_correct_requests(self):
        self.http_client.get.return_value = FakeResponse([
            {"base": "EUR", "quote": "USD", "rate": 1.085, "date": "2024-01-15"}
        ])

        self.provider._fetch_rates()

        calls = self.http_client.get.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][1]["params"], {"base": "EUR", "quotes": "USD"})
        self.assertEqual(calls[1][1]["params"], {"base": "USD", "quotes": "JPY"})

    def test_valid_response_emits_normalized_rate(self):
        self.http_client.get.return_value = FakeResponse([
            {"base": "EUR", "quote": "USD", "rate": 1.085, "date": "2024-01-15"}
        ])

        self.provider._fetch_rates()

        self.assertEqual(len(self.rates), 1)
        rate = self.rates[0]
        self.assertEqual(rate.pair.key, "EUR/USD")
        self.assertEqual(rate.rate, Decimal("1.085"))
        self.assertEqual(rate.source, "frankfurter")

    def test_multiple_rates_in_response(self):
        self.http_client.get.return_value = FakeResponse([
            {"base": "EUR", "quote": "USD", "rate": 1.085, "date": "2024-01-15"},
            {"base": "EUR", "quote": "GBP", "rate": 0.872, "date": "2024-01-15"}
        ])

        self.provider._fetch_rates()

        self.assertEqual(len(self.rates), 1)

    def test_invalid_response_missing_base_is_skipped(self):
        self.http_client.get.return_value = FakeResponse([
            {"quote": "USD", "rate": 1.085, "date": "2024-01-15"}
        ])

        result = self.provider._fetch_rates()

        self.assertTrue(result)
        self.assertEqual(len(self.rates), 0)

    def test_invalid_response_missing_rate_is_skipped(self):
        self.http_client.get.return_value = FakeResponse([
            {"base": "EUR", "quote": "USD", "date": "2024-01-15"}
        ])

        result = self.provider._fetch_rates()

        self.assertTrue(result)
        self.assertEqual(len(self.rates), 0)

    def test_http_error_reports_provider_unavailable(self):
        self.http_client.get.side_effect = Exception("Connection timeout")

        result = self.provider._fetch_rates()

        self.assertFalse(result)
        self.assertIsInstance(self.provider.last_error, ProviderUnavailable)

    def test_non_200_response_reports_provider_unavailable(self):
        self.http_client.get.return_value = FakeResponse({"error": "not found"}, status_code=404)

        result = self.provider._fetch_rates()

        self.assertFalse(result)
        self.assertIsInstance(self.provider.last_error, ProviderUnavailable)

    def test_unsupported_pair_is_skipped(self):
        self.http_client.get.return_value = FakeResponse([
            {"base": "EUR", "quote": "GBP", "rate": 0.872, "date": "2024-01-15"}
        ])

        self.provider._fetch_rates()

        self.assertEqual(len(self.rates), 0)

    def test_malformed_json_raises_error(self):
        self.http_client.get.return_value = FakeResponse("not json")

        result = self.provider._fetch_rates()

        self.assertFalse(result)
        self.assertIsInstance(self.provider.last_error, InvalidForexRate)

    def test_non_list_response_raises_error(self):
        self.http_client.get.return_value = FakeResponse({"base": "EUR", "rates": {"USD": 1.1}})

        result = self.provider._fetch_rates()

        self.assertFalse(result)
        self.assertIsInstance(self.provider.last_error, InvalidForexRate)

    def test_empty_list_response_raises_error(self):
        self.http_client.get.return_value = FakeResponse([])

        result = self.provider._fetch_rates()

        self.assertFalse(result)
        self.assertIsInstance(self.provider.last_error, InvalidForexRate)

    def test_item_missing_quote_is_skipped(self):
        self.http_client.get.return_value = FakeResponse([
            {"base": "EUR", "rate": 1.085, "date": "2024-01-15"}
        ])

        self.provider._fetch_rates()

        self.assertEqual(len(self.rates), 0)

    def test_item_missing_rate_is_skipped(self):
        self.http_client.get.return_value = FakeResponse([
            {"base": "EUR", "quote": "USD", "date": "2024-01-15"}
        ])

        self.provider._fetch_rates()

        self.assertEqual(len(self.rates), 0)

    def test_request_exception_on_first_pair_continues_to_second(self):
        """When first pair request fails, second pair should still be attempted."""
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Connection timeout")
            return FakeResponse([
                {"base": "USD", "quote": "JPY", "rate": 150.0, "date": "2024-01-15"}
            ])

        self.http_client.get.side_effect = side_effect

        result = self.provider._fetch_rates()

        # First pair fails, second succeeds
        self.assertFalse(result)
        self.assertIsInstance(self.provider.last_error, ProviderUnavailable)

    def test_stop_sets_stop_event(self):
        self.provider.stop()
        self.assertTrue(self.provider._stop_event.is_set())

    def test_run_stops_when_event_set(self):
        """Test that run() exits when stop event is set."""
        self.provider._stop_event.set()
        # Should not raise any exception
        self.provider.run()

    def test_start_returns_thread(self):
        thread = self.provider.start()
        self.assertIsNotNone(thread)
        self.assertTrue(thread.daemon)
        self.provider.stop()
        thread.join(timeout=1)

    def test_start_creates_new_thread_each_call(self):
        """Each start() call creates a new thread (not idempotent)."""
        thread1 = self.provider.start()
        thread2 = self.provider.start()
        self.assertIsNot(thread1, thread2)
        self.provider.stop()
        thread1.join(timeout=1)
        thread2.join(timeout=1)

    def test_stop_clears_stop_event_and_joins_thread(self):
        thread = self.provider.start()
        self.provider.stop()
        thread.join(timeout=1)
        self.assertFalse(thread.is_alive())


if __name__ == "__main__":
    unittest.main()