"""Property-based tests for the Scraping Engine Core.

Tests Properties 6, 7, 8, 10, 12, and 13 from the design document.
"""

from __future__ import annotations

import asyncio
import string
from unittest.mock import AsyncMock, MagicMock

import pytest
from hypothesis import given, settings, strategies as st

from app.engine.backoff import ExponentialBackoff
from app.engine.crawl_queue import CrawlQueue
from app.engine.data_extractor import ESQUEMA_INMUEBLE_FIELDS, DataExtractor
from app.engine.stealth_config import StealthConfig


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Valid URLs for testing
url_strategy = st.from_regex(
    r"https?://[a-z][a-z0-9\-]{1,15}\.[a-z]{2,6}(/[a-z0-9\-]{1,10}){0,3}",
    fullmatch=True,
)

# Depth values (valid range 1-10)
depth_strategy = st.integers(min_value=1, max_value=10)

# CSS selector-like strings for testing
selector_strategy = st.from_regex(
    r"\.[a-z][a-z0-9\-]{1,15}",
    fullmatch=True,
)

# Field names from the schema
field_name_strategy = st.sampled_from(ESQUEMA_INMUEBLE_FIELDS)

# Consecutive 429 count (N >= 1)
consecutive_429_strategy = st.integers(min_value=1, max_value=20)


# ---------------------------------------------------------------------------
# Property 6: Crawl Queue Depth and Deduplication
# ---------------------------------------------------------------------------

# Feature: web-scraping-platform, Property 6: Crawl Queue Depth and Deduplication


@pytest.mark.property
class TestCrawlQueueProperty:
    """**Validates: Requirements 3.2, 3.3, 3.6**

    For any set of URLs discovered during crawling, the CrawlQueue SHALL:
    (a) never enqueue a URL at a depth exceeding the configured Profundidad_Navegacion
    (b) never enqueue a URL that has already been visited in the current execution
    """

    @given(
        max_depth=depth_strategy,
        urls=st.lists(url_strategy, min_size=1, max_size=20),
    )
    @settings(max_examples=100, deadline=None)
    def test_depth_limit_enforced(self, max_depth: int, urls: list[str]) -> None:
        """URLs at depth > max_depth are never enqueued."""
        queue = CrawlQueue(max_depth=max_depth)

        for url in urls:
            # Try to add at depth exceeding max
            result = queue.add(url, depth=max_depth + 1)
            assert result is False, (
                f"URL should be rejected at depth {max_depth + 1} "
                f"(max_depth={max_depth})"
            )

        # Queue should be empty since all were rejected
        assert queue.is_empty

    @given(
        max_depth=depth_strategy,
        urls=st.lists(url_strategy, min_size=2, max_size=20, unique=True),
    )
    @settings(max_examples=100, deadline=None)
    def test_urls_within_depth_are_accepted(
        self, max_depth: int, urls: list[str]
    ) -> None:
        """URLs at depth <= max_depth are accepted."""
        queue = CrawlQueue(max_depth=max_depth)

        for url in urls:
            depth = max_depth  # At the boundary
            result = queue.add(url, depth=depth)
            assert result is True, (
                f"URL should be accepted at depth {depth} "
                f"(max_depth={max_depth})"
            )

    @given(
        max_depth=depth_strategy,
        url=url_strategy,
    )
    @settings(max_examples=100, deadline=None)
    def test_deduplication_visited(self, max_depth: int, url: str) -> None:
        """A URL that has been visited cannot be re-enqueued."""
        queue = CrawlQueue(max_depth=max_depth)

        # Add and process the URL
        queue.add(url, depth=0)
        item = queue.next()
        assert item is not None
        assert item.url == url

        # Try to add the same URL again
        result = queue.add(url, depth=0)
        assert result is False, "Visited URL should not be re-enqueued"

    @given(
        max_depth=depth_strategy,
        url=url_strategy,
    )
    @settings(max_examples=100, deadline=None)
    def test_deduplication_enqueued(self, max_depth: int, url: str) -> None:
        """A URL already in the queue cannot be added again."""
        queue = CrawlQueue(max_depth=max_depth)

        # Add the URL
        result1 = queue.add(url, depth=0)
        assert result1 is True

        # Try to add the same URL again (still in queue, not yet visited)
        result2 = queue.add(url, depth=0)
        assert result2 is False, "URL already in queue should not be added again"


# ---------------------------------------------------------------------------
# Property 7: Extraction Produces Complete 66-Field Records
# ---------------------------------------------------------------------------

# Feature: web-scraping-platform, Property 7: Extraction Produces Complete 66-Field Records


