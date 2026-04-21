"""Export generation service for CSV, Excel, and JSON formats.

Uses Pandas + openpyxl for data transformation and file generation.
Supports both synchronous (small datasets) and asynchronous (large datasets)
export workflows.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


def ensure_export_dir() -> Path:
    """Ensure the export directory exists and return its path."""
    export_dir = Path(settings.EXPORT_DIR)
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def generate_export(
    records: list[dict[str, Any]],
    export_format: str,
    export_id: str,
) -> tuple[str, int]:
    """Generate an export file in the specified format.

    Args:
        records: List of property dictionaries to export.
        export_format: One of 'csv', 'excel', 'json'.
        export_id: Unique export identifier for the filename.

    Returns:
        Tuple of (file_path, record_count).

    Raises:
        ValueError: If export_format is not supported.
    """
    import pandas as pd

    if export_format not in ("csv", "excel", "json"):
        raise ValueError(f"Formato de exportación no soportado: {export_format}")

    export_dir = ensure_export_dir()
    record_count = len(records)

    if record_count == 0:
        df = pd.DataFrame()
    else:
        df = pd.DataFrame(records)
        # Convert Decimal columns to float for serialization
        for col in df.columns:
            if df[col].dtype == object:
                try:
                    df[col] = df[col].apply(
                        lambda x: float(x) if hasattr(x, "as_tuple") else x
                    )
                except (ValueError, TypeError):
                    pass

    if export_format == "csv":
        file_name = f"{export_id}.csv"
        file_path = export_dir / file_name
        df.to_csv(file_path, index=False, encoding="utf-8")

    elif export_format == "excel":
        file_name = f"{export_id}.xlsx"
        file_path = export_dir / file_name
        df.to_excel(file_path, index=False, engine="openpyxl")

    elif export_format == "json":
        file_name = f"{export_id}.json"
        file_path = export_dir / file_name
        df.to_json(file_path, orient="records", force_ascii=False, indent=2)

    logger.info(
        "Export file generated",
        export_id=export_id,
        format=export_format,
        record_count=record_count,
        file_path=str(file_path),
    )

    return str(file_path), record_count


def get_content_type(export_format: str) -> str:
    """Return the MIME content type for the given export format."""
    content_types = {
        "csv": "text/csv",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "json": "application/json",
    }
    return content_types.get(export_format, "application/octet-stream")


def get_file_extension(export_format: str) -> str:
    """Return the file extension for the given export format."""
    extensions = {"csv": ".csv", "excel": ".xlsx", "json": ".json"}
    return extensions.get(export_format, "")
