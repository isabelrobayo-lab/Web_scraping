# Inventario de Agentes

> **Documento unificado** para identificar, actualizar y mantener los agentes del proyecto. Cada agente incluye: nombre, objetivo, MCPs, skills, tools, scripts, archivos de código y prompt.

---

## Índice de agentes

| # | Agente | Tipo | Regla/Prompt |
|---|--------|------|--------------|
| 1 | Orquestador (The Architect) | Steering | `.kiro/steering/00-swarm-orchestrator.md` |
| 2 | Scout | Steering | `.kiro/steering/agent-scout.md` |
| 3 | Historian | Steering | `.kiro/steering/agent-historian.md` |
| 4 | Guardian (QA Specialist) | Steering | `.kiro/steering/agent-tech-guardian.md` |
| 5 | GitHub Repos | Steering | `.kiro/steering/agent-github-repos.md` |
| 6 | PO-Agile | Steering | `.kiro/steering/agent-po-agile.md` |
| 7 | Doc Updater | Steering | `.kiro/steering/agent-doc-updater.md` |
| 8 | Cloud Agent Datadog Alert | Steering | `.kiro/steering/agent-datadog-alert.md` |
| 9 | Clarity Behavior | Steering | `.kiro/steering/agent-clarity-behavior.md` |
| 10 | Prompt Engineer | Steering (manual) | `.kiro/steering/agent-prompt-engineer.md` |

---

## 1. Orquestador (The Architect)

| Campo | Valor |
|-------|-------|
| **Nombre** | Orquestador / The Architect |
| **Objetivo** | Coordinar el enjambre: **decidir** qué agente especialista actúa en cada momento y **activarlo** vía subagentes. No sustituir al especialista ejecutando MCP, CLI ni lectura/escritura del repo, salvo excepción explícita del usuario en ese turno. |
| **MCPs** | Ninguno en la sesión del Orquestador; el uso de MCP ocurre **solo** en subagentes (`atlassian`, `datadog`, `github`, etc.). |
| **Skills** | — |
| **Tools** | Subagentes (delegación). Texto al usuario (decisión de orquestación, aclaraciones, síntesis). |
| **Scripts** | `scripts/demo-agentes-run.js` (demo educativa) |
| **Archivos de código** | `.kiro/steering/00-swarm-orchestrator.md`, `.kiro/steering/01-plans-location.md` |
| **Otra información** | **inclusion: always**. Mapa Orquestador → agente en `00-swarm-orchestrator.md`. Planes en `Workspace/plans/`. |

---

## 2. Scout (Fase de Análisis)

| Campo | Valor |
|-------|-------|
| **Nombre** | Scout / El explorador |
| **Objetivo** | Leer tickets de Jira y extraer requerimientos. Responde: *¿Qué quiere el negocio?* |
| **MCPs** | `atlassian` (Jira: getJiraIssue, searchJiraIssuesUsingJql, getVisibleJiraProjects) |
| **Archivos de código** | `.kiro/steering/agent-scout.md`. Referencia: `rules/AGENTS.md`. |
| **Regla de escritura Jira** | **Obligatorio:** Al crear o registrar en Jira, el prefijo **"Creado con IA"** debe ir en la **descripción**, no en el título. |
| **Otra información** | **fileMatch:** `Workspace/plans/**`, `**/platforms.json`, `docs/templates/**`. El Orquestador delega Scout vía subagente para usar MCP Jira. |

---

## 3. Historian (Fase de Contexto)

| Campo | Valor |
|-------|-------|
| **Nombre** | Historian / El experto en historia |
| **Objetivo** | Revisar código y cambios recientes para evitar repetir errores. Responde: *¿Qué impacto tendrá este cambio?* |
| **Tools** | Exploración del repo, `gh pr list`, `git log -n 5`, `tree -L 3` |
| **Archivos de código** | `.kiro/steering/agent-historian.md`. Referencia: `rules/AGENTS.md`. |
| **Otra información** | **fileMatch:** `**/*.{js,ts,tsx,cjs,mjs}`, `**/scripts/**`, `**/tests/**`, `**/tools/**`, `package.json`, `docs/**`. **Scope: repo actual.** |

