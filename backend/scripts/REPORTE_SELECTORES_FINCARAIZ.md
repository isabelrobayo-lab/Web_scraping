# Reporte de Validación de Selectores CSS — fincaraiz.com.co

**Fecha:** 2026-04-22  
**Agente:** Guardian (QA Specialist)  
**URL Listado:** `https://www.fincaraiz.com.co/venta/apartamentos/bogota/bogota-dc`  
**URL Detalle:** `https://www.fincaraiz.com.co/apartamento-en-venta-en-san-cipriano-bogota/193612101`  
**Estado:** Sin CAPTCHA, sin bloqueo. Sitio accesible con Playwright.

---

## 1. Hallazgos Generales

### Tecnologia del sitio
- **Framework:** Next.js (SPA con SSR)
- **UI Library:** Ant Design (antd) — clases `ant-row`, `ant-col`, `ant-space`, `ant-typography`
- **CSS:** Clases estables con prefijo `lc-` (listing card), `property-` (detail), `pd-` (property detail)
- **Clases dinamicas:** Prefijo `jsx-XXXXXXXXX` (CSS-in-JS de Next.js) — NO usar como selectores, son inestables
- **Data attributes:** NO existen `data-test`, `data-id`, `data-listing-id` ni ningun `data-*` util en el DOM

### Estructura de URLs
- **Listado:** `/venta/apartamentos/{ciudad}/{departamento}` con paginacion `/paginaX`
- **Detalle individual:** `/apartamento-en-venta-en-{barrio}-{ciudad}/{id_numerico}`
- **Proyecto vivienda:** `/proyectos-vivienda/{nombre-proyecto}/{id_numerico}`

### Observaciones importantes
1. Las primeras 1-2 paginas del listado son 100% proyectos de vivienda (patrocinados). Los inmuebles individuales aparecen a partir de la pagina 2-3.
2. Los proyectos de vivienda tienen URLs con `/proyectos-vivienda/` y los individuales con `/apartamento-en-venta-en-` o `/apartamento-en-arriendo-en-`.
3. El telefono de contacto NO esta visible en el DOM — requiere completar un formulario para revelarlo.
4. Algunos campos muestran "Preguntale!" cuando el anunciante no proporciono el dato.

---

## 2. Selectores CSS REALES — Pagina de LISTADO

### Contenedor de cards
```
.listingCard                          -> Cada card de propiedad (proyecto o individual)
.listingCard.isBigCard                -> Card grande (formato destacado)
.listingCard.isSuperHighlighted       -> Card super destacada
```

### Enlace a detalle
```
.listingCard a.lc-data                -> Link principal que envuelve los datos de la card
.listingCard a.lc-data[href]          -> Atributo href con la URL del detalle
```

### Precio
```
.listingCard .lc-price                -> Contenedor de precio
.listingCard .main-price              -> Precio principal (ej: "$ 220.000.000" o "Desde $ 262.310.000")
.listingCard .commonExpenses          -> Valor de administracion (ej: "+ $ 180.000 admin")
```

### Tipo de inmueble y ubicacion
```
.listingCard .lc-location             -> Tipo + ubicacion (ej: "Apartamento en Bogota, Bogota, d.c.")
```

### Habitaciones, Banos, Area (tipologia)
```
.listingCard .lc-typologyContainer    -> Contenedor de tipologia
.listingCard .lc-typologyTag          -> Contenedor de items de tipologia
.listingCard .lc-typologyTag__item    -> Cada item individual (3 items: Habs, Banos, m2)
  - Primer item: Habitaciones (ej: "3 Habs.")
  - Segundo item: Banos (ej: "2 Banos")
  - Tercer item: Area (ej: "70 m2")
```

### Titulo del anuncio
```
.listingCard h2                       -> Titulo del anuncio en la card
.listingCard .lc-title                -> Titulo (misma referencia, clase CSS)
```

### Descripcion
```
.listingCard .lc-description          -> Texto de descripcion (truncado en listado)
```

### Anunciante
```
.listingCard .lc-owner-name           -> Nombre del anunciante/inmobiliaria
.listingCard .property-owner-logo img -> Logo del anunciante (atributo alt = nombre)
```

### Tags/Badges
```
.listingCard .lc-tags.tag-isHighlightedBlack  -> Badge "Destacado"
.listingCard .lc-tags.tag-isProject           -> Badge de proyecto
```

### Galeria de imagenes
```
.listingCard .cardImageGallery        -> Contenedor de galeria
.listingCard .emblaGalleryCarousel    -> Carrusel de imagenes
.listingCard .gallery-image           -> Cada imagen de la galeria
```

### Paginacion
```
nav[aria-label="Pagination"]          -> Contenedor de paginacion
nav[aria-label="Pagination"] li a     -> Links de paginas
```

---

## 3. Selectores CSS REALES — Pagina de DETALLE

### Titulo del anuncio
```
h1.property-title                     -> Titulo principal (ej: "Apartamento en Venta en San cipriano, Bogota")
```

