FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (libpq for PostgreSQL, deps for Playwright Chromium)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
        libcups2 libdrm2 libdbus-1-3 libxkbcommon0 \
        libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 \
        libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 \
        libwayland-client0 && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies using pip (from pyproject.toml via pip)
COPY pyproject.toml ./
RUN pip install --no-cache-dir poetry==1.8.4 && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-root --no-interaction && \
    pip uninstall -y poetry

# Install Playwright Chromium browser
RUN playwright install chromium

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

ENV PYTHONPATH="/app" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
