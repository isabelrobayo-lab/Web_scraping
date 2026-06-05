"""Seed script: Configuración de scraping + Mapa de selectores para fincaraiz.com.co.

Crea:
1. ConfiguracionScraping para Venta de apartamentos en Bogotá
2. ConfiguracionScraping para Arriendo de apartamentos en Bogotá
3. MapaSelectores v1 para sitio_origen = "fincaraiz.com.co"

Uso:
    cd backend
    python -m scripts.seed_fincaraiz

Selectores validados contra el DOM real de fincaraiz.com.co (2026-04-22).
Tecnología del sitio: Next.js + Ant Design (antd).
Clases estables: prefijo lc- (listing card), property- (detail), CO- (amenidades).
"""
import asyncio
import sys

sys.path.insert(0, "/app")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


# ===================================================================
# MAPA DE SELECTORES CSS — fincaraiz.com.co (v1)
# ===================================================================
# Validado contra DOM real el 2026-04-22 por Guardian (Playwright).
#
# LISTADO: /venta/apartamentos/{ciudad}/{departamento}
#   - Cards: .listingCard con enlace a.lc-data
#   - Paginación: /venta/paginaX
#   - Proyectos: URL contiene /proyectos-vivienda/ (filtrar)
#   - Individuales: URL contiene /apartamento-en-venta-en- o similar
#
# DETALLE: /apartamento-en-venta-en-{barrio}-{ciudad}/{id_numerico}
#   - Hero: h1.property-title, .property-price-tag
#   - Tipología: .typology-item-container (3 items: habs, baños, m²)
#   - Ficha técnica: .technical-sheet .ant-row (pares label-valor)
#   - Amenidades: .CO-facility-batch .ant-typography
#   - Contacto: .owner-name-text (teléfono oculto tras formulario)
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

FINCARAIZ_SELECTOR_MAP: dict[str, list[str]] = {
    # --- IDENTIFICACIÓN ---
    # El código se extrae del último segmento numérico de la URL del detalle
    "Codigo_Inmueble": [
        "url_regex:/(\\d+)$",
    ],
    # --- CARACTERÍSTICAS PRINCIPALES (selectores directos) ---
    "Titulo_Anuncio": [
        "h1.property-title",
        ".lc-title",
        "h1",
    ],
    "Operacion": [
        ".operation_type",
    ],
    "Tipo_Inmueble": [
        "label:Tipo de Inmueble",
    ],
    "Habitaciones": [
        ".typology-item-container:nth-child(1)",
        ".lc-typologyTag__item:nth-child(1)",
        "label:Habitaciones",
    ],
    "Banos": [
        ".typology-item-container:nth-child(2)",
        ".lc-typologyTag__item:nth-child(2)",
        "label:Baños",
    ],
    "Metros_Totales": [
        ".typology-item-container:nth-child(3)",
        ".lc-typologyTag__item:nth-child(3)",
    ],
    "Estacionamiento": [
        "label:Parqueaderos",
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
        "label:Piso N",
        "label:Piso",
    ],
    # --- PRECIOS ---
    "Precio_Local": [
        ".property-price-tag .main-price",
        ".main-price",
    ],
    "Simbolo_Moneda": [
        "fixed:$",
    ],
    "Administracion_Valor": [
        ".commonExpenses",
        "label:Administración",
        "label:Administracion",
    ],
    # --- UBICACIÓN ---
    "Municipio": [
        ".property-location-tag p:first-child",
        ".lc-location",
    ],
    "Barrio": [
        ".property-location-tag p:last-child",
    ],
    "Sector": [
        ".location-header",
    ],
    # --- CONTACTO ---
    "Dueno_Anuncio": [
        ".owner-name-text",
        ".lc-owner-name",
    ],
    "Tipo_Publicador": [
        ".owner-info .ant-typography",
    ],
    # Teléfono NO disponible en DOM público (oculto tras formulario)
    # Correo NO disponible en DOM público
    # --- DESCRIPCIÓN ---
    "Descripcion_Anuncio": [
        ".property-description",
        ".lc-description",
    ],
    # --- URLs e IMÁGENES ---
    "Url_Anuncio": [
        "meta:og:url",
    ],
    "Url_Imagen_Principal": [
        "meta:og:image",
        ".property-cover-gallery img",
    ],
    # --- AMENIDADES (booleanos) ---
    # Buscar texto exacto en .CO-facility-batch .ant-typography
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
        "amenity:Baño auxiliar",
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
        "amenity:Recepción",
    ],
    "Circuito_Cerrado": [
        "amenity:Circuito cerrado",
        "amenity:CCTV",
    ],
    "Estacionamiento_Visita": [
        "amenity:Parqueadero visitantes",
        "amenity:Parqueadero visita",
    ],
    "Cocina_Americana": [
        "amenity:Cocina americana",
        "amenity:Cocina integral",
        "amenity:Cocina tipo americano",
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
        "fixed:fincaraiz.com.co",
    ],
}


async def main() -> None:
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
                == "https://www.fincaraiz.com.co/venta/apartamentos/bogota/bogota-dc"
            )
        )
        existing_venta = result.scalar_one_or_none()

        if existing_venta:
            print("[SKIP] Config Venta Bogota ya existe (id=%s)" % existing_venta.id)
        else:
            config_venta = ConfiguracionScraping(
                url_base=(
                    "https://www.fincaraiz.com.co"
                    "/venta/apartamentos/bogota/bogota-dc"
                ),
                profundidad_navegacion=3,
                tipo_operacion="Venta",
                modo_ejecucion="Manual",
                cron_expression=None,
                include_patterns=None,
                exclude_patterns=[
                    r"/proyectos-vivienda/",
                    r"/proyecto-nuevo/",
                    r"/login",
                    r"/registro",
                    r"/favoritos",
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
                == "https://www.fincaraiz.com.co/arriendo/apartamentos/bogota/bogota-dc"
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
                    "https://www.fincaraiz.com.co"
                    "/arriendo/apartamentos/bogota/bogota-dc"
                ),
                profundidad_navegacion=3,
                tipo_operacion="Arriendo",
                modo_ejecucion="Manual",
                cron_expression=None,
                include_patterns=None,
                exclude_patterns=[
                    r"/proyectos-vivienda/",
                    r"/proyecto-nuevo/",
                    r"/login",
                    r"/registro",
                    r"/favoritos",
                ],
                active=True,
            )
            db.add(config_arriendo)
            print("[OK] Config Arriendo Bogota creada")

        # ---------------------------------------------------------------
        # 3. Mapa de Selectores para fincaraiz.com.co
        # ---------------------------------------------------------------
        result = await db.execute(
            select(MapaSelectores)
            .where(MapaSelectores.sitio_origen == "fincaraiz.com.co")
            .order_by(MapaSelectores.version.desc())
            .limit(1)
        )
        existing_map = result.scalar_one_or_none()

        if existing_map:
            print(
                "[SKIP] Mapa selectores fincaraiz.com.co ya existe (v%s)"
                % existing_map.version
            )
        else:
            selector_map = MapaSelectores(
                sitio_origen="fincaraiz.com.co",
                version=1,
                mappings=FINCARAIZ_SELECTOR_MAP,
            )
            db.add(selector_map)
            print("[OK] Mapa selectores fincaraiz.com.co v1 creado")

        await db.commit()

    await engine.dispose()
    print("\n[DONE] Seed fincaraiz.com.co completado.")


if __name__ == "__main__":
    asyncio.run(main())
