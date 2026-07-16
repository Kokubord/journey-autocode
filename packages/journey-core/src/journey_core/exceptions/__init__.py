"""Custom exceptions for journey-core (Constituição §5.4)."""


class JourneyError(Exception):
    """Base class for all Journey domain errors."""


class WriteRoutingError(JourneyError):
    """Raised when a write is routed to a forbidden location (e.g. a UNC path)."""