---

## 4. Guardian (QA Specialist)

| Campo | Valor |
|-------|-------|
| **Nombre** | Guardian / QA Specialist |
| **Objetivo** | Validar que los tests E2E pasan. Self-healing de tests. Exigir cobertura mínima. |
| **MCPs** | Chrome DevTools MCP (`chrome-devtools-mcp`): declarado en `.kiro/settings/mcp.json`; **uso reservado** a este agente y al skill `prueba`. |
| **Skills** | `prueba` (`.kiro/skills/prueba/SKILL.md`) |
| **Tools** | `npx playwright test`; herramientas MCP de Chrome DevTools solo para depuración/rendimiento en contexto E2E |
| **Scripts** | `npm test`, `npm run test:ui`, `npx playwright test --project=miniverse` |
| **Archivos de código** | `.kiro/steering/agent-tech-guardian.md`, `tests/smoke.spec.js`, `tests/reportes.spec.js`, `playwright.config.js` |
| **Otra información** | **fileMatch:** `**/tests/**`, `playwright.config.js`, `**/*.spec.js`. Referencia cobertura: `docs/architecture/3-tech-stack-org.md` (70%). |

---

## 5. GitHub Repos (Platform Repos Reader)

| Campo | Valor |
|-------|-------|
| **Nombre** | GitHub Repos / Platform Repos Reader |
| **Objetivo** | Leer y analizar repositorios externos de la plataforma. |
| **MCPs** | `github` (get_file_contents, list_pull_requests, list_commits, search_code, list_issues, search_repositories) |
| **Tools** | MCP GitHub, CLI `gh` |
| **Archivos de código** | `.kiro/steering/agent-github-repos.md`, `Workspace/**/config/platforms.json` |
| **Otra información** | **Scope: repos externos** definidos en `platforms[].github.repos`. Solo lectura. |

---

## 6. PO-Agile (Product Owner / Agile Master)

| Campo | Valor |
|-------|-------|
| **Nombre** | PO-Agile |
| **Objetivo** | Transformar requisitos en Historias de Usuario (INVEST, Dado-Cuando-Entonces). |
| **MCPs** | `atlassian` (opcional, para crear HU en Jira) |
| **Archivos de código** | `.kiro/steering/agent-po-agile.md` |
| **Regla de escritura Jira** | **Obligatorio:** Al crear HU en Jira, el prefijo **"Creado con IA"** debe ir en la **descripción**, no en el título. |
| **Otra información** | **fileMatch:** `Workspace/plans/**`, `**/docs/**`, `**/*.spec.md`, `**/platforms.json`. Proceso Chain-of-Thought obligatorio. |

---

## 7. Doc Updater (Experto en Documentación)

| Campo | Valor |
|-------|-------|
| **Nombre** | Doc Updater |
| **Objetivo** | Mantener la documentación viva. Actualizar `docs/` cuando el código cambia con una solución definitiva. |
| **MCPs** | `drawio-mcp` (`@drawio/mcp`): `open_drawio_xml`, `open_drawio_csv`, `open_drawio_mermaid` — **uso exclusivo** de este agente y skill `diagramas-drawio`. |
| **Skills** | `diagramas-drawio` (si se actualizan diagramas) |
| **Archivos de código** | `.kiro/steering/agent-doc-updater.md`, `.githooks/pre-commit` |
| **Otra información** | **fileMatch:** `**/*.{js,ts,tsx,cjs,mjs}`, `scripts/`, `tests/`, `tools/`, `miniverse/`, `docs/**`, `rules/**`. Trigger adicional: pre-commit hook. |

---

## 8. Cloud Agent Datadog Alert

