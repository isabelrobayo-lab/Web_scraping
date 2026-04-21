# SQUAD-AGENTES-IA

Workspace **agnóstico** de pruebas E2E, auditoría, automatización y coordinación de agentes IA para cualquier aplicación web. La configuración por plataforma (URLs, Jira, Datadog, GitHub) se define en `{WORKSPACE_ROOT}/config/platforms.json` (ver `docs/architecture/4-workspace.md`).

---

## Objetivo del Proyecto

Proveer un entorno unificado donde un **enjambre de agentes IA especializados** colabora para:

- Ejecutar **tests E2E** con Playwright contra cualquier plataforma web configurable.
- Realizar **auditorías** de errores de consola y rendimiento (Lighthouse / PageSpeed).
- Generar **reportes** de ciclo de desarrollo y publicarlos en GitHub Pages.
- Integrar con **Jira**, **Datadog**, **GitHub** y **Microsoft Clarity** vía MCP.
- Coordinar agentes especializados (Scout, Historian, Guardian, PO-Agile, Doc Updater, etc.) mediante un **Orquestador** central.
- Visualizar la actividad de agentes en **Miniverse**, un mundo de píxeles compartido.

---

## Requisitos Previos

### CLIs requeridos

| CLI | Versión | Validación |
|-----|---------|------------|
| Node.js | 18+ | `node --version` |
| npm | (incluido con Node) | `npm --version` |
| npx playwright | (incluido con npm) | `npx playwright --version` |
| gh (GitHub CLI) | Última estable | `gh auth status` |

### Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd squad-agentes-ia

# 2. Instalar dependencias
npm install

# 3. Instalar navegadores de Playwright (primera vez)
npx playwright install

# 4. Configurar git hooks (recordatorio Doc Updater en pre-commit)
git config core.hooksPath .githooks

# 5. (Opcional) Si trabajas con Miniverse
cd miniverse && npm install && cd ..
```

---

## Configuración de Plataformas

Al iniciar por primera vez, el sistema solicita crear `{WORKSPACE_ROOT}/config/platforms.json` a partir de la plantilla `docs/templates/platforms.example.json`.

Datos a configurar por plataforma:
- URLs (app, staging, docs)
- `smokePaths` y `auditZones` para tests y auditorías
- Jira: `projectKey`, tableros de incidentes
- Datadog: `site`, `dashboardIds`, `serviceToRepos`
- GitHub: `org`, `repos`

Flujo detallado: [`docs/onboarding/01-flujo-primera-interaccion.md`](./docs/onboarding/01-flujo-primera-interaccion.md)

---

## MCPs (Model Context Protocol)

Servidores MCP configurados en `.kiro/settings/mcp.example.json` (plantilla versionada):

> **Nota:** `.kiro/settings/mcp.json` está en `.gitignore` para que cada usuario mantenga su propia configuración sin conflictos. Al clonar el repo por primera vez, el onboarding copia la plantilla automáticamente. Si ya tienes MCPs configurados a nivel global (`~/.kiro/settings/mcp.json`), Kiro los respeta — el merge tiene precedencia: user < workspace.

| MCP | Comando | Uso | Agente autorizado |
|-----|---------|-----|-------------------|
| **atlassian** | `npx mcp-remote@latest https://mcp.atlassian.com/v1/mcp` | Jira, Confluence (tickets, backlog, HU) | Scout, PO-Agile |
| **playwright** | `npx @playwright/mcp@latest` | Exploración interactiva de UI | Guardian |
| **chrome-devtools** | `npx chrome-devtools-mcp@latest` | Depuración E2E, rendimiento, Lighthouse | Guardian (skill `prueba`) |
| **clarity-server** | `npx @microsoft/clarity-mcp-server` | Analítica de comportamiento, sesiones UX | Clarity Behavior |
| **drawio-mcp** | `npx @drawio/mcp` | Crear y editar diagramas Draw.io | Doc Updater (skill `diagramas-drawio`) |

