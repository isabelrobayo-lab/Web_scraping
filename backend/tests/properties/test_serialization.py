"""Property-based tests for serialization round-trip (Property 18)
and deserialization robustness (Property 19).

**Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

Tests that:
- Serializing then deserializing produces equivalent record (round-trip)
- Extra fields are ignored with warning
- Missing required fields return descriptive error
"""

# Feature: web-scraping-platform, Property 18: Serialization Round-Trip
# Feature: web-scraping-platform, Property 19: Deserialization Robustness

import json
import string
from datetime import datetime

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from app.data_logic.serializer import (
    ALL_FIELDS,
    BOOLEAN_FIELDS,
    DATE_FIELDS,
    INTEGER_FIELDS,
    NUMERIC_FIELDS,
    REQUIRED_FIELDS,
    Serializer,
    SerializationError,
)


serializer = Serializer()


# ---------------------------------------------------------------------------
# Strategies for generating valid EsquemaInmueble records
# ---------------------------------------------------------------------------

# String fields (non-required)
optional_string = st.one_of(st.none(), st.text(min_size=1, max_size=50))

# Required string fields (never None)
required_string = st.text(
    alphabet=string.ascii_letters + string.digits + "-_.",
    min_size=1,
    max_size=30,
)

# Optional numeric values
optional_numeric = st.one_of(
    st.none(),
    st.floats(min_value=-1e8, max_value=1e8, allow_nan=False, allow_infinity=False),
)

# Optional integer values
optional_integer = st.one_of(
    st.none(),
    st.integers(min_value=0, max_value=1000),
)

# Optional boolean values
optional_boolean = st.one_of(st.none(), st.booleans())

# Optional datetime values
optional_datetime = st.one_of(
    st.none(),
    st.datetimes(
        min_value=datetime(2000, 1, 1),
        max_value=datetime(2030, 12, 31),
    ),
)


@st.composite
def esquema_inmueble_record(draw):
    """Generate a valid EsquemaInmueble record dictionary with all 66 fields."""
    record = {}

    for field_name in ALL_FIELDS:
        if field_name == "Id_Interno":
            record[field_name] = draw(st.one_of(st.none(), st.integers(min_value=1, max_value=999999)))
        elif field_name in REQUIRED_FIELDS:
            record[field_name] = draw(required_string)
        elif field_name in DATE_FIELDS:
            record[field_name] = draw(optional_datetime)
        elif field_name in BOOLEAN_FIELDS:
            record[field_name] = draw(optional_boolean)
        elif field_name in INTEGER_FIELDS:
            record[field_name] = draw(optional_integer)
        elif field_name in NUMERIC_FIELDS:
            record[field_name] = draw(optional_numeric)
        else:
            # String fields
            record[field_name] = draw(optional_string)

    return record


# Extra field names that are NOT in ALL_FIELDS
extra_field_names = st.text(
    alphabet=string.ascii_lowercase,
    min_size=5,
    max_size=15,
).filter(lambda x: x not in set(ALL_FIELDS))


# ---------------------------------------------------------------------------
# Property 18: Serialization Round-Trip
# ---------------------------------------------------------------------------


class TestSerializationRoundTrip:
    """Property 18: serialize then deserialize produces equivalent record."""

    @settings(max_examples=100, deadline=None)
    @given(record=esquema_inmueble_record())
    def test_round_trip_preserves_all_fields(self, record: dict):
        """Serializing to JSON and deserializing back produces equivalent record."""
        json_str = serializer.to_json(record)
        restored = serializer.from_json(json_str)

        # All 66 fields must be present
        assert len(restored) == len(ALL_FIELDS)

        for field_name in ALL_FIELDS:
            original = record.get(field_name)
            result = restored.get(field_name)

            if original is None:
                assert result is None, f"Field {field_name}: expected None, got {result}"
            elif isinstance(original, datetime):
                # Dates are restored from ISO string
                assert isinstance(result, datetime), f"Field {field_name}: expected datetime"
                assert result == original, f"Field {field_name}: {result} != {original}"
            elif isinstance(original, bool):
                assert result == original, f"Field {field_name}: {result} != {original}"
            elif isinstance(original, int) and field_name in INTEGER_FIELDS:
                assert result == original, f"Field {field_name}: {result} != {original}"
            elif isinstance(original, (int, float)) and field_name in NUMERIC_FIELDS:
                assert isinstance(result, float), f"Field {field_name}: expected float"
                assert abs(result - original) < 1e-6, f"Field {field_name}: {result} != {original}"
            elif field_name == "Id_Interno" and original is not None:
                assert result == original, f"Field {field_name}: {result} != {original}"
            else:
                # String comparison
                assert str(result) == str(original), f"Field {field_name}: '{result}' != '{original}'"

    @settings(max_examples=100, deadline=None)
    @given(record=esquema_inmueble_record())
    def test_json_output_has_66_fields(self, record: dict):
        """Serialized JSON always contains exactly 66 fields."""
        json_str = serializer.to_json(record)
        parsed = json.loads(json_str)
        assert len(parsed) == 66

    @settings(max_examples=100, deadline=None)
    @given(record=esquema_inmueble_record())
    def test_nulls_preserved_in_json(self, record: dict):
        """Null values are explicitly present in JSON output (not omitted)."""
        json_str = serializer.to_json(record)
        parsed = json.loads(json_str)

        for field_name in ALL_FIELDS:
            assert field_name in parsed, f"Field {field_name} missing from JSON output"


