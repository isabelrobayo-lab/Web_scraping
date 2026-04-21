# Inventario de MCPs Instalados

Referencia consolidada de todos los servidores MCP configurados en el workspace. Útil para replicar el entorno en otras máquinas o para onboarding de nuevos miembros.

> **Última actualización:** 2026-04-17

---

## Resumen

| # | MCP Server | Paquete / Binario | Nivel | Estado | Agente autorizado |
|---|-----------|-------------------|-------|--------|-------------------|
| 1 | Atlassian | `mcp-remote@latest` → `mcp.atlassian.com` | Workspace | ✅ Activo | Scout, PO-Agile, Cloud Agent Datadog Alert |
| 2 | Playwright | `@playwright/mcp@latest` | Workspace | ✅ Activo | Guardian (skill `prueba`) |
| 3 | Chrome DevTools | `chrome-devtools-mcp@latest` | Workspace + Cursor | ✅ Activo | Guardian (skill `prueba`) |
| 4 | Microsoft Clarity | `@microsoft/clarity-mcp-server` | Workspace + Cursor | ✅ Activo | Clarity Behavior |
| 5 | Datadog | `datadog_mcp_cli.exe` (binario local) | Workspace | ✅ Activo | Cloud Agent Datadog Alert |
| 6 | Draw.io | `@drawio/mcp` | Workspace | ✅ Activo | Doc Updater (skill `diagramas-drawio`) |
| 7 | Fetch | `mcp-server-fetch` (uvx) | Global | ❌ Deshabilitado | — |
| 8 | Figma (Power) | `mcp.figma.com/mcp` (HTTP) | Global (Power) | ✅ Activo | — |

---

## Detalle por servidor

### 1. Atlassian (Jira + Confluence)

- **Paquete:** `mcp-remote@latest` conectando a `https://mcp.atlassian.com/v1/mcp`
- **Tipo:** Remote MCP (proxy via mcp-remote)
- **Propósito:** Gestión de issues Jira, búsqueda CQL en Confluence, lectura/escritura de páginas, transiciones de workflow
- **Auto-approve:** `getAccessibleAtlassianResources`, `searchJiraIssuesUsingJql`, `getJiraIssue`, `editJiraIssue`, `lookupJiraAccountId`, `getJiraProjectIssueTypesMetadata`
- **Herramientas principales:** `searchJiraIssuesUsingJql`, `getJiraIssue`, `createJiraIssue`, `editJiraIssue`, `transitionJiraIssue`, `addCommentToJiraIssue`, `searchConfluenceUsingCql`, `getConfluencePage`, `search` (Rovo)

```json
{
  "command": "npx",
  "args": ["-y", "mcp-remote@latest", "https://mcp.atlassian.com/v1/mcp"]
}
```

### 2. Playwright

- **Paquete:** `@playwright/mcp@latest`
- **Tipo:** Local MCP (npx)
- **Propósito:** Automatización de navegador para tests E2E, navegación, screenshots, interacción con elementos web
- **Auto-approve:** `browser_snapshot`, `browser_take_screenshot`
- **Herramientas principales:** `browser_navigate`, `browser_click`, `browser_snapshot`, `browser_take_screenshot`, `browser_type`, `browser_evaluate`, `browser_network_requests`, `browser_console_messages`

```json
{
  "command": "npx",
  "args": ["-y", "@playwright/mcp@latest"]
}
```

### 3. Chrome DevTools

- **Paquete:** `chrome-devtools-mcp@latest`
- **Tipo:** Local MCP (npx)
- **Propósito:** Inspección profunda del navegador — performance traces, Lighthouse audits, heap snapshots, network analysis, console messages
- **Auto-approve:** ninguno
- **Herramientas principales:** `take_snapshot`, `take_screenshot`, `navigate_page`, `click`, `fill`, `lighthouse_audit`, `performance_start_trace`, `performance_stop_trace`, `take_memory_snapshot`, `list_network_requests`, `list_console_messages`

```json
{
  "command": "npx",
  "args": ["-y", "chrome-devtools-mcp@latest"]
}
```

### 4. Microsoft Clarity