Configuración adicional:
- **Datadog**: MCP Datadog (configurar dominio: us1, us3, us5, eu1, ap1, ap2)
- **GitHub**: MCP GitHub (PRs, commits, código de repos externos)
- **aws-docs**: Documentación oficial de AWS vía `uvx awslabs.aws-documentation-mcp-server@latest`

Guía de configuración: [`docs/onboarding/02-playwright-mcp-config.md`](./docs/onboarding/02-playwright-mcp-config.md)

---

## Agentes del Enjambre

El proyecto opera con un **Orquestador** que delega a agentes especialistas:

| # | Agente | Dominio | Steering / Prompt |
|---|--------|---------|-------------------|
| 1 | **Orquestador** | Coordinación general | `00-swarm-orchestrator.md` |
| 2 | **Scout** | Jira, Confluence, backlog | Embebido en Orquestador |
| 3 | **Historian** | Exploración del repo actual | Embebido en Orquestador |
| 4 | **Guardian** | Tests E2E, Playwright, CLI | `agent-tech-guardian.md` |
| 5 | **GitHub Repos** | Repos externos de plataforma | `agent-github-repos.md` |
| 6 | **PO-Agile** | Historias de Usuario (INVEST, Gherkin) | `agent-po-agile.md` |
| 7 | **Doc Updater** | Documentación viva | `agent-doc-updater.md` |
| 8 | **Cloud Datadog** | Alertas, monitores, automation | `automation-datadog-alert-prompt.md` |
| 9 | **Clarity Behavior** | UX en producción (Microsoft Clarity) | `agent-clarity-behavior.md` |

Inventario completo: [`docs/architecture/6-inventario-agentes.md`](./docs/architecture/6-inventario-agentes.md)

---

## Skills

| Skill | Ubicación | Uso |
|-------|-----------|-----|
| **prueba** | `.kiro/skills/prueba/` | Tests E2E Playwright, corrección de fallos, reintento |
| **construir** | `.kiro/skills/construir/` | Build, commit, push a producción |
| **diagramas-drawio** | `.kiro/skills/diagramas-drawio/` | Crear/editar diagramas Mermaid / Draw.io |

---

## Hooks de Agentes (16 hooks en `.kiro/hooks/`)

> Versionados en el repo. Al bajar la rama, cualquier usuario los carga automáticamente en Kiro.

### Control de acceso MCP (preToolUse)

| Hook | Propósito |
|------|-----------|
| `atlassian-write-guard` | Solo Scout, PO-Agile y Cloud Agent Datadog pueden ESCRIBIR en Jira/Confluence |
| `clarity-mcp-guard` | Solo Clarity Behavior usa MCP Clarity |
| `datadog-mcp-guard` | Solo Cloud Agent Datadog usa MCP Datadog |
| `chrome-devtools-guard` | Solo Guardian (skill prueba) usa Chrome DevTools MCP |
| `playwright-mcp-guard` | Solo Guardian (skill prueba) usa Playwright MCP |
| `github-mcp-guard` | Solo GitHub Repos y Cloud Agent Datadog usan MCP GitHub |
| `drawio-mcp-guard` | Solo Doc Updater (skill diagramas-drawio) usa MCP Draw.io |

### Seguridad (preToolUse)

| Hook | Propósito |
|------|-----------|
| `secrets-guard` | Bloquea escritura de credenciales/tokens hardcodeados en código |
| `git-safety-guard` | Exige dry-run o stash antes de operaciones git destructivas |
| `jira-metadata-check` | Obliga a consultar metadata de campos antes de crear issues en Jira |

### Delegación y orquestación (promptSubmit)

| Hook | Propósito |
|------|-----------|
| `swarm-delegation-enforcer` | Obliga al Orquestador a evaluar delegación a especialista antes de responder |

### Calidad de código (fileEdited, fileCreated, postToolUse, postTaskExecution)

| Hook | Tipo | Propósito |
|------|------|-----------|
| `hardcoded-data-validator` | postToolUse (write) | Detecta datos hardcodeados que deberían venir de platforms.json |
| `doc-updater-reminder` | fileEdited (código) | Recuerda actualizar docs/ cuando cambia código fuente |
| `agnostico-particular-check` | fileCreated (Workspace/, scripts/, tools/) | Valida si la acción es transversal o particular al producto |
| `lint-on-save` | fileEdited (JS/TS) | Ejecuta ESLint al guardar archivos |
| `post-task-tests` | postTaskExecution | Ejecuta `npm test` tras completar una tarea de spec |

