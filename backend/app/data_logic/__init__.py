"""DATA_LOGIC module — validation, upsert, serialization, error logging, and deactivation."""

from app.data_logic.deactivation_detector import DeactivationDetector
from app.data_logic.error_logger import ErrorLogger, ExecutionSummary, ScrapingError
from app.data_logic.field_validator import FieldValidator
from app.data_logic.serializer import Serializer
from app.data_logic.upsert_service import UpsertAction, UpsertResult, UpsertService

__all__ = [
    "DeactivationDetector",
    "ErrorLogger",
    "ExecutionSummary",
    "FieldValidator",
    "ScrapingError",
    "Serializer",
    "UpsertAction",
    "UpsertResult",
    "UpsertService",
]
