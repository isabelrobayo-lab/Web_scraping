# Resumen del Proyecto: SQUAD-AGENTES-IA

> **Archivo de contexto principal** para que la IA entienda el proyecto, sus patrones y reglas de comportamiento.

---

## ¿De qué trata la aplicación?

**SQUAD-AGENTES-IA** es un workspace **agnóstico** de pruebas E2E y auditoría para cualquier plataforma/aplicación web.

Incluye:

- **Tests E2E** con Playwright (baseURL configurable)
- **Scripts de auditoría** de errores de consola en el navegador
- **Reportes** de ciclo de desarrollo y despliegue a GitHub Pages
- **Integración** con Jira, Datadog y GitHub vía MCP
- **Miniverse** — mundo de píxeles compartido para agentes IA (`miniverse/`)

**Configuración por plataforma** (URLs, Jira, Datadog) vive en `{WORKSPACE_ROOT}/config/platforms.json` (ver `docs/architecture/4-workspace.md`). Ver `docs/onboarding/01-flujo-primera-interaccion.md` para el flujo de primera interacción.

**Microsoft Clarity:** métricas y sesiones vía MCP (agente Clarity Behavior) y token de proyecto. Referencias de tableros enlazados a productos concretos se almacenan en `{WORKSPACE_ROOT}/data/clarity-projects.md`.

---

## Stack tecnológico (versiones)

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Node.js | 18+ | Runtime |
| Playwright | ^1.58.2 | Tests E2E y auditoría de consola |
| Vitest | ^4.1.0 | Tests unitarios (audit-data, helpers) |
| ESLint | ^8.57.0 | Linting |
| Prettier | ^3.3.0 | Formateo |
| supertest | ^7.2.2 | Tests de API (disponible, no usado aún) |

---

## Patrones de componentes

### Tests

- **Playwright** (`playwright.config.js`): proyecto **chromium** — `tests/smoke.spec.js` (smoke agnóstico) y `tests/reportes.spec.js` (página `reportes.html` en GitHub Pages; URL por defecto configurable con `REPORTES_BASE_URL`). Proyecto **miniverse** — `tests/miniverse.spec.js` (base URL `MINIVERSE_BASE_URL` o `http://localhost:5173`). Los archivos en `tests/unit/**` no los ejecuta Playwright (`testIgnore`).
- **Vitest**: `tests/unit/` — audit-data, get-platform-config, analyze-cycle-time, etc. Ver `docs/testing/vitest-cli.md`.

### Scripts (`scripts/`)

- **workspace-root.js** — resuelve la raíz de artefactos (`WORKSPACE_ROOT`); lo usan scripts y tests que escriben bajo `Workspace/`
- **get-platform-config.js** — lee `{WORKSPACE_ROOT}/config/platforms.json` (o ruta absoluta/relativa en `PLATFORMS_CONFIG_PATH`); usado por Playwright, auditorías y herramientas
- **audit-console-errors.js** — auditoría de errores de consola (URL y zonas desde config)
- **audit-data.js** — datos y helpers para auditoría (ZONES por defecto, createEmptyReport, categorizeMessage)
- **audit-lighthouse.js** — auditoría de rendimiento (PageSpeed Insights API o Lighthouse CLI); salida en `Workspace/audit/lighthouse/`
- **demo-agentes-run.js** — demo del flujo de agentes; enlazado desde `docs/demo-agentes.html` vía `npm run demo:agentes`

### Herramientas (`tools/scripts/`)

- **generate-cycle-report-html.js** — reporte HTML de ciclo de desarrollo
- **analyze-cycle-time.js** — análisis por fases (Jira) → MD en `Workspace/reports/`
- **deploy-pages.js** — regenera reportes y copia a `docs/` para GitHub Pages
- **create-cursor-automation.js** — creación asistida de automation en cursor.com (Datadog → plan + HU); `npm run automation:create-cursor`
- **regenerate-diagram-html.js** — regenera `docs/diagrams/*.html` desde `*.mmd`; `npm run diagrams:regenerate-html`

