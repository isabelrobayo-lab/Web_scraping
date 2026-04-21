"""SQLAlchemy models for the Plataforma Paramétrica de Web Scraping Inmobiliario.

All models use SQLAlchemy 2.0+ Mapped[] style annotations with async support.
"""

from app.models.usuario import Usuario
from app.models.configuracion_scraping import ConfiguracionScraping
from app.models.mapa_selectores import MapaSelectores
from app.models.tarea_scraping import TareaScraping
from app.models.esquema_inmueble import EsquemaInmueble
from app.models.log_error import LogError
from app.models.exportacion import Exportacion

__all__ = [
    "Usuario",
    "ConfiguracionScraping",
    "MapaSelectores",
    "TareaScraping",
    "EsquemaInmueble",
    "LogError",
    "Exportacion",
]
