---
name: prueba-ui
description: Abre el navegador, comprueba el funcionamiento de la UI recién creada o modificada, y si falla corrige los errores y reintenta automáticamente. Usa Playwright CLI para tests E2E; Playwright MCP para exploración interactiva; Chrome DevTools MCP solo en este flujo E2E para rendimiento y depuración profunda.
---

# Skill de Prueba de UI

## Objetivo

Verificar que la interfaz de usuario funciona correctamente tras cambios recientes. Si hay fallos, corregirlos y reintentar hasta que todos los tests pasen.

## Instrucciones

### 1. Identificar qué probar

- **Smoke tests**: Tests E2E agnósticos en `tests/smoke.spec.js`. La `baseURL` y rutas se leen desde `{WORKSPACE_ROOT}/config/platforms.json`.
- **UI específica**: Si se creó o modificó una página, ejecutar los tests que la cubran.

### 2. Ejecutar tests con Playwright CLI

```bash
npm test
```

O con UI interactiva:

```bash
npm run test:ui
```

### 3. Si falla

1. Revisar el output de Playwright (trace, screenshots en `{WORKSPACE_ROOT}/playwright/test-results/`).
2. Identificar la causa del fallo.
3. Corregir el código.
4. Volver al paso 2 y ejecutar los tests de nuevo.
5. Repetir hasta que todos pasen.

### 4. Playwright MCP (exploración interactiva)

Si Playwright MCP está disponible:
- Usar `browser_navigate`, `browser_snapshot` para explorar una página concreta.
- Útil para verificación ad hoc sin escribir un test.
- Priorizar `npm test` para smoke tests; MCP para exploración interactiva.

### 5. Chrome DevTools MCP (solo dentro de este skill)

Si está activo en `.kiro/settings/mcp.json`:
- Usar **solo** dentro de esta skill para trazas de rendimiento, Lighthouse, red, consola y capturas cuando Playwright no basta para diagnosticar.
- No sustituye el criterio de éxito: cerrar siempre con `npm test` pasando.
- Otros agentes del enjambre no deben invocar estas herramientas directamente.

### 6. Criterio de éxito

- Todos los tests de Playwright pasan.
- No hay errores críticos en consola (si se audita con `npm run audit`).

## Checklist

- [ ] `npm test` ejecutado
- [ ] Fallos corregidos y tests re-ejecutados
- [ ] Resultado final: todos los tests pasan
