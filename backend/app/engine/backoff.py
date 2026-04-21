"""Exponential backoff for HTTP 429 responses.

Implements backoff calculation: delay = min(30 * 2^(N-1), 600) seconds
where N is the number of consecutive 429 responses.
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


class ExponentialBackoff:
    """Exponential backoff calculator for HTTP 429 (Too Many Requests).

    Formula: delay = min(base * 2^(N-1), max_delay)
    where N is the consecutive 429 count (starting at 1).

    Default: base=30s, max=600s (10 minutes)
    Sequence: 30s -> 60s -> 120s -> 240s -> 480s -> 600s (capped)
    """

    def __init__(self, base: int = 30, max_delay: int = 600) -> None:
        """Initialize backoff calculator.

        Args:
            base: Base delay in seconds (default: 30).
            max_delay: Maximum delay in seconds (default: 600).
        """
        self._base = base
        self._max_delay = max_delay
        self._consecutive_count = 0

    @property
    def base(self) -> int:
        """Return the base delay."""
        return self._base

    @property
    def max_delay(self) -> int:
        """Return the maximum delay."""
        return self._max_delay

    @property
    def consecutive_count(self) -> int:
        """Return the current consecutive 429 count."""
        return self._consecutive_count

    def record_429(self) -> float:
        """Record a 429 response and return the backoff delay.

        Increments the consecutive count and calculates the delay.

        Returns:
            The backoff delay in seconds.
        """
        self._consecutive_count += 1
        delay = self.calculate(self._consecutive_count)

        logger.warning(
            "HTTP 429 backoff applied",
            consecutive_count=self._consecutive_count,
            delay_seconds=delay,
        )

        return delay

    def reset(self) -> None:
        """Reset the consecutive count after a successful request."""
        if self._consecutive_count > 0:
            logger.info(
                "Backoff reset after successful request",
                previous_count=self._consecutive_count,
            )
        self._consecutive_count = 0

    def calculate(self, n: int) -> float:
        """Calculate backoff delay for N consecutive 429 responses.

        Formula: min(base * 2^(N-1), max_delay)

        Args:
            n: Number of consecutive 429 responses (N >= 1).

        Returns:
            The backoff delay in seconds.
        """
        if n < 1:
            return 0.0

        delay = self._base * (2 ** (n - 1))
        return min(delay, self._max_delay)
