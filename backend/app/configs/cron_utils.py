"""Cron expression validation and human-readable preview generation.

Uses croniter for syntax validation and cron-descriptor for
generating human-readable descriptions of cron schedules.
"""

from croniter import croniter
from cron_descriptor import get_description, Options


def validate_cron_expression(expression: str) -> str:
    """Validate a 5-field standard cron expression.

    Args:
        expression: A cron expression string (e.g., "0 3 * * *").

    Returns:
        The validated expression string.

    Raises:
        ValueError: If the expression is not a valid 5-field cron.
    """
    expression = expression.strip()
    parts = expression.split()
    if len(parts) != 5:
        raise ValueError(
            f"Expresión cron debe tener exactamente 5 campos "
            f"(minuto hora día_mes mes día_semana), se recibieron {len(parts)}"
        )
    if not croniter.is_valid(expression):
        raise ValueError(
            f"Expresión cron inválida: '{expression}'. "
            f"Formato esperado: minuto hora día_mes mes día_semana"
        )
    return expression


def get_cron_preview(expression: str) -> str:
    """Generate a human-readable preview of a cron expression.

    Args:
        expression: A valid 5-field cron expression.

    Returns:
        A human-readable description (e.g., "Every day at 3:00 AM").
        Returns a fallback message if description generation fails.
    """
    try:
        options = Options()
        options.use_24hour_time_format = False
        options.locale_code = "es_ES"
        description = get_description(expression, options)
        return description
    except Exception:
        # Fallback: try without locale
        try:
            description = get_description(expression)
            return description
        except Exception:
            return f"Programado: {expression}"
