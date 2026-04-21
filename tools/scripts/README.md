# Scripts de automatización

Scripts reutilizables para el proyecto.

## Scripts disponibles

| Script | Descripción |
|--------|-------------|
| `create-cursor-automation.js` | Automatiza la creación de la automation Datadog→Cursor en cursor.com/automations (Playwright) |
| `regenerate-diagram-html.js` | Regenera los `.html` de `docs/diagrams/` desde los `.mmd` (codifica Mermaid para Draw.io) |
| `generate-cycle-report-html.js` | Genera reporte HTML del ciclo de desarrollo |
| `analyze-cycle-time.js` | Analiza tiempo por fase del ciclo (Jira); genera MD en `Workspace/reports/` |
| `deploy-pages.js` | Regenera reportes y copia a `docs/` para GitHub Pages |

## Uso

### Regenerar diagramas HTML

```bash
npm run diagrams:regenerate-html
```

Lee cada `.mmd` en `docs/diagrams/`, comprime el Mermaid (deflate+base64) y genera los `.html` que redirigen a Draw.io con el diagrama precargado. Útil tras actualizar diagramas.

### Crear automatización en Cursor (Playwright)

```bash
npm run automation:create-cursor
```

Abre el navegador, navega a cursor.com/automations e intenta crear la automatización "Datadog Alert → Plan + HU". La primera vez puede pedir login manual; el estado se guarda en `Workspace/playwright/cursor-browser-state/` para reutilizar la sesión. Si la UI de Cursor ha cambiado, el script puede pausar para completar manualmente. Ver `docs/runbook/automation-datadog-alert.md`.

### Reporte de ciclo

```bash
npm run report:cycle
```

Genera el reporte HTML en `Workspace/reports/analisis-ciclo-desarrollo.html`. Lee datos de `docs/data/jira-cycle-2025.json`.

### Análisis de tiempo por fase

```bash
node tools/scripts/analyze-cycle-time.js [ruta-json]
```

Analiza HUs de Jira y genera `Workspace/reports/analisis-ciclo-desarrollo.md`. Por defecto usa `docs/data/jira-cycle-2025.json`.

### Desplegar a GitHub Pages

```bash
npm run deploy:pages
```

Regenera los reportes y los copia a `docs/` para que GitHub Pages los sirva.