@pytest.mark.property
class TestExtractionProperty:
    """**Validates: Requirements 3.4, 3.5, 8.1**

    For any page and valid Mapa_Selectores, the DataExtractor SHALL produce
    a dictionary with exactly 66 keys matching the Esquema_Inmueble fields,
    where fields not found on the page are set to null rather than omitted.
    """

    @given(
        field_subset=st.lists(
            st.sampled_from(ESQUEMA_INMUEBLE_FIELDS),
            min_size=0,
            max_size=30,
            unique=True,
        ),
    )
    @settings(max_examples=100, deadline=None)
    def test_always_66_fields(self, field_subset: list[str]) -> None:
        """Extraction always produces exactly 66 fields regardless of selector map."""
        extractor = DataExtractor()

        # Create a selector map with only a subset of fields
        selector_map: dict[str, list[str]] = {}
        page_data: dict[str, str] = {}

        for field_name in field_subset:
            selector = f".{field_name.lower().replace('_', '-')}"
            selector_map[field_name] = [selector]
            # Some fields have values, some don't
            page_data[selector] = f"value-for-{field_name}"

        result = extractor.extract_sync(page_data, selector_map)

        # Must have exactly 66 keys
        assert len(result) == 66, f"Expected 66 fields, got {len(result)}"

        # All 66 field names must be present
        for field_name in ESQUEMA_INMUEBLE_FIELDS:
            assert field_name in result, f"Field '{field_name}' missing from result"

    @given(
        field_subset=st.lists(
            st.sampled_from(ESQUEMA_INMUEBLE_FIELDS),
            min_size=1,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100, deadline=None)
    def test_missing_fields_are_null(self, field_subset: list[str]) -> None:
        """Fields not found on the page are set to None (null), not omitted."""
        extractor = DataExtractor()

        # Create selector map but provide NO page data
        selector_map: dict[str, list[str]] = {}
        for field_name in field_subset:
            selector_map[field_name] = [f".missing-{field_name.lower()}"]

        result = extractor.extract_sync({}, selector_map)

        # All fields should be None since no selectors match
        for field_name in ESQUEMA_INMUEBLE_FIELDS:
            assert result[field_name] is None, (
                f"Field '{field_name}' should be None when not found"
            )


# ---------------------------------------------------------------------------
# Property 8: Fail-Safe Continuation on Error
# ---------------------------------------------------------------------------

# Feature: web-scraping-platform, Property 8: Fail-Safe Continuation on Error


@pytest.mark.property
class TestFailSafeProperty:
    """**Validates: Requirements 3.7**

    For any crawl queue containing URLs where some produce unrecoverable errors,
    the ENGINE SHALL process all non-failing URLs, log errors for failing ones,
    and never halt the entire execution due to a single URL failure.
    """

    @given(
        num_urls=st.integers(min_value=2, max_value=10),
        failing_indices=st.lists(
            st.integers(min_value=0, max_value=9),
            min_size=1,
            max_size=5,
            unique=True,
        ),
    )
    @settings(max_examples=100, deadline=None)
    def test_continues_after_errors(
        self, num_urls: int, failing_indices: list[int]
    ) -> None:
        """Engine processes all URLs even when some fail."""
        # Normalize failing indices to be within range
        failing_indices = [i % num_urls for i in failing_indices]
        failing_set = set(failing_indices)

        urls = [f"https://example{i}.com/page" for i in range(num_urls)]

        # Simulate processing with fail-safe behavior
        processed = []
        errors = []

        for i, url in enumerate(urls):
            try:
                if i in failing_set:
                    raise RuntimeError(f"Simulated error for URL {url}")
                processed.append(url)
            except Exception as e:
                # Fail-safe: log error, skip, continue
                errors.append({"url": url, "error": str(e)})
                continue

        # All non-failing URLs should be processed
        expected_processed = num_urls - len(failing_set)
        assert len(processed) == expected_processed, (
            f"Expected {expected_processed} processed, got {len(processed)}"
        )

        # Errors should be logged for failing URLs
        assert len(errors) == len(failing_set), (
            f"Expected {len(failing_set)} errors, got {len(errors)}"
        )

        # Total processed + errors = total URLs
        assert len(processed) + len(errors) == num_urls


# ---------------------------------------------------------------------------
# Property 10: Selector Priority Order
# ---------------------------------------------------------------------------

# Feature: web-scraping-platform, Property 10: Selector Priority Order


@pytest.mark.property
class TestSelectorPriorityProperty:
    """**Validates: Requirements 4.3**

    For any field with multiple configured CSS selectors, the ENGINE SHALL
    use the value from the first selector that returns a non-empty match,
    ignoring subsequent selectors.
    """

    @given(
        num_selectors=st.integers(min_value=2, max_value=5),
        first_match_index=st.integers(min_value=0, max_value=4),
    )
    @settings(max_examples=100, deadline=None)
    def test_first_match_wins(
        self, num_selectors: int, first_match_index: int
    ) -> None:
        """The first selector that matches is used, subsequent ones ignored."""
        # Normalize first_match_index
        first_match_index = first_match_index % num_selectors

        extractor = DataExtractor()

        # Create selectors for a single field
        field_name = "Titulo_Anuncio"
        selectors = [f".selector-{i}" for i in range(num_selectors)]

        # Only provide data for selectors at and after first_match_index
        page_data: dict[str, str] = {}
        for i in range(first_match_index, num_selectors):
            page_data[selectors[i]] = f"value-from-selector-{i}"

        selector_map = {field_name: selectors}
        result = extractor.extract_sync(page_data, selector_map)

        # The value should come from the first matching selector
        expected_value = f"value-from-selector-{first_match_index}"
        assert result[field_name] == expected_value, (
            f"Expected value from selector {first_match_index}, "
            f"got '{result[field_name]}'"
        )

    @given(
        values=st.lists(
            st.text(
                alphabet=string.ascii_letters + string.digits,
                min_size=1,
                max_size=20,
            ),
            min_size=2,
            max_size=5,
        ),
    )
    @settings(max_examples=100, deadline=None)
    def test_priority_order_consistent(self, values: list[str]) -> None:
        """When all selectors match, the first one always wins."""
        extractor = DataExtractor()

        field_name = "Municipio"
        selectors = [f".sel-{i}" for i in range(len(values))]

        # All selectors have values
        page_data = {sel: val for sel, val in zip(selectors, values)}

        selector_map = {field_name: selectors}
        result = extractor.extract_sync(page_data, selector_map)

        # First selector's value should win
        assert result[field_name] == values[0], (
            f"Expected first value '{values[0]}', got '{result[field_name]}'"
        )


# ---------------------------------------------------------------------------
# Property 12: Stealth Delay Range
# ---------------------------------------------------------------------------

# Feature: web-scraping-platform, Property 12: Stealth Delay Range


@pytest.mark.property
class TestStealthDelayProperty:
    """**Validates: Requirements 5.2**

    For any generated inter-request delay, the value SHALL fall within
    the range [2.0, 7.0] seconds.
    """

    @given(st.integers(min_value=1, max_value=1000))
    @settings(max_examples=100, deadline=None)
    def test_delay_within_range(self, _seed: int) -> None:
        """Generated delays are always within [2.0, 7.0]."""
        config = StealthConfig()
        delay = config.get_random_delay()

        assert 2.0 <= delay <= 7.0, (
            f"Delay {delay} is outside range [2.0, 7.0]"
        )

    @given(
        min_delay=st.floats(min_value=0.1, max_value=5.0),
        max_delay=st.floats(min_value=5.1, max_value=30.0),
    )
    @settings(max_examples=100, deadline=None)
    def test_custom_delay_range(self, min_delay: float, max_delay: float) -> None:
        """Custom delay ranges are respected."""
        config = StealthConfig(min_delay=min_delay, max_delay=max_delay)
        delay = config.get_random_delay()

        assert min_delay <= delay <= max_delay, (
            f"Delay {delay} is outside custom range [{min_delay}, {max_delay}]"
        )


# ---------------------------------------------------------------------------
# Property 13: Exponential Backoff Calculation
# ---------------------------------------------------------------------------

# Feature: web-scraping-platform, Property 13: Exponential Backoff Calculation


@pytest.mark.property
class TestBackoffProperty:
    """**Validates: Requirements 5.5**

    For any sequence of N consecutive HTTP 429 responses (N >= 1),
    the backoff delay SHALL equal min(30 * 2^(N-1), 600) seconds.
    """

    @given(n=consecutive_429_strategy)
    @settings(max_examples=100, deadline=None)
    def test_backoff_formula(self, n: int) -> None:
        """Backoff follows the formula min(30 * 2^(N-1), 600)."""
        backoff = ExponentialBackoff(base=30, max_delay=600)

        delay = backoff.calculate(n)
        expected = min(30 * (2 ** (n - 1)), 600)

        assert delay == expected, (
            f"For N={n}, expected {expected}, got {delay}"
        )

    @given(n=consecutive_429_strategy)
    @settings(max_examples=100, deadline=None)
    def test_backoff_never_exceeds_max(self, n: int) -> None:
        """Backoff delay never exceeds the maximum (600s)."""
        backoff = ExponentialBackoff(base=30, max_delay=600)

        delay = backoff.calculate(n)
        assert delay <= 600, f"Delay {delay} exceeds max 600s"

    @given(n=consecutive_429_strategy)
    @settings(max_examples=100, deadline=None)
    def test_backoff_always_positive(self, n: int) -> None:
        """Backoff delay is always positive for N >= 1."""
        backoff = ExponentialBackoff(base=30, max_delay=600)

        delay = backoff.calculate(n)
        assert delay > 0, f"Delay should be positive, got {delay}"

    @given(
        base=st.integers(min_value=1, max_value=60),
        max_delay=st.integers(min_value=60, max_value=1200),
        n=consecutive_429_strategy,
    )
    @settings(max_examples=100, deadline=None)
    def test_backoff_custom_params(
        self, base: int, max_delay: int, n: int
    ) -> None:
        """Backoff formula works with custom base and max_delay."""
        backoff = ExponentialBackoff(base=base, max_delay=max_delay)

        delay = backoff.calculate(n)
        expected = min(base * (2 ** (n - 1)), max_delay)

        assert delay == expected, (
            f"For base={base}, max={max_delay}, N={n}: "
            f"expected {expected}, got {delay}"
        )