### Precio
```
.property-price-tag                   -> Contenedor completo de precio
.property-price-tag .main-price       -> Precio principal (ej: "$ 220.000.000")
.property-price-tag .operation_type   -> Tipo de operacion (ej: "Precio de Venta")
.property-price-tag .commonExpenses   -> Administracion (ej: "+ $ 180.000 administracion")
```

### Tipologia (Habitaciones, Banos, Area)
```
.property-typology-tag                -> Contenedor de tipologia
.typology-item-container              -> Cada item (3 items: Habs, Banos, m2)
  - Primer .typology-item-container: Habitaciones
  - Segundo .typology-item-container: Banos
  - Tercer .typology-item-container: Area total
```

### Ubicacion
```
.property-location-tag                -> Contenedor de ubicacion (municipio + barrio)
.property-location-tag p:first-child  -> Municipio (ej: "Suba, Bogota, d.c.")
.property-location-tag p:last-child   -> Barrio (ej: "San cipriano, Bogota, d.c.")
.location-header                      -> Header con ubicacion principal y asociadas
```

### Codigo del inmueble
```
No hay clase CSS estable. El codigo esta en un span con clase jsx-XXXXXXX (dinamica).
Alternativa: extraer del URL (ultimo segmento numerico: /193612101)
Alternativa: buscar texto "Codigo Fincaraiz:" en la pagina
```

### Ficha Tecnica (Detalles de la Propiedad)
La seccion `.technical-sheet` contiene pares label-valor en filas `.ant-row.ant-row-space-between`:

```
Estructura de cada fila:
.ant-row.ant-row-space-between
  +-- .ant-col (label: "Estrato")
  +-- .ant-col.dots (separador visual)
  +-- .ant-col (valor: "3")
```

**Labels disponibles en la ficha tecnica:**

| Label en DOM | Campo Esquema | Valor ejemplo |
|---|---|---|
| Tipo de Inmueble | Tipo_Inmueble | "Apartamento" |
| Estado | (no mapeado) | "Buen estado" |
| Banos | Banos | "2" |
| Antiguedad | Antiguedad_Detalle | "mas de 30 anos" |
| Habitaciones | Habitaciones | "3" |
| Parqueaderos | Estacionamiento | "Preguntale!" |
| Area Construida | Area_Construida | "70 m2" |
| Area Privada | Area_Privada | "70 m2" |
| Estrato | Estrato | "Preguntale!" |
| Administracion | Administracion_Valor | "$ 180.000" |
| Piso N | Piso_Propiedad | "Preguntale!" |
| Cantidad de Pisos | (no mapeado) | "Preguntale!" |
| Acepta permuta | (no mapeado) | "Preguntale!" |
| Remodelado | (no mapeado) | "Preguntale!" |

### Descripcion
```
.property-description                 -> Texto completo de descripcion
.description-container                -> Contenedor padre (incluye titulo "Descripcion")
```

### Amenidades / Comodidades
```
.property-facilities                  -> Contenedor de comodidades
.CO-facility-batch                    -> Cada amenidad individual
.CO-facility-batch .ant-typography    -> Texto de la amenidad (ej: "Balcon", "Cocina Integral")
```

### Contacto / Anunciante
```
.owner-info                           -> Contenedor de info del anunciante
.owner-name-text                      -> Nombre del anunciante (ej: "Tu360Inmobiliario")
.property-owner-logo img              -> Logo del anunciante
.property-information-request         -> Seccion completa de contacto
.contact-form                         -> Formulario de contacto
```

### Galeria de imagenes
```
.property-cover-gallery img           -> Imagenes de la galeria
meta[property="og:image"]             -> URL de imagen principal (meta tag)
```

### URLs y Meta
```
link[rel="canonical"]                 -> URL canonica del anuncio
meta[property="og:url"]               -> URL del anuncio (Open Graph)
meta[property="og:image"]             -> Imagen principal (Open Graph)
```

### Mapa
```
.property-local-information-map       -> Contenedor del mapa
.leaflet-container                    -> Mapa Leaflet (lat/lng disponible via JS)
```

---

## 4. Mapeo: Selectores REALES a Esquema de 66 campos

### Campos con selector directo (13 campos)

| Campo Esquema | Pagina | Selector CSS Real |
|---|---|---|
| Titulo_Anuncio | Detalle | `h1.property-title` |
| Titulo_Anuncio | Listado | `.listingCard h2`, `.lc-title` |
| Precio_Local | Detalle | `.property-price-tag .main-price` |
| Precio_Local | Listado | `.main-price` |
| Administracion_Valor | Ambas | `.commonExpenses` |
| Operacion | Detalle | `.operation_type` |
| Habitaciones | Detalle | `.typology-item-container:nth-child(1)` |
| Habitaciones | Listado | `.lc-typologyTag__item:nth-child(1)` |
| Banos | Detalle | `.typology-item-container:nth-child(2)` |
| Banos | Listado | `.lc-typologyTag__item:nth-child(2)` |
| Metros_Totales | Detalle | `.typology-item-container:nth-child(3)` |
| Metros_Totales | Listado | `.lc-typologyTag__item:nth-child(3)` |
| Descripcion_Anuncio | Detalle | `.property-description` |
| Descripcion_Anuncio | Listado | `.lc-description` |
| Dueno_Anuncio | Detalle | `.owner-name-text` |
| Dueno_Anuncio | Listado | `.lc-owner-name` |
| Municipio | Detalle | `.property-location-tag p:first-child` |
| Barrio | Detalle | `.property-location-tag p:last-child` |
| Url_Anuncio | Detalle | `link[rel='canonical']` (attr href) |
| Url_Imagen_Principal | Detalle | `meta[property='og:image']` (attr content) |

