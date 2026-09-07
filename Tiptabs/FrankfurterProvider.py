import logging
import time
from datetime import datetime, timezone
from decimal import Decimal
from threading import Event, Thread
from urllib.parse import urljoin

import requests

from Tiptabs.ForexErrors import InvalidForexRate, ProviderUnavailable
from Tiptabs.ForexRate import CurrencyPair, ForexRate


class FrankfurterProvider:
    """Adapter for Frankfurter's REST API."""

    default_endpoint = "https://api.frankfurter.dev/v2/"

    def __init__(self, config, on_rate, http_client=None, logger=None):
        self.config = config
        self.on_rate = on_rate
        self.logger = logger or logging.getLogger(__name__)
        self.http_client = http_client or requests.Session()
        self._stop_event = Event()
        self.last_error = None
        self.connected = False

    @property
    def url(self):
        endpoint = getattr(self.config, "frankfurter_endpoint", None) or self.default_endpoint
        return urljoin(endpoint, "rates")

    def _fetch_rates(self):
        pairs_by_base = {}
        for pair_symbol in self.config.pairs:
            pair = CurrencyPair.parse(pair_symbol)
            pairs_by_base.setdefault(pair.base, []).append(pair.quote)

        for base, quotes in pairs_by_base.items():
            params = {"base": base, "quotes": ",".join(quotes)}
            try:
                response = self.http_client.get(self.url, params=params, timeout=10)
                response.raise_for_status()
                self._handle_response(response.json(), base)
            except requests.RequestException as error:
                self._on_error(ProviderUnavailable(f"Frankfurter request failed: {error}"))
                return False
            except (ValueError, KeyError, InvalidForexRate) as error:
                self._on_error(InvalidForexRate(f"Frankfurter response invalid: {error}"))
                return False
            except Exception as error:
                self._on_error(ProviderUnavailable(f"Frankfurter request failed: {error}"))
                return False
        return True

    def _handle_response(self, payload, expected_base):
        # Frankfurter returns a list of rate objects: [{"base": "EUR", "quote": "USD", "rate": 1.16, "date": "2026-09-07"}]
        if not isinstance(payload, list):
            raise InvalidForexRate("Response is not a JSON array")

        if not payload:
            raise InvalidForexRate("Response array is empty")

        provider_timestamp = int(time.time() * 1000)
        observed_at = datetime.fromtimestamp(provider_timestamp / 1000, tz=timezone.utc)

        for item in payload:
            if not isinstance(item, dict):
                self.logger.debug("Skipping non-dict item in response: %s", item)
                continue

            base = item.get("base")
            if base != expected_base:
                self.logger.debug("Response base %s does not match requested %s", base, expected_base)
                continue

            quote = item.get("quote")
            rate_value = item.get("rate")
            date_str = item.get("date")

            if not quote or rate_value is None:
                self.logger.debug("Skipping item missing quote or rate: %s", item)
                continue

            try:
                pair = CurrencyPair(base, quote)
                if pair.provider_symbol not in self.config.pairs:
                    continue
                rate = ForexRate(
                    pair=pair,
                    rate=Decimal(str(rate_value)),
                    source="frankfurter",
                    observed_at=observed_at,
                    provider_timestamp=provider_timestamp,
                )
                self.on_rate(rate)
            except (ValueError, InvalidForexRate, TypeError):
                self.logger.debug("Skipping invalid rate for %s/%s", base, quote)
                continue

    def _on_error(self, error):
        self.last_error = error
        self.connected = False
        self.logger.warning("Frankfurter forex provider unavailable: %s", error)

    def run(self):
        while not self._stop_event.is_set():
            self.connected = True
            self.last_error = None
            self._fetch_rates()
            self._stop_event.wait(self.config.refresh_seconds)

    def start(self):
        thread = Thread(target=self.run, name="frankfurter-forex-provider", daemon=True)
        thread.start()
        return thread

    def stop(self):
        self._stop_event.set()