---

## Steering Files

Archivos en `.kiro/steering/` que guían el comportamiento de los agentes:

| Archivo | Inclusión | Propósito |
|---------|-----------|-----------|
| `00-swarm-orchestrator.md` | always | Orquestador: mapa de agentes y delegación |
| `01-plans-location.md` | always | Planes en `Workspace/plans/` |
| `02-onboarding-first-interaction.md` | always | Validar MCPs/CLIs y crear platforms.json |
| `03-validacion-agnostico-particular.md` | always | Pregunta obligatoria: transversal vs particular |
| `04-playwright-cli-vs-mcp.md` | fileMatch (tests) | Cuándo usar Playwright CLI vs MCP |
| `05-indice-agentes.md` | manual | Índice rápido de agentes |
| `05-jira-writing-guidelines.md` | always | Lineamientos de escritura en Jira (ADF, campos obligatorios) |
| `project-rules.md` | always | Reglas generales del proyecto |
| `vitest-cli.md` | fileMatch (tests) | Convenciones Vitest |
| `agent-tech-guardian.md` | fileMatch (tests) | Guardian: QA Specialist |
| `agent-github-repos.md` | fileMatch (platforms) | Lectura repos externos |
| `agent-po-agile.md` | fileMatch (plans, docs) | PO: Historias de Usuario |
| `agent-doc-updater.md` | fileMatch (código, docs) | Documentación viva |
| `agent-clarity-behavior.md` | fileMatch (docs, ux) | Análisis UX con Clarity |
| `org-architecture-rules.md` | always | Reglas de arquitectura organizacional |
| `org-rules-devops.md` | always | Reglas DevOps organizacional |
| `org-rules-infrastructure.md` | always | Reglas de infraestructura organizacional |
| `org-rules-security.md` | always | Reglas de seguridad organizacional |
| `org-stack-tecnologico.md` | always | Stack tecnológico aprobado por la organización |

---

## Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `npm test` | Tests E2E Playwright (URL desde config) |
| `npm run test:unit` | Tests unitarios Vitest |
| `npm run test:unit:watch` | Vitest en modo watch |
| `npm run test:unit:coverage` | Vitest con cobertura → `./coverage/` |
| `npm run test:ui` | Playwright con UI interactiva |
| `npm run audit` | Auditoría de errores de consola |
| `npm run audit:lighthouse` | Auditoría de rendimiento (Lighthouse/PageSpeed) |
| `npm run report:cycle` | Genera reporte ciclo de desarrollo → `Workspace/reports/` |
| `npm run deploy:pages` | Regenera reportes y copia a `docs/` para GitHub Pages |
| `npm run automation:create-cursor` | Asiste creación de automation Datadog |
| `npm run diagrams:regenerate-html` | Regenera HTML de diagramas desde `.mmd` |
| `npm run demo:agentes` | Ejecuta demo de agentes |
| `npm run seed:agents` | Sembrado de agentes Miniverse |
| `npm run lint` | ESLint |
| `npm run format` | Prettier |

---

## Stack Tecnológico

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Node.js | 18+ | Runtime |
| Playwright | ^1.58.2 | Tests E2E y auditoría |
| Vitest | ^4.1.0 | Tests unitarios |
| ESLint | ^8.57.0 | Linting |
| Prettier | ^3.3.0 | Formateo |
| supertest | ^7.2.2 | Tests de API (disponible) |
| fast-check | ^4.6.0 | Property-based testing |

Configuración de calidad:
- `.eslintrc.cjs`: ESLint + Prettier, ignora `Workspace/`
- `.prettierrc`: singleQuote, semi, tabWidth: 2, printWidth: 100, trailingComma: es5

---

## Estructura del Proyecto

