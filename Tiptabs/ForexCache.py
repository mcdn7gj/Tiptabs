from datetime import datetime, timezone
from threading import RLock


class ForexCache:
    """Thread-safe latest-rate repository for the current single-process runtime."""

    def __init__(self, clock=None):
        self._rates = {}
        self._lock = RLock()
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def put(self, rate):
        key = rate.pair.key
        with self._lock:
            current = self._rates.get(key)
            if current is not None and rate.provider_timestamp < current.provider_timestamp:
                return False
            self._rates[key] = rate
            return True

    def get(self, pair):
        with self._lock:
            return self._rates.get(pair.key)

    def age(self, pair, now=None):
        rate = self.get(pair)
        if rate is None:
            return None
        current_time = now or self._clock()
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
        return current_time.astimezone(timezone.utc) - rate.observed_at

    def keys(self):
        with self._lock:
            return tuple(self._rates.keys())

    def clear(self):
        with self._lock:
            self._rates.clear()
