# ADR 003: Playwright para tests E2E

## Estado

Aceptado

## Contexto

El workspace es **agnóstico** y soporta tests E2E para cualquier plataforma web. Se necesita un framework que cubra tests E2E y auditoría de consola, con configuración por producto (URLs desde `Workspace/config/platforms.json`).

## Opciones consideradas

1. **Cypress** — Popular para E2E en navegador, menos adecuado para tests de API pura
2. **Puppeteer** — Bajo nivel, sin abstracciones de testing
3. **Playwright** — API unificada para navegador y API, multi-browser, screenshots, traces

## Decisión

Se eligió **Playwright** porque:

- Soporta `page` (navegador) y `request` (API) en el mismo framework
- El script de auditoría (`audit-console-errors.js`) usa Playwright (Firefox) para capturar errores de consola
- Traces y screenshots en fallos facilitan el debugging
- Integración con CI (reporter `github`)
- baseURL y rutas configurables por plataforma vía `get-platform-config.js`

## Consecuencias

- Un solo framework para E2E y auditoría
- Comando único: `npm test`
- Base URL y smokePaths desde `Workspace/config/platforms.json` (o env `BASE_URL`)
