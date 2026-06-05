"""Seed script: Configuración de scraping + Mapa de selectores para properati.com.co.

Crea:
1. ConfiguracionScraping para Venta de apartamentos en Bogotá
2. ConfiguracionScraping para Arriendo de apartamentos en Bogotá
3. MapaSelectores v1 para sitio_origen = "properati.com.co"

Uso:
    cd backend
    python -m scripts.seed_properati

Selectores basados en el DOM del listado de properati.com.co (2026-04-22).
Tecnología del sitio: React (SPA).
NOTA: El DOM de detalle NO pudo fetchearse directamente (SPA requiere JS).
Los selectores de detalle tienen selector_status="pending" y serán descubiertos
automáticamente por el auto_discover_selectors (Celery task) vía Playwright.
"""
import asyncio
import sys

sys.path.insert(0, "/app")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


# ===================================================================
# MAPA DE SELECTORES CSS — properati.com.co (v1)
# ===================================================================
# Basado en DOM del listado fetcheado el 2026-04-22.
# DETALLE: No se pudo fetchear (SPA). Selectores son estimaciones
# basadas en la estructura del listado + convenciones React comunes.
# El auto_discover_selectors los refinará vía Playwright.
#
# LISTADO: /s/bogota-d-c-colombia/apartamento/venta
#   - Cards: elementos con título, precio, ubicación, características
#   - Paginación: /s/bogota-d-c-colombia/apartamento/venta/{pageNumber}
#   - Filtrar: excluir /proyecto/, /asistente-personal, /blog
#
# DETALLE: /detalle/{id-complejo}
#   - Ejemplo: /detalle/14032-32-b4ab-b4da75ac7f81-19c25e9-9d16-7338
#   - Código: segmento ID después de /detalle/
#
# TIPOS DE SELECTOR:
#   - "css:..." o sin prefijo → Selector CSS directo (text_content)
#   - "label:..." → Buscar en ficha técnica por label (lógica especial)
#   - "amenity:..." → Buscar en lista de amenidades por texto
#   - "url_regex:..." → Extraer del URL con regex
#   - "meta:..." → Extraer content de meta tag
#   - "fixed:..." → Valor fijo hardcoded
#
# El DataExtractor debe interpretar estos prefijos.
# ===================================================================

PROPERATI_SELECTOR_MAP: dict[str, list[str]] = {
    # --- IDENTIFICACIÓN ---
    # El código se extrae del segmento después de /detalle/ en la URL
    # Ejemplo: /detalle/14032-32-b4ab-b4da75ac7f81-19c25e9-9d16-7338
    "Codigo_Inmueble": [
        "url_regex:/detalle/([^/]+)$",
    ],
    # --- CARACTERÍSTICAS PRINCIPALES ---
    "Titulo_Anuncio": [
        "h1",
        "[data-testid='property-title']",
        ".property-title",
        ".listing-title",
    ],
    "Operacion": [
        "label:Tipo de operación",
        "label:Operación",
    ],
    "Tipo_Inmueble": [
        "label:Tipo de propiedad",
        "label:Tipo Inmueble",
    ],
    "Habitaciones": [
        "[data-testid='bedrooms']",
        ".property-features :has-text('habitaciones')",
        "label:Habitaciones",
    ],
    "Banos": [
        "[data-testid='bathrooms']",
        ".property-features :has-text('baños')",
        "label:Baños",
    ],
    "Metros_Totales": [
        "[data-testid='area']",
        ".property-features :has-text('m²')",
        "label:Superficie total",
    ],
    "Estacionamiento": [
        "[data-testid='parking']",
        ".property-features :has-text('Parqueadero')",
        "label:Parqueaderos",
        "label:Estacionamientos",
    ],
    "Area_Privada": [
        "label:Área Privada",
        "label:Superficie cubierta",
    ],
    "Area_Construida": [
        "label:Área Construida",
        "label:Superficie total",
    ],
    "Estrato": [
        "label:Estrato",
    ],
    "Antiguedad_Detalle": [
        "label:Antigüedad",
        "label:Año de construcción",
    ],
    "Piso_Propiedad": [
        "label:Piso",
        "label:Número de piso",
    ],
    # --- PRECIOS ---
    "Precio_Local": [
        "[data-testid='price']",
        ".price",
        ".listing-price",
    ],
    "Simbolo_Moneda": [
        "fixed:$",
    ],
    "Administracion_Valor": [
        "label:Administración",
        "label:Expensas",
    ],
    # --- UBICACIÓN ---
    "Municipio": [
        "label:Ciudad",
        ".location-city",
    ],
    "Barrio": [
        "label:Barrio",
        ".location-neighborhood",
    ],
    "Sector": [
        "label:Zona",
        "label:Localidad",
        ".location-zone",
    ],
    # --- CONTACTO ---
    "Dueno_Anuncio": [
        "[data-testid='publisher-name']",
        ".publisher-name",
        ".advertiser-info .name",
    ],
    "Tipo_Publicador": [
        "[data-testid='publisher-type']",
        ".publisher-type",
    ],
    # --- DESCRIPCIÓN ---
    "Descripcion_Anuncio": [
        "[data-testid='description']",
        ".property-description",
        ".description-text",
    ],
    # --- URLs e IMÁGENES ---
    "Url_Anuncio": [
        "meta:og:url",
    ],
    "Url_Imagen_Principal": [
        "meta:og:image",
        "[data-testid='gallery'] img",
        ".gallery img:first-child",
    ],
    # --- AMENIDADES (booleanos) ---
    "Tiene_Ascensores": [
        "amenity:Ascensor",
    ],
    "Tiene_Balcones": [
        "amenity:Balcón",
        "amenity:Balcon",
    ],
    "Tiene_Seguridad": [
        "amenity:Vigilancia",
        "amenity:Seguridad",
    ],
    "Tiene_Bodega_Deposito": [
        "amenity:Depósito",
        "amenity:Deposito",
        "amenity:Bodega",
    ],
    "Tiene_Terraza": [
        "amenity:Terraza",
    ],
    "Cuarto_Servicio": [
        "amenity:Cuarto de servicio",
    ],
    "Bano_Servicio": [
        "amenity:Baño de servicio",
    ],
    "Tiene_Calefaccion": [
        "amenity:Calefacción",
        "amenity:Calentador",
    ],
    "Tiene_Alarma": [
        "amenity:Alarma",
    ],
    "Acceso_Controlado": [
        "amenity:Portería",
        "amenity:Porteria",
    ],
    "Circuito_Cerrado": [
        "amenity:Circuito cerrado",
        "amenity:CCTV",
    ],
    "Estacionamiento_Visita": [
        "amenity:Parqueadero visitantes",
    ],
    "Cocina_Americana": [
        "amenity:Cocina americana",
        "amenity:Cocina integral",
    ],
    "Tiene_Gimnasio": [
        "amenity:Gimnasio",
    ],
    "Tiene_BBQ": [
        "amenity:BBQ",
        "amenity:Zona BBQ",
    ],
    "Tiene_Piscina": [
        "amenity:Piscina",
    ],
    "En_Conjunto_Residencial": [
        "amenity:Conjunto cerrado",
        "amenity:Conjunto residencial",
    ],
    # --- CAMPOS DERIVADOS POR EL ENGINE ---
    "Sitio_Origen": [
        "fixed:properati.com.co",
    ],
}


