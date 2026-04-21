"""Pydantic schemas for Configuracion_Scraping CRUD operations.

Provides request/response models with validation for URL, depth range,
cron expressions, and operation/execution modes.
"""

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.configs.cron_utils import validate_cron_expression


class TipoOperacion(str, Enum):
    """Allowed operation types for scraping configurations."""

    VENTA = "Venta"
    ARRIENDO = "Arriendo"


class ModoEjecucion(str, Enum):
    """Execution mode for scraping configurations."""

    MANUAL = "Manual"
    PROGRAMADO = "Programado"


class ConfigCreate(BaseModel):
    """Schema for creating a new scraping configuration.

    Validates:
    - url_base: must be a well-formed HTTP or HTTPS URL
    - profundidad_navegacion: integer between 1 and 10
    - cron_expression: required when modo_ejecucion is Programado
    """

    url_base: Annotated[str, Field(max_length=2048)]
    profundidad_navegacion: Annotated[int, Field(ge=1, le=10)]
    tipo_operacion: TipoOperacion
    modo_ejecucion: ModoEjecucion
    cron_expression: str | None = None

    @field_validator("url_base")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that url_base is a well-formed HTTP or HTTPS URL."""
        import re

        pattern = re.compile(
            r"^https?://"
            r"[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?"
            r"(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*"
            r"\.[a-zA-Z]{2,}"
            r"(:\d{1,5})?"
            r"(/[^\s]*)?$"
        )
        if not pattern.match(v):
            raise ValueError(
                "URL debe ser una URL HTTP o HTTPS válida "
                "(ej: https://www.ejemplo.com)"
            )
        return v

    @field_validator("cron_expression")
    @classmethod
    def validate_cron(cls, v: str | None) -> str | None:
        """Validate cron expression syntax if provided."""
        if v is not None:
            validate_cron_expression(v)
        return v

    @model_validator(mode="after")
    def cron_required_when_programado(self) -> "ConfigCreate":
        """Ensure cron_expression is provided when modo_ejecucion is Programado."""
        if self.modo_ejecucion == ModoEjecucion.PROGRAMADO:
            if not self.cron_expression:
                raise ValueError(
                    "cron_expression es requerido cuando modo_ejecucion es 'Programado'"
                )
        elif self.modo_ejecucion == ModoEjecucion.MANUAL:
            # Clear cron_expression for manual mode
            self.cron_expression = None
        return self


class ConfigUpdate(BaseModel):
    """Schema for updating an existing scraping configuration.

    All fields are optional — only provided fields will be updated.
    """

    url_base: Annotated[str, Field(max_length=2048)] | None = None
    profundidad_navegacion: Annotated[int, Field(ge=1, le=10)] | None = None
    tipo_operacion: TipoOperacion | None = None
    modo_ejecucion: ModoEjecucion | None = None
    cron_expression: str | None = None

    @field_validator("url_base")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        """Validate URL if provided."""
        if v is None:
            return v
        import re

        pattern = re.compile(
            r"^https?://"
            r"[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?"
            r"(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*"
            r"\.[a-zA-Z]{2,}"
            r"(:\d{1,5})?"
            r"(/[^\s]*)?$"
        )
        if not pattern.match(v):
            raise ValueError(
                "URL debe ser una URL HTTP o HTTPS válida "
                "(ej: https://www.ejemplo.com)"
            )
        return v

    @field_validator("cron_expression")
    @classmethod
    def validate_cron(cls, v: str | None) -> str | None:
        """Validate cron expression syntax if provided."""
        if v is not None:
            validate_cron_expression(v)
        return v

    @model_validator(mode="after")
    def cron_required_when_programado(self) -> "ConfigUpdate":
        """Ensure cron_expression is provided when switching to Programado."""
        if self.modo_ejecucion == ModoEjecucion.PROGRAMADO:
            if not self.cron_expression:
                raise ValueError(
                    "cron_expression es requerido cuando modo_ejecucion es 'Programado'"
                )
        elif self.modo_ejecucion == ModoEjecucion.MANUAL:
            self.cron_expression = None
        return self


class ConfigResponse(BaseModel):
    """Schema for returning a scraping configuration."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    url_base: str
    profundidad_navegacion: int
    tipo_operacion: str
    modo_ejecucion: str
    cron_expression: str | None = None
    cron_preview: str | None = None
    active: bool
    created_at: datetime
    updated_at: datetime
    last_execution_at: datetime | None = None


class PaginatedConfigResponse(BaseModel):
    """Paginated list response for configurations."""

    items: list[ConfigResponse]
    total: int
    page: int
    pages: int
