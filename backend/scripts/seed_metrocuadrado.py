"""Seed script: Configuración de scraping + Mapa de selectores para metrocuadrado.com.

Crea:
1. ConfiguracionScraping para Venta de apartamentos en Bogotá
2. ConfiguracionScraping para Arriendo de apartamentos en Bogotá
3. MapaSelectores v1 para sitio_origen = "metrocuadrado.com"

Uso:
    cd backend
    python -m scripts.seed_metrocuadrado

Selectores basados en el DOM real de metrocuadrado.com (2026-04-22).
Tecnología del sitio: React/Next.js.
Clases estables: convenciones BEM y data-attributes de Next.js.
El auto_discover_selectors (Celery task) refinará estos selectores vía Playwright.
"""
import asyncio
import sys

sys.path.insert(0, "/app")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


# ===================================================================
# MAPA DE SELECTORES CSS — metrocuadrado.com (v1)
# ===================================================================
# Basado en DOM real fetcheado el 2026-04-22.
#
# LISTADO: /apartamentos/venta/bogota
#   - Cards: elementos de listado con enlaces a detalle
#   - Paginación: ?page=X o /page/X
#   - Filtrar: excluir /proyecto/, /proyectos/, /inmobiliaria/
#
# DETALLE: /inmueble/venta-apartamento-bogota-{barrio}-.../{CODIGO}
#   - Hero: h1 con "Apartamento En Venta, {BARRIO}"
#   - Precio: texto "$ 750.000.000"
#   - Tipología: "2 hab.", "2 bañ.", "2 par."
#   - Área: "Área Construida 90m²", "Área Privada 90m²"
#   - Ficha: "Estrato 4", "Antigüedad: Entre 0 y 5 años"
#   - Barrio: "Barrio común: LA SALLE CHAPINERO ALTO"
#   - Código: "Código: 2238-M3958545"
#   - Contacto: "ASOCIACION PROFESIONAL INMOBILIARIA API"
#
# TIPOS DE SELECTOR:
#   - "css:..." o sin prefijo → Selector CSS directo (text_content)
#   - "label:..." → Buscar en ficha técnica por label (lógica especial)
#   - "amenity:..." → Buscar en lista de amenidades/características por texto
#   - "url_regex:..." → Extraer del URL con regex
#   - "meta:..." → Extraer content de meta tag
#   - "fixed:..." → Valor fijo hardcoded
#
# El DataExtractor debe interpretar estos prefijos.
# ===================================================================

METROCUADRADO_SELECTOR_MAP: dict[str, list[str]] = {
    # --- IDENTIFICACIÓN ---
    # El código se extrae del último segmento de la URL del detalle
    # Ejemplo: /inmueble/venta-apartamento-bogota-.../2238-M3958545 → "2238-M3958545"
    "Codigo_Inmueble": [
        "url_regex:/([^/]+)$",
        "label:Código",
        "label:Codigo",
    ],
    # --- CARACTERÍSTICAS PRINCIPALES ---
    "Titulo_Anuncio": [
        "h1",
        "[data-testid='property-title']",
        ".property-title",
    ],
    "Operacion": [
        "label:Tipo de negocio",
        "label:Operación",
    ],
    "Tipo_Inmueble": [
        "label:Tipo de inmueble",
        "label:Tipo Inmueble",
    ],
    "Habitaciones": [
        "[data-testid='bedrooms']",
        ".features-item:has-text('hab')",
        "label:Habitaciones",
    ],
    "Banos": [
        "[data-testid='bathrooms']",
        ".features-item:has-text('bañ')",
        "label:Baños",
    ],
    "Metros_Totales": [
        "[data-testid='area']",
        ".features-item:has-text('m²')",
    ],
    "Estacionamiento": [
        "[data-testid='parking']",
        ".features-item:has-text('par')",
        "label:Parqueaderos",
        "label:Garajes",
    ],
    "Area_Privada": [
        "label:Área Privada",
        "label:Area Privada",
    ],
    "Area_Construida": [
        "label:Área Construida",
        "label:Area Construida",
    ],
    "Estrato": [
        "label:Estrato",
    ],
    "Antiguedad_Detalle": [
        "label:Antigüedad",
        "label:Antiguedad",
    ],
    "Piso_Propiedad": [
        "label:Número de piso",
        "label:Piso",
    ],
    # --- PRECIOS ---
    "Precio_Local": [
        "[data-testid='price']",
        ".price-container",
        "h2:has-text('$')",
    ],
    "Simbolo_Moneda": [
        "fixed:$",
    ],
    "Administracion_Valor": [
        "label:Administración",
        "label:Administracion",
        "label:Valor administración",
    ],
    # --- UBICACIÓN ---
    "Municipio": [
        "label:Ciudad",
        "label:Municipio",
    ],
    "Barrio": [
        "label:Barrio común",
        "label:Barrio",
    ],
    "Sector": [
        "label:Sector",
        "label:Localidad",
    ],
    # --- CONTACTO ---
    "Dueno_Anuncio": [
        "[data-testid='advertiser-name']",
        ".advertiser-name",
        ".contact-info .name",
    ],
    "Tipo_Publicador": [
        "[data-testid='advertiser-type']",
        ".advertiser-type",
    ],
    # --- DESCRIPCIÓN ---
    "Descripcion_Anuncio": [
        "[data-testid='description']",
        ".property-description",
        ".description-content",
    ],
    # --- URLs e IMÁGENES ---
    "Url_Anuncio": [
        "meta:og:url",
    ],
    "Url_Imagen_Principal": [
        "meta:og:image",
        "[data-testid='gallery'] img",
        ".gallery-container img:first-child",
    ],
    # --- AMENIDADES (booleanos) ---
    # Buscar texto en la lista de características del inmueble
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
        "amenity:Cuarto servicio",
    ],
    "Bano_Servicio": [
        "amenity:Baño de servicio",
        "amenity:Bano de servicio",
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
        "amenity:Parqueadero visita",
    ],
    "Parqueadero_Cubierto": [
        "amenity:Parqueadero cubierto",
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
        "fixed:metrocuadrado.com",
    ],
}


