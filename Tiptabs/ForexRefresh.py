import logging
import threading
from threading import Event, Thread
from typing import Protocol


class ForexProviderProtocol(Protocol):
    """Protocol for forex providers used by ForexRefresh."""

    def start(self) -> Thread:
        ...

    def stop(self) -> None:
        ...

    @property
    def connected(self) -> bool:
        ...

    @property
    def last_error(self):
        ...


class ForexRefresh:
    """Own provider startup and periodic freshness reconciliation."""

    def __init__(self, provider: ForexProviderProtocol, service, interval_seconds=300, logger=None):
        self.provider = provider
        self.service = service
        self.interval_seconds = interval_seconds
        self.logger = logger or logging.getLogger(__name__)
        self._stop_event = Event()
        self._thread = None
        self.last_status = None

    def reconcile(self):
        pairs = self.service.available_pairs()
        status = {
            "provider_connected": bool(self.provider.connected),
            "provider_error": self.provider.last_error,
            "cached_pairs": pairs,
        }
        self.last_status = status
        if status["provider_error"] is not None:
            self.logger.warning("Forex refresh observed provider error: %s", status["provider_error"])
        return status

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return self._thread
        self.provider.start()
        self._stop_event.clear()
        self._thread = Thread(target=self._run, name="forex-refresh", daemon=True)
        self._thread.start()
        return self._thread

    def _run(self):
        while not self._stop_event.wait(self.interval_seconds):
            self.reconcile()

    def stop(self):
        self._stop_event.set()
        self.provider.stop()
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(timeout=1)