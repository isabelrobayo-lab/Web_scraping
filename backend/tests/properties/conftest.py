"""Shared Hypothesis strategies for property-based tests.

Provides reusable strategies for generating domain objects used across
multiple property test modules (configurations, selectors, properties, etc.).
"""

import string

from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Primitive strategies
# ---------------------------------------------------------------------------

# Valid HTTP/HTTPS URLs
urls = st.from_regex(
    r"https?://[a-z][a-z0-9\-]{1,20}\.[a-z]{2,6}(/[a-z0-9\-]{1,15}){0,4}",
    fullmatch=True,
)

# Valid CSS selectors (simplified subset for testing)
css_selectors = st.from_regex(
    r"[a-z][a-z0-9\-]*(\.[a-z][a-z0-9\-]*){0,2}(#[a-z][a-z0-9\-]*)?",
    fullmatch=True,
)

# Sitio origen identifiers
sitio_origen_strategy = st.from_regex(
    r"[a-z][a-z0-9\-]{2,20}\.(com|co|net|org)",
    fullmatch=True,
)

# Codigo inmueble identifiers
codigo_inmueble_strategy = st.text(
    alphabet=string.ascii_uppercase + string.digits,
    min_size=4,
    max_size=20,
)

# Profundidad de navegacion (1-10)
profundidad_strategy = st.integers(min_value=1, max_value=10)

# Tipo de operacion
tipo_operacion_strategy = st.sampled_from(["Venta", "Arriendo"])

# Modo de ejecucion
modo_ejecucion_strategy = st.sampled_from(["Manual", "Programado"])

# ---------------------------------------------------------------------------
# Numeric field strategies
# ---------------------------------------------------------------------------

# Prices (positive decimals)
precio_strategy = st.floats(
    min_value=0.01,
    max_value=99_999_999.99,
    allow_nan=False,
    allow_infinity=False,
)

# Area in square meters
area_strategy = st.floats(
    min_value=1.0,
    max_value=100_000.0,
    allow_nan=False,
    allow_infinity=False,
)

# Geographic coordinates
latitud_strategy = st.floats(
    min_value=-90.0,
    max_value=90.0,
    allow_nan=False,
    allow_infinity=False,
)

longitud_strategy = st.floats(
    min_value=-180.0,
    max_value=180.0,
    allow_nan=False,
    allow_infinity=False,
)

# Estrato (1-6 for Colombian real estate)
estrato_strategy = st.integers(min_value=1, max_value=6)

# ---------------------------------------------------------------------------
# Boolean field strategies (raw string values as extracted from HTML)
# ---------------------------------------------------------------------------

boolean_string_strategy = st.sampled_from([
    "Si", "No", "True", "False", "true", "false", "1", "0",
    "si", "no", "Sí", "sí", "YES", "NO",
])

# ---------------------------------------------------------------------------
# Date field strategies (common formats found in real estate sites)
# ---------------------------------------------------------------------------

date_string_strategy = st.sampled_from([
    "2024-01-15",
    "15/01/2024",
    "01-15-2024",
    "2024-03-22T10:30:00",
    "22 Mar 2024",
    "2023-12-31",
])

# ---------------------------------------------------------------------------
# Cron expression strategies (valid subset)
# ---------------------------------------------------------------------------

cron_minute = st.sampled_from(["0", "15", "30", "45", "*/5", "*/10", "*/15"])
cron_hour = st.sampled_from(["*", "0", "6", "12", "18", "*/2", "*/6"])
cron_dom = st.sampled_from(["*", "1", "15", "*/7"])
cron_month = st.sampled_from(["*", "1", "6", "*/3"])
cron_dow = st.sampled_from(["*", "0", "1", "1-5", "0,6"])


@st.composite
def cron_expression_strategy(draw):
    """Generate valid 5-field cron expressions."""
    minute = draw(cron_minute)
    hour = draw(cron_hour)
    dom = draw(cron_dom)
    month = draw(cron_month)
    dow = draw(cron_dow)
    return f"{minute} {hour} {dom} {month} {dow}"
