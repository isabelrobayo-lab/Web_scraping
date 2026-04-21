"""Property-based tests for field type parsing (Property 17).

**Validates: Requirements 8.3, 8.4, 8.5, 8.6**

Tests that:
- parse_numeric extracts numbers or returns None
- parse_boolean interprets Si/No/True/False/1/0 or returns None
- parse_date parses dates or returns None
- Latitud validated in range [-90, 90]
- Longitud validated in range [-180, 180]
"""

# Feature: web-scraping-platform, Property 17: Field Type Parsing

from datetime import datetime

from hypothesis import given, settings
from hypothesis import strategies as st

from app.data_logic.field_validator import FieldValidator


validator = FieldValidator()


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Strings that contain at least one digit (should parse to a number)
numeric_strings = st.from_regex(r"[\$\u20ac]?\d[\d,]*\.?\d*\s?[a-z]*", fullmatch=True)

# Strings with no digits at all (should fail to parse)
non_numeric_strings = st.from_regex(r"[a-zA-Z]{2,10}", fullmatch=True)

# Valid boolean string values
true_strings = st.sampled_from(["Si", "Sí", "si", "sí", "Yes", "yes", "YES", "True", "true", "1"])
false_strings = st.sampled_from(["No", "no", "NO", "False", "false", "0"])
valid_boolean_strings = st.one_of(true_strings, false_strings)

# Invalid boolean strings
invalid_boolean_strings = st.sampled_from(["maybe", "unknown", "perhaps", "quizas", "abc", "xyz"])

# Valid date strings in supported formats
valid_date_strings = st.sampled_from([
    "2024-01-15",
    "2023-12-31",
    "15/01/2024",
    "31/12/2023",
    "01-15-2024",
    "2024-03-22T10:30:00",
    "22 Mar 2024",
    "Jan 15, 2024",
    "Dec 31, 2023",
])

# Invalid date strings
invalid_date_strings = st.sampled_from([
    "invalid",
    "not-a-date",
    "abc123",
    "99/99/9999",
    "tomorrow",
])

# Latitude values: valid [-90, 90]
valid_latitudes = st.floats(min_value=-90.0, max_value=90.0, allow_nan=False, allow_infinity=False)
invalid_latitudes = st.one_of(
    st.floats(min_value=90.01, max_value=1000.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=-1000.0, max_value=-90.01, allow_nan=False, allow_infinity=False),
)

# Longitude values: valid [-180, 180]
valid_longitudes = st.floats(min_value=-180.0, max_value=180.0, allow_nan=False, allow_infinity=False)
invalid_longitudes = st.one_of(
    st.floats(min_value=180.01, max_value=1000.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=-1000.0, max_value=-180.01, allow_nan=False, allow_infinity=False),
)


# ---------------------------------------------------------------------------
# Property Tests
# ---------------------------------------------------------------------------


class TestParseNumeric:
    """Property tests for parse_numeric."""

    @settings(max_examples=100)
    @given(value=numeric_strings)
    def test_numeric_strings_return_float_or_none(self, value: str):
        """parse_numeric always returns a float or None for any string input."""
        result = validator.parse_numeric(value)
        assert result is None or isinstance(result, float)

    @settings(max_examples=100)
    @given(value=non_numeric_strings)
    def test_non_numeric_strings_return_none(self, value: str):
        """Strings without digits return None."""
        result = validator.parse_numeric(value)
        assert result is None

    @settings(max_examples=100)
    @given(n=st.floats(min_value=-1e9, max_value=1e9, allow_nan=False, allow_infinity=False))
    def test_plain_number_strings_parse_correctly(self, n: float):
        """A plain number formatted as string should parse back to that number."""
        # Format without thousands separator
        value = f"{n:.2f}"
        result = validator.parse_numeric(value)
        assert result is not None
        assert abs(result - n) < 0.01


class TestParseBoolean:
    """Property tests for parse_boolean."""

    @settings(max_examples=100)
    @given(value=true_strings)
    def test_true_values_return_true(self, value: str):
        """Recognized true strings always return True."""
        result = validator.parse_boolean(value)
        assert result is True

    @settings(max_examples=100)
    @given(value=false_strings)
    def test_false_values_return_false(self, value: str):
        """Recognized false strings always return False."""
        result = validator.parse_boolean(value)
        assert result is False

    @settings(max_examples=100)
    @given(value=invalid_boolean_strings)
    def test_unrecognizable_values_return_none(self, value: str):
        """Unrecognizable boolean strings return None."""
        result = validator.parse_boolean(value)
        assert result is None


class TestParseDate:
    """Property tests for parse_date."""

    @settings(max_examples=100)
    @given(value=valid_date_strings)
    def test_valid_dates_return_datetime(self, value: str):
        """Valid date strings always return a datetime instance."""
        result = validator.parse_date(value)
        assert isinstance(result, datetime)

    @settings(max_examples=100)
    @given(value=invalid_date_strings)
    def test_invalid_dates_return_none(self, value: str):
        """Invalid date strings always return None."""
        result = validator.parse_date(value)
        assert result is None


class TestCoordinateValidation:
    """Property tests for latitude and longitude range validation."""

    @settings(max_examples=100)
    @given(lat=valid_latitudes)
    def test_valid_latitude_accepted(self, lat: float):
        """Latitudes in [-90, 90] are accepted by validation."""
        raw_data = {"Latitud": lat}
        result = validator.validate(raw_data)
        assert result.data["Latitud"] == lat

    @settings(max_examples=100)
    @given(lat=invalid_latitudes)
    def test_invalid_latitude_set_to_none(self, lat: float):
        """Latitudes outside [-90, 90] are set to None with warning."""
        raw_data = {"Latitud": lat}
        result = validator.validate(raw_data)
        assert result.data["Latitud"] is None
        assert any("Latitud" in w for w in result.warnings)

    @settings(max_examples=100)
    @given(lon=valid_longitudes)
    def test_valid_longitude_accepted(self, lon: float):
        """Longitudes in [-180, 180] are accepted by validation."""
        raw_data = {"Longitud": lon}
        result = validator.validate(raw_data)
        assert result.data["Longitud"] == lon

    @settings(max_examples=100)
    @given(lon=invalid_longitudes)
    def test_invalid_longitude_set_to_none(self, lon: float):
        """Longitudes outside [-180, 180] are set to None with warning."""
        raw_data = {"Longitud": lon}
        result = validator.validate(raw_data)
        assert result.data["Longitud"] is None
        assert any("Longitud" in w for w in result.warnings)
