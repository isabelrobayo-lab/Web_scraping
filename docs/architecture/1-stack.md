# Stack Tecnológico

## Lineamientos

- **Runtime:** Node.js 18+ en todo el proyecto
- **Raíz:** JavaScript (CJS) para tests, scripts y herramientas
- **Testing:** Playwright para E2E; Vitest para unitarios
- **Calidad:** ESLint + Prettier
- **Separación:** Código fuente versionado vs artefactos en `Workspace/` (`.gitignore`)

## Runtime y lenguaje

| Tecnología | Versión | Notas |
|------------|---------|-------|
| Node.js | 18+ | Requerido para scripts y tests |
| JavaScript (CJS) | - | Raíz: `"type": "commonjs"` (tests, scripts) |

## Testing y calidad

| Herramienta | Versión | Uso |
|-------------|---------|-----|
| @playwright/test | ^1.58.2 | Tests E2E (raíz) |
| vitest | ^4.1.0 | Tests unitarios (tests/unit/**/*.test.js) |
| supertest | ^7.2.2 | Tests de API (disponible, no usado aún) |
| eslint | ^8.57.0 | Linting |
| eslint-config-prettier | ^9.1.0 | Integración Prettier |
| prettier | ^3.3.0 | Formateo |

## Infraestructura

| Herramienta | Uso |
|-------------|-----|
| Playwright | Navegadores para E2E y auditoría de consola |

## Subproyectos

### Miniverse (`miniverse/`)

Mundo de píxeles compartido para agentes IA, basado en el upstream **[ianscott313/miniverse](https://github.com/ianscott313/miniverse)** (npm `@miniverse/core`, `@miniverse/server`).

| Tecnología | Uso |
|------------|-----|
| Node.js 18+ | Runtime |
| TypeScript | Cliente Vite |
| Vite ^5 | Dev server y HMR de la UI (`http://localhost:5173`) |
| `@miniverse/server` | CLI `miniverse`, API REST + WebSocket (`http://localhost:4321`) |
| `@miniverse/core` | Motor canvas, ciudadanos, editor |

**Lineamientos aplicados:**

- Planes en `Workspace/plans/` cuando apliquen cambios estructurales
- API de heartbeats y acciones [documentada en el upstream](https://github.com/ianscott313/miniverse#readme); sin hardcodear plataformas en el código del monorepo
- Validación: `tests/miniverse.spec.js` — `npx playwright test --project=miniverse` (con `npm run dev` en `miniverse/`)