---

## Reglas (Rules)

Comportamientos que la IA **debe seguir** al trabajar en este proyecto:

1. **No hagas build en cada cambio**  
   No ejecutes `npm run build` o equivalentes tras cada modificación. Solo haz build cuando sea explícitamente necesario (ej. antes de deploy).

2. **Planificación antes de código**  
   Para tareas complejas, genera un plan en `{WORKSPACE_ROOT}/plans/` antes de tocar código.

3. **Validación con Playwright**  
   No consideres una tarea terminada sin un reporte de éxito de Playwright cuando aplique.

4. **Orquestador siempre activa especialistas**  
   Toda petición de trabajo debe pasar por **decisión del Orquestador** y **activación vía Task** (subagentes) según el mapa en `.kiro/steering/00-swarm-orchestrator.md`. No omitir el especialista por considerar la tarea “pequeña”.

5. **Uso de MCP (segregado por hooks)**  
   Cada MCP tiene un hook `preToolUse` que restringe su uso al agente autorizado. Los 16 hooks en `.kiro/hooks/` se versionan con el repo y se cargan automáticamente en Kiro.
   - Jira/Confluence escritura: Scout, PO-Agile, Cloud Agent (`atlassian-write-guard`)
   - Datadog: Cloud Agent Datadog (`datadog-mcp-guard`)
   - GitHub MCP (repos externos): GitHub Repos, Cloud Agent (`github-mcp-guard`)
   - Playwright MCP: Guardian (`playwright-mcp-guard`)
   - Chrome DevTools: Guardian/skill prueba (`chrome-devtools-guard`)
   - Clarity: Clarity Behavior (`clarity-mcp-guard`)
   - Draw.io: Doc Updater/skill diagramas (`drawio-mcp-guard`)
   - Seguridad: `secrets-guard` (no credenciales en código), `git-safety-guard` (no git destructivo sin dry-run)
   - Delegación: `swarm-delegation-enforcer` (Orquestador evalúa especialista en cada prompt)

6. **Automatización Datadog**  
   **Scheduled: alertas vía MCP Datadog, validación, repos, plan en `{WORKSPACE_ROOT}/plans/` y HU en Jira. Ver `docs/runbook/automation-datadog-alert.md`.

7. **No mezclar contextos**  
   Preferir **varios Task** con roles claros a mezclar Scout, Historian y Guardian en un solo contexto difuso. Excepción: el usuario pide explícitamente un solo hilo en ese mensaje.

8. **Spec Driven Development (SDD)**  
   La especificación es la fuente de verdad. Antes de implementar: (1) Define requisitos y criterios de aceptación, (2) Genera diseño técnico y plan en `{WORKSPACE_ROOT}/plans/`, (3) Descompón en tareas atómicas. El código se deriva de la spec; usa PRD/Confluence como input cuando aplique.

### Framework de trabajo

**Spec Driven Development (SDD)** es el framework de trabajo del proyecto. La especificación formal (PRD, Confluence, Jira) es la fuente de verdad; el código se deriva de ella. Referencias: `rules/process-prd-generation.mdc` (formato PRD) y `rules/AGENTS.md` (ciclo Problem/Design/Deliver).

---

## Estructura de carpetas relevante

Separación estricta entre **código fuente** (versionado) y **artefactos generados** (`.gitignore`). Ver [docs/ESTRUCTURA.md](./ESTRUCTURA.md) para el árbol completo, flujos de lógica y **diagramas Mermaid** integrados.

> **Diagramas:** La documentación incluye diagramas gráficos (Mermaid) en ESTRUCTURA, onboarding, architecture y runbooks. Ver [docs/diagrams/README.md](./diagrams/README.md) para la estrategia y edición en Draw.io.

