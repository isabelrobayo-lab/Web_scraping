# Scraping Platform Backend

Backend API para la Plataforma Paramétrica de Web Scraping Inmobiliario.

## Stack Tecnológico

- **Python** 3.12+
- **FastAPI** 0.115+ (framework async)
- **Uvicorn** (ASGI server)
- **Poetry** 1.8+ (dependency management)
- **PostgreSQL** 15.4+ con SQLAlchemy 2.0+ async
- **Celery** + Redis (task queue)
- **Alembic** (database migrations)
- **pytest** 8.0+ (testing)

## Estructura del Proyecto

```
backend/
├── app/                  # Paquete principal de la aplicación
│   ├── __init__.py
│   └── main.py           # Entry point de FastAPI
├── tests/                # Tests
│   ├── __init__.py
│   └── test_health.py
├── alembic/              # Migraciones de base de datos
├── pyproject.toml        # Configuración Poetry y dependencias
└── README.md
```

## Instalación

```bash
# Instalar dependencias con Poetry
poetry install

# Activar el entorno virtual
poetry shell
```

## Ejecución

```bash
# Servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Tests

```bash
pytest
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/docs` | Documentación Swagger UI |
| GET | `/api/redoc` | Documentación ReDoc |