| Campo | Valor |
|-------|-------|
| **Nombre** | Cloud Agent Datadog Alert |
| **Objetivo** | Obtener alertas de Datadog vía MCP, validar servicios, consultar repos, generar plan y crear/verificar HU en Jira. |
| **MCPs** | `datadog`, `atlassian`, `github` |
| **Archivos de código** | `.kiro/steering/agent-datadog-alert.md`, `docs/templates/automation-datadog-alert-prompt.md`, `docs/runbook/automation-datadog-alert.md`, `Workspace/**/config/platforms.json` |
| **Archivo de prompt** | `.kiro/steering/agent-datadog-alert.md` (steering), `docs/templates/automation-datadog-alert-prompt.md` (prompt original) |
| **Otra información** | Variables de entorno: `PLATFORMS_JSON`, `JIRA_CLOUD_ID`, `JIRA_PROJECT_KEY`. Config: `datadog.serviceToRepos`, `github.repos` en platforms.json. |

---

## 9. Clarity Behavior (Analista Clarity / UX comportamiento)

| Campo | Valor |
|-------|-------|
| **Nombre** | Clarity Behavior / Analista Clarity |
| **Objetivo** | Analizar comportamiento de usuarios reales con Microsoft Clarity vía MCP. |
| **MCPs** | `@microsoft/clarity-mcp-server`: `query-analytics-dashboard`, `list-session-recordings`, `query-documentation-resources` |
| **Tools** | Herramientas del MCP Clarity; autenticación con token JWT de exportación (`CLARITY_API_TOKEN`). |
| **Archivos de código** | `.kiro/steering/agent-clarity-behavior.md`, `docs/onboarding/02-playwright-mcp-config.md`, `docs/data/clarity-projects.md` |
| **Otra información** | **fileMatch:** `docs/**`, `**/ux/**`, `**/analytics/**`. No sustituye al Guardian en E2E. Respetar privacidad de datos de usuarios reales. |

---

## 10. Prompt Engineer (Diseñador de Prompts Avanzados)

| Campo | Valor |
|-------|-------|
| **Nombre** | Prompt Engineer / Diseñador de Prompts |
| **Objetivo** | Diseñar prompts avanzados, efectivos y optimizados para modelos de IA. Aplicar técnicas de prompting (CoT, Few-Shot, RAG, ReAct, Tree of Thoughts, etc.) y explicar las decisiones tomadas. |
| **MCPs** | Ninguno. Opera con conocimiento y razonamiento. |
| **Skills** | — |
| **Tools** | Texto al usuario (prompt creado + explicación + recomendaciones). Web search para benchmarks de modelos si se solicita. |
| **Archivos de código** | `.kiro/steering/agent-prompt-engineer.md` |
| **Otra información** | **inclusion: manual**. **NUNCA activado automáticamente por el Orquestador.** Solo bajo petición explícita del usuario. No aparece en el mapa de agentes del Orquestador. |

---

## Reglas de soporte (no son agentes)

| Regla | Propósito |
|-------|-----------|
| `.kiro/steering/01-plans-location.md` | Planes en `Workspace/plans/` |
| `.kiro/steering/02-onboarding-first-interaction.md` | Validar MCPs/CLIs y crear platforms.json si no existe |
| `.kiro/steering/03-validacion-agnostico-particular.md` | Pregunta obligatoria: transversal vs particular al producto |
| `.kiro/steering/vitest-cli.md` | Scripts npm y patrones CLI para Vitest / cobertura |
| `.kiro/steering/04-playwright-cli-vs-mcp.md` | Cuándo usar Playwright Test (CLI) vs Playwright MCP |
| `.kiro/steering/project-rules.md` | Reglas generales del proyecto |

---

## Skills disponibles (reutilizables por agentes)

| Skill | Ubicación | Uso |
|-------|-----------|-----|
| **construir** | `.kiro/skills/construir/SKILL.md` | Build, commit, push a producción |
| **prueba** | `.kiro/skills/prueba/SKILL.md` | Playwright E2E, corrección de fallos, reintento |
| **diagramas-drawio** | `.kiro/skills/diagramas-drawio/SKILL.md` | Crear/editar diagramas con MCP drawio |

---

## Hooks de enforcement del enjambre

