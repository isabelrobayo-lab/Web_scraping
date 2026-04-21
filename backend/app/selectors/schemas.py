"""Pydantic schemas for Mapa_Selectores management.

Provides request/response models with CSS selector syntax validation
using the cssselect library.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def validate_css_selector(selector: str) -> str:
    """Validate that a string is a syntactically valid CSS selector.

    Uses cssselect to parse the selector. Raises ValueError if invalid.
    """
    from cssselect import GenericTranslator, SelectorSyntaxError

    selector = selector.strip()
    if not selector:
        raise ValueError("CSS selector cannot be empty")

    try:
        GenericTranslator().css_to_xpath(selector)
    except SelectorSyntaxError as e:
        raise ValueError(f"Invalid CSS selector '{selector}': {e}")

    return selector


class SelectorMapUpdate(BaseModel):
    """Schema for creating or updating a selector map.

    mappings: dict where keys are field names and values are lists of CSS selectors.
    Each CSS selector is validated for syntactic correctness.
    """

    mappings: dict[str, list[str]] = Field(
        ...,
        description="Mapping of field names to lists of CSS selectors",
        min_length=1,
    )

    @field_validator("mappings")
    @classmethod
    def validate_mappings(cls, v: dict[str, list[str]]) -> dict[str, list[str]]:
        """Validate that all CSS selectors in mappings are syntactically valid."""
        for field_name, selectors in v.items():
            if not field_name.strip():
                raise ValueError("Field name cannot be empty")
            if not selectors:
                raise ValueError(
                    f"Field '{field_name}' must have at least one CSS selector"
                )
            for selector in selectors:
                validate_css_selector(selector)
        return v


class SelectorMapResponse(BaseModel):
    """Schema for returning a selector map."""

    model_config = ConfigDict(from_attributes=True)

    sitio_origen: str
    version: int
    mappings: dict[str, list[str]]
    created_at: datetime