### Campos con logica especial requerida (32 campos)

| Campo | Estrategia |
|---|---|
| Codigo_Inmueble | Extraer de URL (regex `/(\d+)$`) o texto "Codigo Fincaraiz:" |
| Tipo_Inmueble | Ficha tecnica label "Tipo de Inmueble" |
| Estacionamiento | Ficha tecnica label "Parqueaderos" |
| Area_Privada | Ficha tecnica label "Area Privada" |
| Area_Construida | Ficha tecnica label "Area Construida" |
| Estrato | Ficha tecnica label "Estrato" |
| Antiguedad_Detalle | Ficha tecnica label "Antiguedad" |
| Piso_Propiedad | Ficha tecnica label "Piso N" |
| Simbolo_Moneda | Extraer "$" del texto de precio |
| Tipo_Publicador | Parsear "Inmobiliaria Verificada" de `.owner-info` |
| Sector | Extraer de `.location-header` "Ubicaciones asociadas" |
| Latitud/Longitud | Extraer via JS del mapa Leaflet |
| Amenidades (17 campos) | Buscar texto en `.CO-facility-batch .ant-typography` |
| Fecha_Control | Timestamp del scraping |
| Fecha_Actualizacion | Timestamp del scraping |
| Estado_Activo | Presencia en listado = activo |
| Sitio_Origen | Hardcoded "fincaraiz.com.co" |

### Campos NO disponibles en el DOM (21 campos)

Telefono_Principal, Telefono_Opcional, Correo_Contacto, Tipo_Empresa,
Tipo_Estudio, Es_Loft, Fecha_Publicacion, Direccion, Fecha_Desactivacion,
Precio_USD, Precio_Bajo, Cambio_Precio_Valor, Glosa_Administracion,
Amoblado, Orientacion, Uso_Comercial, Rango_Antiguedad (derivable)

---

## 5. Recomendaciones para el Engine

### 5.1 Nuevo patron: extraccion de ficha tecnica (label-valor)
El DataExtractor actual solo soporta selectores CSS directos. Para la ficha tecnica se necesita:

```python
async def extract_technical_sheet(page) -> dict:
    rows = await page.query_selector_all('.technical-sheet .ant-row.ant-row-space-between')
    result = {}
    for row in rows:
        cols = await row.query_selector_all(':scope > .ant-col')
        if len(cols) == 3:
            label = (await cols[0].text_content()).strip().lstrip('* ')
            value = (await cols[2].text_content()).strip()
            if value != 'Preguntale!':
                result[label] = value
    return result
```

### 5.2 Nuevo patron: extraccion de amenidades
```python
async def extract_amenities(page) -> list[str]:
    batches = await page.query_selector_all('.CO-facility-batch .ant-typography')
    amenities = []
    for b in batches:
        text = (await b.text_content()).strip()
        if text and text != '*':
            amenities.append(text)
    return amenities
```

### 5.3 Diferenciacion proyecto vs individual
```python
def is_individual_property(url: str) -> bool:
    return '/proyectos-vivienda/' not in url
```

### 5.4 Extraccion de codigo del inmueble
```python
import re
code = re.search(r'/(\d+)$', url).group(1)
```

---

## 6. Resumen de Cobertura

| Categoria | Total | Selector directo | Logica especial | No disponible |
|---|---|---|---|---|
| Identificacion | 2 | 0 | 2 | 0 |
| Caracteristicas | 12 | 5 | 6 | 1 |
| Precios | 5 | 2 | 1 | 2 |
| Ubicacion | 6 | 2 | 2 | 2 |
| Contacto | 5 | 1 | 1 | 3 |
| Descripcion | 1 | 1 | 0 | 0 |
| URLs/Imagenes | 2 | 2 | 0 | 0 |
| Fechas | 4 | 0 | 2 | 2 |
| Amenidades (bool) | 17 | 0 | 17 | 0 |
| Otros | 12 | 0 | 1 | 11 |
| **TOTAL** | **66** | **13** | **32** | **21** |

### Conclusion
- **13 campos** se pueden extraer con selectores CSS directos (sin cambios al engine)
- **32 campos** requieren logica especial (ficha tecnica label-valor, amenidades por texto, extraccion de URL)
- **21 campos** no estan disponibles en el DOM publico de fincaraiz.com.co
- **El seed actual (seed_fincaraiz.py) tiene 0% de selectores funcionales** — todos los selectores data-test, data-id, clases como span.property-code, div.rooms, etc. NO existen en el DOM real
