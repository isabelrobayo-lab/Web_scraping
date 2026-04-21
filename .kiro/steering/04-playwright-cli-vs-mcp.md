---
inclusion: fileMatch
fileMatchPattern: ['**/tests/**', 'playwright.config.js', '**/*.spec.js']
---
# Playwright: CLI vs MCP

## Regla de priorización

| Caso | Usar | Motivo |
|------|------|--------|
| Smoke tests, regresión, validación CI | `npm test` o `npx playwright test` | Tests deterministas, eficientes en tokens |
| Explorar una página sin test escrito | Playwright MCP (si está configurado) | Interacción iterativa, snapshot de accesibilidad |
| Verificar ad hoc en conversación | Playwright MCP | El agente navega y verifica en tiempo real |

## Instrucciones

1. **Tests conocidos** (smoke.spec.js, miniverse.spec.js, etc.): Ejecutar siempre vía CLI (`npm test`).
2. **Exploración nueva** (ej. "verifica que /login carga correctamente"): Usar Playwright MCP si está disponible; si no, sugerir escribir un test y ejecutarlo con CLI.
3. **Guardian / criterio de éxito**: El reporte final debe basarse en `npm test`; MCP no sustituye la validación con tests versionados.
