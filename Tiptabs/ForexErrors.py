class ForexError(Exception):
    """Base error for internal forex operations."""


class InvalidForexRate(ForexError):
    """Raised when provider data cannot become a usable rate."""


class MissingForexRate(ForexError):
    """Raised when no direct or permitted inverse rate exists."""


class ProviderUnavailable(ForexError):
    """Raised or reported when the configured provider cannot supply data."""