- **Paquete:** `@microsoft/clarity-mcp-server`
- **Tipo:** Local MCP (npx)
- **Propósito:** Analytics de comportamiento de usuarios — sesiones, heatmaps, dead clicks, rage clicks, métricas de UX, documentación de Clarity
- **Auto-approve:** ninguno
- **Herramientas principales:** `query_analytics_dashboard`, `list_session_recordings`, `query_documentation_resources`

```json
{
  "command": "npx",
  "args": ["-y", "@microsoft/clarity-mcp-server"]
}
```

### 5. Datadog

- **Binario:** `datadog_mcp_cli.exe` (instalación local)
- **Tipo:** Binario local
- **Propósito:** Observabilidad — métricas, logs, traces, monitores, incidentes, dashboards, servicios, spans APM
- **Auto-approve:** ninguno
- **Herramientas principales:** `get_datadog_metric`, `search_datadog_logs`, `analyze_datadog_logs`, `search_datadog_monitors`, `search_datadog_incidents`, `search_datadog_spans`, `aggregate_spans`, `search_datadog_services`, `search_datadog_dashboards`
- **Nota:** Requiere instalación del CLI de Datadog. No es un paquete npm.

```json
{
  "command": "{RUTA_LOCAL}/datadog_mcp_cli.exe",
  "args": []
}
```

### 6. Draw.io

- **Paquete:** `@drawio/mcp`
- **Tipo:** Local MCP (npx)
- **Propósito:** Creación y edición de diagramas — arquitectura, flujos, organigramas, secuencia. Soporta XML, CSV y Mermaid
- **Auto-approve:** ninguno
- **Herramientas principales:** `open_drawio_xml`, `open_drawio_csv`, `open_drawio_mermaid`

```json
{
  "command": "npx",
  "args": ["-y", "@drawio/mcp"]
}
```

### 7. Fetch (Deshabilitado)

- **Paquete:** `mcp-server-fetch` (via uvx)
- **Nivel:** Global (`~/.kiro/settings/mcp.json`)
- **Estado:** ❌ Deshabilitado
- **Propósito:** Fetch de contenido web (reemplazado por herramientas nativas de Kiro)

### 8. Figma (Power)

- **URL:** `https://mcp.figma.com/mcp`
- **Tipo:** HTTP MCP (instalado como Power de Kiro)
- **Nivel:** Global (`~/.kiro/settings/mcp.json` → sección `powers`)
- **Propósito:** Integración con Figma para implementar diseños como código, Code Connect, reglas de design system

---

## Configuración por IDE

### Kiro (Workspace) — `.kiro/settings/mcp.json`

Contiene los 6 MCPs principales: Atlassian, Playwright, Chrome DevTools, Clarity, Datadog, Draw.io.

### Kiro (Global) — `~/.kiro/settings/mcp.json`

Contiene Fetch (deshabilitado) y Figma Power.

### Cursor — `.cursor/mcp.json`

Contiene Chrome DevTools y Clarity (subconjunto del workspace Kiro).

---

## Cómo replicar en otro entorno

1. Copiar `.kiro/settings/mcp.example.json` → `.kiro/settings/mcp.json`
2. Agregar Datadog: instalar `datadog_mcp_cli` y actualizar la ruta del binario
3. Agregar Draw.io: añadir la entrada de `@drawio/mcp`
4. Para Figma: instalar el Power desde el panel de Powers de Kiro
5. Autenticar Atlassian: al primer uso, `mcp-remote` abrirá el flujo OAuth

---

## Relación con el Swarm de Agentes

Cada MCP está asignado a agentes específicos según el mapa del Orquestador (`00-swarm-orchestrator.md`). Los hooks de enforcement en `.kiro/hooks/` validan que solo el agente autorizado use cada MCP.

| MCP | Agente(s) | Hook de enforcement |
|-----|-----------|---------------------|
| Atlassian | Scout, PO-Agile, Cloud Agent Datadog Alert | `atlassian-write-guard` |
| Playwright | Guardian | `playwright-mcp-guard` |
| Chrome DevTools | Guardian | `chrome-devtools-guard` |
| Clarity | Clarity Behavior | `clarity-mcp-guard` |
| Datadog | Cloud Agent Datadog Alert | `datadog-mcp-guard` |
| Draw.io | Doc Updater | `drawio-mcp-guard` |
| GitHub | GitHub Repos, Cloud Agent Datadog Alert | `github-mcp-guard` |
