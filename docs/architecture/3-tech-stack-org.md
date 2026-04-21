# Ecosistema Tecnológico de la Organización

## Herramientas de Negocio

- [cite_start]**Gestión:** Jira (via MCP atlassian)[cite: 1462, 1476].
- [cite_start]**Monitoreo:** Datadog (via MCP datadog)[cite: 1886].

## Estándares de Git

- [cite_start]**Uso:** Solo análisis de PRs y lectura de historial[cite: 155, 4012].
- **Prohibido:** No realizar commits ni pushes automáticos en fase de análisis.

## Estándares de Calidad

- [cite_start]**E2E:** Playwright (`@playwright/test`); comando habitual: `npm test` o `npx playwright test`[cite: 323, 324].
- **Unitarios:** Vitest en `tests/unit/` (`npm run test:unit`).
- **HTTP (repo):** `supertest` está en `package.json` como dependencia de desarrollo; no hay suite de API obligatoria documentada aún.
