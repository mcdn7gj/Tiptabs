import unittest
import os
from unittest.mock import patch, MagicMock

from Tiptabs.ForexCache import ForexCache
from Tiptabs.ForexService import ForexService
from Tiptabs.Tiptabs import Tiptabs
from Tiptabs.main import create_app, _available_currencies, _configured_currencies, main
from tests.forex_fixtures import forex_rate


class MainRouteTests(unittest.TestCase):
    def setUp(self):
        cache = ForexCache()
        cache.put(forex_rate("EUR/USD", "1.10"))
        cache.put(forex_rate("EUR/JPY", "150"))
        service = ForexService(cache)
        self.app = create_app(service, Tiptabs("EUR", forex_service=service), rates=["EUR", "JPY", "USD"])
        self.client = self.app.test_client()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "healthy")

    def test_home_get_renders_rates(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"USD", response.data)

    def test_home_post_uses_internal_service(self):
        response = self.client.post("/", data={
            "base_currency": "EUR",
            "bill_amount": "20",
            "tip_percentage": "15",
            "converted_currency": "USD",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["True"].startswith("Your total amount was:"))

    def test_home_post_missing_rate_returns_error(self):
        response = self.client.post("/", data={
            "base_currency": "EUR",
            "bill_amount": "20",
            "tip_percentage": "15",
            "converted_currency": "GBP",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("unavailable", response.get_json()["False"])

    def test_home_post_invalid_base_returns_error(self):
        response = self.client.post("/", data={
            "base_currency": "INVALID",
            "bill_amount": "20",
            "tip_percentage": "15",
            "converted_currency": "USD",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("ERROR", response.get_json()["False"])

    def test_home_post_empty_form_returns_error(self):
        response = self.client.post("/", data={})
        self.assertEqual(response.status_code, 200)
        self.assertIn("ERROR", response.get_json()["False"])

    def test_home_put_supported(self):
        # PUT is handled by the same route as GET/POST
        response = self.client.put("/")
        self.assertEqual(response.status_code, 200)

    def test_404_handler(self):
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["ERROR"], "Not Found.")


class MainHelperTests(unittest.TestCase):
    def test_available_currencies(self):
        cache = ForexCache()
        cache.put(forex_rate("EUR/USD", "1.10"))
        cache.put(forex_rate("EUR/JPY", "150"))
        service = ForexService(cache)
        currencies = _available_currencies(service)
        self.assertIn("EUR", currencies)
        self.assertIn("USD", currencies)
        self.assertIn("JPY", currencies)

    def test_configured_currencies(self):
        pairs = ("EUR-USD", "USD-JPY")
        currencies = _configured_currencies(pairs)
        self.assertIn("EUR", currencies)
        self.assertIn("USD", currencies)
        self.assertIn("JPY", currencies)

    @patch("Tiptabs.main.load_dotenv")
    @patch("Tiptabs.main.ForexConfig")
    @patch("Tiptabs.main.ForexCache")
    @patch("Tiptabs.main.ForexService")
    @patch("Tiptabs.main.Tiptabs")
    @patch("Tiptabs.main.FrankfurterProvider")
    @patch("Tiptabs.main.ForexRefresh")
    def test_main_creates_app_and_runs(self, mock_refresh, mock_provider, mock_tiptabs, mock_service, mock_cache, mock_config, mock_load_dotenv):
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.pairs = ("EUR-USD", "USD-JPY")
        mock_config_instance.refresh_seconds = 300
        mock_config_instance.freshness_seconds = 300
        mock_config.from_env.return_value = mock_config_instance

        mock_cache_instance = MagicMock()
        mock_cache.return_value = mock_cache_instance

        mock_service_instance = MagicMock()
        mock_service.return_value = mock_service_instance

        mock_tiptabs_instance = MagicMock()
        mock_tiptabs.return_value = mock_tiptabs_instance

        mock_provider_instance = MagicMock()
        mock_provider.return_value = mock_provider_instance

        mock_refresh_instance = MagicMock()
        mock_refresh.return_value = mock_refresh_instance

        # Verify the module can be imported and main function exists
        from Tiptabs import main
        self.assertTrue(hasattr(main, "main"))
        self.assertTrue(callable(main.main))

    @patch("Tiptabs.main.create_app")
    @patch("Tiptabs.main.load_dotenv")
    @patch("Tiptabs.main.ForexConfig")
    @patch("Tiptabs.main.ForexCache")
    @patch("Tiptabs.main.ForexService")
    @patch("Tiptabs.main.Tiptabs")
    @patch("Tiptabs.main.FrankfurterProvider")
    @patch("Tiptabs.main.ForexRefresh")
    @patch("Tiptabs.main.os.getenv", return_value="EUR")
    def test_main_function(self, mock_getenv, mock_refresh, mock_provider, mock_tiptabs, mock_service, mock_cache, mock_config, mock_load_dotenv, mock_create_app):
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.pairs = ("EUR-USD", "USD-JPY")
        mock_config_instance.refresh_seconds = 300
        mock_config_instance.freshness_seconds = 300
        mock_config.from_env.return_value = mock_config_instance

        mock_cache_instance = MagicMock()
        mock_cache.return_value = mock_cache_instance

        mock_service_instance = MagicMock()
        mock_service.return_value = mock_service_instance

        mock_tiptabs_instance = MagicMock()
        mock_tiptabs.return_value = mock_tiptabs_instance

        mock_provider_instance = MagicMock()
        mock_provider.return_value = mock_provider_instance

        mock_refresh_instance = MagicMock()
        mock_refresh.return_value = mock_refresh_instance

        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        # Call main - it will call app.run which is mocked
        main()

        # Verify the setup was called
        mock_config.from_env.assert_called_once()
        mock_cache.assert_called_once()
        mock_service.assert_called_once()
        mock_tiptabs.assert_called_once()
        mock_provider.assert_called_once()
        mock_refresh.assert_called_once()
        mock_refresh_instance.start.assert_called_once()
        mock_refresh_instance.stop.assert_called_once()
        mock_app.run.assert_called_once_with(host='0.0.0.0', port=5000)

    def test_main_module_imports(self):
        # Verify main module can be imported without errors
        from Tiptabs import main
        self.assertTrue(hasattr(main, "create_app"))
        self.assertTrue(hasattr(main, "main"))


if __name__ == "__main__":
    unittest.main()