async def main() -> None:
    """Seed properati.com.co configurations and selector map."""
    from app.core.config import settings
    from app.core.database import Base
    from app.models.configuracion_scraping import ConfiguracionScraping
    from app.models.mapa_selectores import MapaSelectores

    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as db:
        # ---------------------------------------------------------------
        # 1. Configuración: Venta — Apartamentos Bogotá
        # ---------------------------------------------------------------
        result = await db.execute(
            select(ConfiguracionScraping).where(
                ConfiguracionScraping.url_base
                == "https://www.properati.com.co/s/bogota-d-c-colombia/apartamento/venta"
            )
        )
        existing_venta = result.scalar_one_or_none()

        if existing_venta:
            print("[SKIP] Config Venta Bogota ya existe (id=%s)" % existing_venta.id)
        else:
            config_venta = ConfiguracionScraping(
                url_base=(
                    "https://www.properati.com.co"
                    "/s/bogota-d-c-colombia/apartamento/venta"
                ),
                profundidad_navegacion=3,
                tipo_operacion="Venta",
                modo_ejecucion="Manual",
                cron_expression=None,
                include_patterns=None,
                exclude_patterns=[
                    r"/proyecto/",
                    r"/asistente-personal",
                    r"/blog",
                    r"/s/.*/(casa|apartaestudio|local|oficina|bodega|lote|finca)/",
                ],
                selector_status="pending",
                active=True,
            )
            db.add(config_venta)
            print("[OK] Config Venta Bogota creada")

        # ---------------------------------------------------------------
        # 2. Configuración: Arriendo — Apartamentos Bogotá
        # ---------------------------------------------------------------
        result = await db.execute(
            select(ConfiguracionScraping).where(
                ConfiguracionScraping.url_base
                == "https://www.properati.com.co/s/bogota-d-c-colombia/apartamento/arriendo"
            )
        )
        existing_arriendo = result.scalar_one_or_none()

        if existing_arriendo:
            print(
                "[SKIP] Config Arriendo Bogota ya existe (id=%s)"
                % existing_arriendo.id
            )
        else:
            config_arriendo = ConfiguracionScraping(
                url_base=(
                    "https://www.properati.com.co"
                    "/s/bogota-d-c-colombia/apartamento/arriendo"
                ),
                profundidad_navegacion=3,
                tipo_operacion="Arriendo",
                modo_ejecucion="Manual",
                cron_expression=None,
                include_patterns=None,
                exclude_patterns=[
                    r"/proyecto/",
                    r"/asistente-personal",
                    r"/blog",
                    r"/s/.*/(casa|apartaestudio|local|oficina|bodega|lote|finca)/",
                ],
                selector_status="pending",
                active=True,
            )
            db.add(config_arriendo)
            print("[OK] Config Arriendo Bogota creada")

        # ---------------------------------------------------------------
        # 3. Mapa de Selectores para properati.com.co
        # ---------------------------------------------------------------
        result = await db.execute(
            select(MapaSelectores)
            .where(MapaSelectores.sitio_origen == "properati.com.co")
            .order_by(MapaSelectores.version.desc())
            .limit(1)
        )
        existing_map = result.scalar_one_or_none()

        if existing_map:
            print(
                "[SKIP] Mapa selectores properati.com.co ya existe (v%s)"
                % existing_map.version
            )
        else:
            selector_map = MapaSelectores(
                sitio_origen="properati.com.co",
                version=1,
                mappings=PROPERATI_SELECTOR_MAP,
            )
            db.add(selector_map)
            print("[OK] Mapa selectores properati.com.co v1 creado")

        await db.commit()

    await engine.dispose()
    print("\n[DONE] Seed properati.com.co completado.")


if __name__ == "__main__":
    asyncio.run(main())