async def main() -> None:
    """Seed metrocuadrado.com configurations and selector map."""
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
                == "https://www.metrocuadrado.com/apartamentos/venta/bogota"
            )
        )
        existing_venta = result.scalar_one_or_none()

        if existing_venta:
            print("[SKIP] Config Venta Bogota ya existe (id=%s)" % existing_venta.id)
        else:
            config_venta = ConfiguracionScraping(
                url_base="https://www.metrocuadrado.com/apartamentos/venta/bogota",
                profundidad_navegacion=3,
                tipo_operacion="Venta",
                modo_ejecucion="Manual",
                cron_expression=None,
                include_patterns=None,
                exclude_patterns=[
                    r"/proyecto/",
                    r"/proyectos/",
                    r"/inmobiliaria/",
                    r"/constructoras/",
                    r"/login",
                    r"/registro",
                    r"/noticias/",
                    r"/blog/",
                ],
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
                == "https://www.metrocuadrado.com/apartamentos/arriendo/bogota"
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
                url_base="https://www.metrocuadrado.com/apartamentos/arriendo/bogota",
                profundidad_navegacion=3,
                tipo_operacion="Arriendo",
                modo_ejecucion="Manual",
                cron_expression=None,
                include_patterns=None,
                exclude_patterns=[
                    r"/proyecto/",
                    r"/proyectos/",
                    r"/inmobiliaria/",
                    r"/constructoras/",
                    r"/login",
                    r"/registro",
                    r"/noticias/",
                    r"/blog/",
                ],
                active=True,
            )
            db.add(config_arriendo)
            print("[OK] Config Arriendo Bogota creada")

        # ---------------------------------------------------------------
        # 3. Mapa de Selectores para metrocuadrado.com
        # ---------------------------------------------------------------
        result = await db.execute(
            select(MapaSelectores)
            .where(MapaSelectores.sitio_origen == "metrocuadrado.com")
            .order_by(MapaSelectores.version.desc())
            .limit(1)
        )
        existing_map = result.scalar_one_or_none()

        if existing_map:
            print(
                "[SKIP] Mapa selectores metrocuadrado.com ya existe (v%s)"
                % existing_map.version
            )
        else:
            selector_map = MapaSelectores(
                sitio_origen="metrocuadrado.com",
                version=1,
                mappings=METROCUADRADO_SELECTOR_MAP,
            )
            db.add(selector_map)
            print("[OK] Mapa selectores metrocuadrado.com v1 creado")

        await db.commit()

    await engine.dispose()
    print("\n[DONE] Seed metrocuadrado.com completado.")


if __name__ == "__main__":
    asyncio.run(main())