> Todos los hooks viven en `.kiro/hooks/` y se versionan con el repo. Al bajar la rama, cualquier usuario los carga automáticamente en Kiro.

### Control de acceso MCP (preToolUse)

| Hook | Archivo | Propósito |
|------|---------|-----------|
| `atlassian-write-guard` | `.kiro/hooks/atlassian-write-guard.kiro.hook` | Solo Scout, PO-Agile y Cloud Agent Datadog pueden ESCRIBIR en Jira/Confluence |
| `clarity-mcp-guard` | `.kiro/hooks/clarity-mcp-guard.kiro.hook` | Solo Clarity Behavior puede usar MCP Clarity |
| `datadog-mcp-guard` | `.kiro/hooks/datadog-mcp-guard.kiro.hook` | Solo Cloud Agent Datadog puede usar MCP Datadog |
| `chrome-devtools-guard` | `.kiro/hooks/chrome-devtools-guard.kiro.hook` | Solo Guardian (skill prueba) puede usar Chrome DevTools MCP |
| `playwright-mcp-guard` | `.kiro/hooks/playwright-mcp-guard.kiro.hook` | Solo Guardian (skill prueba) puede usar Playwright MCP |
| `github-mcp-guard` | `.kiro/hooks/github-mcp-guard.kiro.hook` | Solo GitHub Repos y Cloud Agent Datadog pueden usar MCP GitHub |
| `drawio-mcp-guard` | `.kiro/hooks/drawio-mcp-guard.kiro.hook` | Solo Doc Updater (skill diagramas-drawio) puede usar MCP Draw.io |

### Seguridad (preToolUse)

| Hook | Archivo | Propósito |
|------|---------|-----------|
| `secrets-guard` | `.kiro/hooks/secrets-guard.kiro.hook` | Bloquea escritura de credenciales/tokens hardcodeados en código |
| `git-safety-guard` | `.kiro/hooks/git-safety-guard.kiro.hook` | Exige dry-run o stash antes de operaciones git destructivas |
| `jira-metadata-check` | `.kiro/hooks/jira-metadata-check.kiro.hook` | Obliga a consultar metadata de campos antes de crear issues en Jira |

### Delegación y orquestación (promptSubmit)

| Hook | Archivo | Propósito |
|------|---------|-----------|
| `swarm-delegation-enforcer` | `.kiro/hooks/swarm-delegation-enforcer.kiro.hook` | Obliga al Orquestador a evaluar delegación a especialista antes de responder |

### Calidad de código (fileEdited, fileCreated, postToolUse, postTaskExecution)

| Hook | Archivo | Tipo | Propósito |
|------|---------|------|-----------|
| `hardcoded-data-validator` | `.kiro/hooks/hardcoded-data-validator.kiro.hook` | postToolUse (write) | Detecta datos hardcodeados que deberían venir de platforms.json |
| `doc-updater-reminder` | `.kiro/hooks/doc-updater-reminder.kiro.hook` | fileEdited (código) | Recuerda actualizar docs/ cuando cambia código fuente |
| `agnostico-particular-check` | `.kiro/hooks/agnostico-particular-check.kiro.hook` | fileCreated (Workspace/, scripts/, tools/) | Valida si la acción es transversal o particular al producto |
| `lint-on-save` | `.kiro/hooks/lint-on-save.kiro.hook` | fileEdited (JS/TS) | Ejecuta ESLint al guardar archivos |
| `post-task-tests` | `.kiro/hooks/post-task-tests.kiro.hook` | postTaskExecution | Ejecuta `npm test` tras completar una tarea de spec |

---

## Diagrama de referencia

| Diagrama | Descripción |
|----------|-------------|
| [equipo-agentes.html](../diagrams/equipo-agentes.html) | Equipo Orquestador → Scout, Historian, Guardian |
| [4-fases-protocolo.html](../diagrams/4-fases-protocolo.html) | 4 fases del protocolo |
| [flujo-automation-datadog-alert.html](../diagrams/flujo-automation-datadog-alert.html) | Cloud Agent Datadog (6 pasos) |
| [agentes-mcps-cli-skills-actividades.html](../diagrams/agentes-mcps-cli-skills-actividades.html) | Agentes ↔ MCPs, CLIs, skills |

