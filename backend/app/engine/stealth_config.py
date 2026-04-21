"""Stealth configuration for anti-bot evasion.

Implements multiple layers of anti-detection:
- Pool of 20+ current browser User-Agent strings
- Random delay between 2-7 seconds (uniform distribution)
- Session rotation every 50 requests
- Exponential backoff configuration
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

import structlog

logger = structlog.get_logger(__name__)

# Pool of 20+ current browser User-Agent strings (Chrome, Firefox, Safari
# on Windows, macOS, Linux)
DEFAULT_USER_AGENTS: list[str] = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Firefox on Linux
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    # Chrome on Android (mobile)
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    # Safari on iOS
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]

# Common viewport resolutions for stealth
VIEWPORT_OPTIONS: list[dict[str, int]] = [
    {"width": 1280, "height": 720},
    {"width": 1366, "height": 768},
    {"width": 1920, "height": 1080},
]


@dataclass
class StealthConfig:
    """Configuration for anti-bot stealth techniques.

    Attributes:
        user_agents: Pool of User-Agent strings to rotate through.
        min_delay: Minimum delay between requests in seconds.
        max_delay: Maximum delay between requests in seconds.
        session_rotation_interval: Number of requests before rotating session.
        backoff_initial: Initial backoff delay in seconds for HTTP 429.
        backoff_max: Maximum backoff delay in seconds.
    """

    user_agents: list[str] = field(default_factory=lambda: list(DEFAULT_USER_AGENTS))
    min_delay: float = 2.0
    max_delay: float = 7.0
    session_rotation_interval: int = 50
    backoff_initial: int = 30
    backoff_max: int = 600

    def get_random_user_agent(self) -> str:
        """Select a random User-Agent from the pool."""
        return random.choice(self.user_agents)

    def get_random_delay(self) -> float:
        """Generate a random delay between min_delay and max_delay (uniform distribution)."""
        return random.uniform(self.min_delay, self.max_delay)

    def get_random_viewport(self) -> dict[str, int]:
        """Select a random viewport from common resolutions."""
        return random.choice(VIEWPORT_OPTIONS)

    def should_rotate_session(self, request_count: int) -> bool:
        """Check if session should be rotated based on request count.

        Args:
            request_count: Number of requests made in current session.

        Returns:
            True if session should be rotated.
        """
        return request_count > 0 and request_count % self.session_rotation_interval == 0