# ---------------------------------------------------------------------------
# Property 19: Deserialization Robustness
# ---------------------------------------------------------------------------


class TestDeserializationRobustness:
    """Property 19: extra fields ignored, missing required fields error."""

    @settings(max_examples=100, deadline=None)
    @given(
        record=esquema_inmueble_record(),
        extra_key=extra_field_names,
        extra_value=st.text(min_size=1, max_size=20),
    )
    def test_extra_fields_ignored(self, record: dict, extra_key: str, extra_value: str):
        """Extra fields not in EsquemaInmueble are ignored during deserialization."""
        # Ensure extra_key is truly not in ALL_FIELDS
        assume(extra_key not in set(ALL_FIELDS))

        json_str = serializer.to_json(record)
        parsed = json.loads(json_str)

        # Add extra field
        parsed[extra_key] = extra_value
        modified_json = json.dumps(parsed, ensure_ascii=False)

        # Should succeed without error
        restored = serializer.from_json(modified_json)

        # Extra field should NOT be in the result
        assert extra_key not in restored

        # All 66 standard fields should still be present
        assert len(restored) == len(ALL_FIELDS)

    @settings(max_examples=100, deadline=None)
    @given(record=esquema_inmueble_record())
    def test_missing_codigo_inmueble_raises_error(self, record: dict):
        """Missing Codigo_Inmueble raises SerializationError."""
        json_str = serializer.to_json(record)
        parsed = json.loads(json_str)

        # Remove required field
        parsed["Codigo_Inmueble"] = None
        modified_json = json.dumps(parsed, ensure_ascii=False)

        with pytest.raises(SerializationError) as exc_info:
            serializer.from_json(modified_json)

        assert "Codigo_Inmueble" in str(exc_info.value)
        assert "Codigo_Inmueble" in exc_info.value.missing_fields

    @settings(max_examples=100, deadline=None)
    @given(record=esquema_inmueble_record())
    def test_missing_sitio_origen_raises_error(self, record: dict):
        """Missing Sitio_Origen raises SerializationError."""
        json_str = serializer.to_json(record)
        parsed = json.loads(json_str)

        # Remove required field
        parsed["Sitio_Origen"] = None
        modified_json = json.dumps(parsed, ensure_ascii=False)

        with pytest.raises(SerializationError) as exc_info:
            serializer.from_json(modified_json)

        assert "Sitio_Origen" in str(exc_info.value)
        assert "Sitio_Origen" in exc_info.value.missing_fields

    @settings(max_examples=100, deadline=None)
    @given(record=esquema_inmueble_record())
    def test_missing_both_required_fields_raises_error(self, record: dict):
        """Missing both required fields raises error listing both."""
        json_str = serializer.to_json(record)
        parsed = json.loads(json_str)

        # Remove both required fields
        parsed["Codigo_Inmueble"] = None
        parsed["Sitio_Origen"] = None
        modified_json = json.dumps(parsed, ensure_ascii=False)

        with pytest.raises(SerializationError) as exc_info:
            serializer.from_json(modified_json)

        assert "Codigo_Inmueble" in exc_info.value.missing_fields
        assert "Sitio_Origen" in exc_info.value.missing_fields