---

## Agentes CLI (Kiro CLI)

> Los agentes CLI permiten ejecutar los especialistas del enjambre desde terminal vía `kiro-cli --agent <nombre>`. Cada agente tiene su propia configuración de tools, MCPs, hooks y permisos pre-aprobados. Viven en `.kiro/agents/`.

| # | Agente CLI | Archivo | Shortcut | MCPs | Tools principales |
|---|-----------|---------|----------|------|-------------------|
| 1 | Scout | `.kiro/agents/scout.json` | `ctrl+1` | Atlassian | `read`, `@atlassian` |
| 2 | Guardian | `.kiro/agents/guardian.json` | `ctrl+2` | Playwright, Chrome DevTools | `read`, `write`, `shell`, `@playwright`, `@chrome-devtools` |
| 3 | Historian | `.kiro/agents/historian.json` | `ctrl+3` | — | `read`, `shell` (git, gh) |
| 4 | GitHub Repos | `.kiro/agents/github-repos.json` | `ctrl+4` | GitHub | `read`, `shell` (gh), `@github` |
| 5 | Datadog Alert | `.kiro/agents/datadog-alert.json` | `ctrl+5` | Datadog, GitHub, Atlassian | `read`, `write`, `shell`, `@datadog`, `@github`, `@atlassian` |

### Uso desde terminal

```bash
# Iniciar sesión con un agente específico
kiro-cli --agent scout

# Dentro de una sesión, cambiar de agente
/agent swap

# Listar agentes disponibles
/agent list
```

### Diseño de cada agente CLI

- **Prompt:** Apunta al steering existente del agente (`file://../steering/agent-*.md`).
- **MCPs:** Cada agente declara solo los MCPs que necesita (`includeMcpJson: false`).
- **Tools:** Restringidos al mínimo necesario. `allowedTools` pre-aprueba operaciones de lectura.
- **Resources:** Carga steering, lineamientos Jira, contexto de plataforma y `platforms.json`.
- **Hooks:** `agentSpawn` para contexto inicial. `preToolUse` para validaciones de escritura en Jira.
- **Seguridad:** Credenciales vía variables de entorno. Sin secretos en archivos.

### Agentes NO incluidos en CLI (y por qué)

| Agente | Razón |
|--------|-------|
| Orquestador | Es el agente default del IDE. No opera aislado. |
| Doc Updater | Necesita Draw.io MCP (visual). Mejor en IDE. |
| PO-Agile | Su valor principal es interactivo. Opcional futuro. |
| Clarity Behavior | MCP requiere token manual y login web. Opcional futuro. |
| Prompt Engineer | Manual, conversacional. No gana nada en CLI. |

---

## Cómo actualizar un agente

1. **Steering (1–7, 9):** Editar el `.md` en `.kiro/steering/`.
2. **Cloud Agent (8):** Editar `docs/templates/automation-datadog-alert-prompt.md`.
3. **MCPs/Skills:** Actualizar este documento y el steering correspondiente.
4. **Agente CLI:** Editar el `.json` en `.kiro/agents/`. El prompt apunta al steering, así que cambios en steering se reflejan automáticamente.
5. **Nuevo agente:** Añadir entrada en este inventario, fila en `00-swarm-orchestrator.md` y crear steering en `.kiro/steering/`. Si aplica CLI, crear `.kiro/agents/<nombre>.json`.

---

## Referencias

- [5-agents-functional-architecture.md](./5-agents-functional-architecture.md) — Documento para negocio
- [runbook/automation-datadog-alert.md](../runbook/automation-datadog-alert.md) — Configuración Cloud Agent
- [Kiro CLI — Custom Agents](https://kiro.dev/docs/cli/custom-agents/) — Documentación oficial
- [Kiro CLI — Configuration Reference](https://kiro.dev/docs/cli/custom-agents/configuration-reference) — Referencia de campos