```
SQUAD-AGENTES-IA/
├── tests/                    # E2E Playwright + unit/ (Vitest)
├── scripts/                  # Config, auditoría, demo agentes
├── tools/scripts/            # Reportes, deploy, automation, diagramas
├── miniverse/                # Mundo de píxeles para agentes IA
├── docs/                     # Documentación viva y GitHub Pages
│   ├── architecture/         # Diseño, stack, inventario agentes
│   ├── onboarding/           # Flujo primera interacción
│   ├── runbook/              # Guías operativas
│   ├── templates/            # Plantillas (platforms.example.json)
│   ├── data/                 # Datos de referencia
│   └── decisions/            # ADRs
├── Workspace/                # Artefactos por producto (.gitignore)
│   ├── <tu-plataforma>/       # WORKSPACE_ROOT (ej. ciencuadras, jelpit, etc.)
│   └── <otra-plataforma>/
├── .kiro/                    # Steering, hooks, skills, specs
│   ├── steering/             # Reglas de comportamiento de agentes
│   ├── hooks/                # Hooks de control de acceso y calidad
│   ├── skills/               # Skills reutilizables (prueba, construir, diagramas)
│   └── settings/mcp.json     # Configuración MCP del workspace
├── .iarules/                 # Reglas de arquitectura y seguridad
├── .githooks/                # Git hooks (pre-commit: recordatorio Doc Updater)
├── rules/                    # Reglas técnicas (Playwright, Datadog, PRD)
├── playwright.config.js      # baseURL desde platforms.json
├── vitest.config.js          # Tests unitarios (tests/unit/)
└── package.json
```

---

## Git Hooks

El hook `pre-commit` en `.githooks/` muestra un recordatorio cuando hay cambios en código sin cambios en documentación. Instalación:

```bash
git config core.hooksPath .githooks
```

Para saltar: `git commit --no-verify`

---

## Reglas del Proyecto (.iarules/)

| Regla | Propósito |
|-------|-----------|
| `architecture-rules.md` | Reglas de arquitectura (capas, seguridad, resiliencia, API First) |
| `rules-security.md` | Seguridad (autenticación, validación, encriptación, secretos) |
| `rules-devops.md` | Reglas DevOps |
| `rules-infrastructure.md` | Reglas de infraestructura |
| `stack-seguros-bolivar.md` | Stack específico de la organización |

---

## GitHub Pages

Los reportes HTML se publican en GitHub Pages. El workflow `.github/workflows/deploy-miniverse-github-pages.yml` despliega Miniverse + reportes de `docs/`.

```bash
# Regenerar reportes y copiar a docs/
npm run deploy:pages

# Commit y push
git add docs/
git commit -m "Actualizar reportes para GitHub Pages"
git push
```

---

## Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `WORKSPACE_ROOT` | Raíz de artefactos (requerida). Si no se define, cae a `Workspace/` con warning | `Workspace/` (genérico) |
| `PLATFORMS_CONFIG_PATH` | Ruta alternativa a platforms.json | `{WORKSPACE_ROOT}/config/platforms.json` |
| `REPORTES_BASE_URL` | URL base para tests de reportes | GitHub Pages URL |
| `MINIVERSE_BASE_URL` | URL base para tests Miniverse | `http://localhost:5173` |
| `MINIVERSE_URL` | URL de la API Miniverse para el adaptador de hooks (`kiro-miniverse-sync.mjs`) | `http://localhost:4321` |
| `CLARITY_API_TOKEN` | Token de exportación de Microsoft Clarity | — |

---

## Documentación Adicional

| Documento | Descripción |
|-----------|-------------|
| [`docs/resumen-proyecto.md`](./docs/resumen-proyecto.md) | Contexto principal para IA |
| [`docs/ESTRUCTURA.md`](./docs/ESTRUCTURA.md) | Estructura completa y flujos de lógica |
| [`docs/architecture/`](./docs/architecture/) | Diseño del sistema |
| [`docs/onboarding/`](./docs/onboarding/) | Flujo de primera interacción |
| [`docs/runbook/`](./docs/runbook/) | Guías operativas |
| [`CHANGELOG.md`](./CHANGELOG.md) | Registro de cambios (SemVer) |