```
SQUAD-AGENTES-IA/
├── tests/
│   ├── smoke.spec.js       # E2E agnósticos (baseURL y smokePaths desde config)
│   └── unit/               # Tests unitarios (Vitest)
├── scripts/
│   ├── workspace-root.js
│   ├── get-platform-config.js
│   ├── audit-console-errors.js
│   ├── audit-data.js
│   ├── audit-lighthouse.js
│   └── demo-agentes-run.js
├── tools/scripts/
│   ├── generate-cycle-report-html.js
│   ├── analyze-cycle-time.js
│   ├── deploy-pages.js
│   ├── create-cursor-automation.js
│   ├── regenerate-diagram-html.js
│   └── README.md
├── docs/                   # Documentación y reportes publicados
│   ├── README.md           # Índice de documentación
│   ├── resumen-proyecto.md # Contexto principal para IA
│   ├── ESTRUCTURA.md       # Estructura y lógica del proyecto
│   ├── Asset/              # Plantillas CSS y HTML para reportes (GitHub Pages)
│   ├── architecture/       # Diseño, stack, design-system, workspace
│   ├── onboarding/         # Flujo primera interacción
│   ├── runbook/            # Guías operativas
│   ├── analisis/           # Análisis y reportes MD (ciclo, limpieza)
│   ├── templates/          # Plantillas de config (platforms.example.json)
│   ├── data/               # Datos de referencia (jira-cycle-*.json)
│   └── decisions/          # ADRs
├── Workspace/              # Artefactos por producto (no versionados); ver docs/architecture/4-workspace.md
│   ├── <tu-plataforma>/  # WORKSPACE_ROOT
│   │   ├── config/platforms.json
│   │   └── reports/ plans/ audit/ playwright/ observabilidad/ repos/ data/
│   └── <otra-plataforma>/  # Misma forma de carpetas (otro producto)
├── playwright.config.js    # baseURL desde get-platform-config
├── vitest.config.js        # Config Vitest (tests/unit/**/*.test.js)
├── .kiro/                  # Steering, hooks, skills, specs y agents CLI
│   └── agents/             # Custom Agents para Kiro CLI (terminal)
└── rules/                  # Reglas técnicas (Playwright, Datadog, PRD, etc.)
```

---

## Comandos principales

| Comando | Descripción |
|---------|-------------|
| `npm test` | Tests E2E Playwright (URL desde config) |
| `npm run test:unit` | Tests unitarios Vitest (single run) |
| `npm run test:unit:watch` | Vitest watch (desarrollo) |
| `npm run test:unit:ui` | Vitest UI interactiva |
| `npm run test:unit:coverage` | Vitest con cobertura → `./coverage/` |
| `npm run test:unit:list` | Lista tests Vitest |
| `npm run test:unit:related` | Vitest solo tests relacionados con archivos cambiados (`vitest related --run`) |
| `npm run test:ui` | Playwright con UI interactiva |
| `npm run audit` | Auditoría de errores de consola (URL desde config) |
| `npm run audit:lighthouse` | Auditoría Lighthouse / PageSpeed → `Workspace/audit/lighthouse/` |
| `npm run report:cycle` | Genera reporte ciclo de desarrollo → `Workspace/reports/` |
| `npm run deploy:pages` | Regenera reportes y copia a `docs/` para GitHub Pages |
| `npm run automation:create-cursor` | Asiste creación de automation Datadog en Cursor (ver `docs/runbook/automation-datadog-alert.md`) |
| `npm run diagrams:regenerate-html` | Regenera HTML de diagramas en `docs/diagrams/` desde `.mmd` |
| `npm run demo:agentes` | Ejecuta demo de agentes |
| `npm run demo:agentes:open` | Abre `docs/demo-agentes.html` en el navegador (macOS `open`) |
| `npm run lint` | ESLint |
| `npm run format` | Prettier |
| `npm run seed:agents` | Sembrado de agentes Miniverse (`npm --prefix miniverse run seed:agents`) |
| `npm run seed:agents:live` | Igual, proceso en vivo (`miniverse` seed con `--keep-alive`) |
| `npx playwright test --project=miniverse` | Tests E2E Miniverse (requiere `cd miniverse && npm run dev`: Vite :5173 + API :4321) |
