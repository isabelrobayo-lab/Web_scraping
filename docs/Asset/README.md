# Asset – Plantillas de reportes para GitHub Pages

Esta carpeta contiene las plantillas reutilizables para los reportes HTML publicados en GitHub Pages (`docs/`).

## Estructura

| Archivo | Uso |
|---------|-----|
| `report-base.css` | Variables CSS, reset, tipografía y layout base. Cargar siempre primero. |
| `report-components.css` | Componentes: nav, header, sections, cards, tables, badges, footer. Para reportes de contenido. |
| `report-index.css` | Estilos del índice de reportes (`reportes.html`). Layout centrado con cards. |
| `template-report.html` | Plantilla HTML de referencia para reportes con contenido. |
| `template-report-index.html` | Plantilla HTML de referencia para el índice de reportes. |

## Uso en reportes HTML

### Reporte con contenido (ej. reporte ejecutivo, análisis ciclo)

```html
<link rel="stylesheet" href="Asset/report-base.css">
<link rel="stylesheet" href="Asset/report-components.css">
```

### Índice de reportes (reportes.html)

```html
<link rel="stylesheet" href="Asset/report-base.css">
<link rel="stylesheet" href="Asset/report-index.css">
```

## Rutas relativas

Los reportes HTML viven en `docs/`. La ruta a Asset es `Asset/` (mismo nivel que el HTML).

- `docs/reportes.html` → `Asset/report-base.css`
- `docs/index.html` → `Asset/report-base.css`

## Scripts generadores

El script `tools/scripts/generate-cycle-report-html.js` genera HTML con estilos inline. Para usar las plantillas CSS, se puede refactorizar para:

1. Incluir `<link rel="stylesheet" href="Asset/report-base.css">` y `report-components.css`
2. Eliminar los bloques `<style>` duplicados del HTML generado

Los archivos generados se copian a `docs/` con `npm run deploy:pages`, por lo que las rutas `Asset/` funcionan correctamente en GitHub Pages.

## Fuentes

Las plantillas usan **DM Sans** y **JetBrains Mono** desde Google Fonts. Los reportes deben incluir:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

## Referencia

- Runbook GitHub Pages: [docs/runbook/github-pages.md](../runbook/github-pages.md)
- Resumen del proyecto: [docs/resumen-proyecto.md](../resumen-proyecto.md)
