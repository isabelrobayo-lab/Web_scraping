# Documentación del proyecto SQUAD-AGENTES-IA

> **Archivo de contexto principal para IA:** [resumen-proyecto.md](./resumen-proyecto.md)

---

## Estructura de docs

```
docs/
├── index.html              # Landing (GitHub Pages)
├── reportes.html           # Índice de reportes HTML
├── demo-agentes.html       # Demo visual del flujo de agentes (ver `npm run demo:agentes`)
├── README.md               # Este índice
├── resumen-proyecto.md     # Contexto principal para IA
├── ESTRUCTURA.md           # Estructura y lógica del proyecto (con diagrama de flujos)
├── diagrams/               # Estrategia de diagramas (Mermaid + Draw.io)
├── architecture/           # Diseño del sistema
│   ├── 0-overview.md
│   ├── 1-stack.md
│   ├── 2-design-system.md
│   ├── 3-tech-stack-org.md
│   ├── 4-workspace.md
│   ├── 5-agents-functional-architecture.md   # Agentes (visual, para negocio)
│   └── 6-inventario-agentes.md               # Inventario unificado de agentes (actualización)
├── Asset/                  # Plantillas CSS/HTML para reportes
├── onboarding/             # Flujo primera interacción
├── runbook/                # Guías operativas
├── decisions/              # ADRs
├── testing/                # Guías de testing (p. ej. vitest-cli.md)
├── analisis/               # Análisis y reportes MD
├── templates/              # Plantillas de config
├── data/                   # Datos de referencia (jira-cycle-*.json)
└── *.html                  # Reportes publicados (analisis-ciclo-desarrollo, etc.)
```

---

## Índice

### Diagramas (Mermaid + Draw.io)

Los diagramas están embebidos en Mermaid dentro de los documentos para renderizado en GitHub. Para editar versiones gráficas, usa el MCP `drawio-mcp` o [diagrams.net](https://app.diagrams.net/).

| Ubicación | Diagrama |
|-----------|----------|
| [ESTRUCTURA.md](./ESTRUCTURA.md) | Flujos integrados (config, E2E, auditoría, reportes, agentes) |
| [esquema-proyecto.md](./esquema-proyecto.md) | Esquema visual del proyecto (componentes, automation, config) |
| [onboarding/01-flujo-primera-interaccion.md](./onboarding/01-flujo-primera-interaccion.md) | Flujo de onboarding (validación MCPs/CLIs → platforms.json) |
| [onboarding/02-playwright-mcp-config.md](./onboarding/02-playwright-mcp-config.md) | Playwright MCP opcional en Cursor (complemento al CLI) |
| [architecture/4-workspace.md](./architecture/4-workspace.md) | Flujo de datos Workspace (generadores → carpetas → deploy) |
| [architecture/0-overview.md](./architecture/0-overview.md) | Separación código vs artefactos |
| [architecture/5-agents-functional-architecture.md](./architecture/5-agents-functional-architecture.md) | Equipo de agentes y fases del protocolo |
| [runbook/github-pages.md](./runbook/github-pages.md) | Flujo de publicación deploy:pages → GitHub Pages |

### Contexto y arquitectura

| Documento | Descripción |
|----------|-------------|
| [resumen-proyecto.md](./resumen-proyecto.md) | Contexto principal: stack, patrones, reglas, estructura |
| [ESTRUCTURA.md](./ESTRUCTURA.md) | Estructura del proyecto y flujos de lógica |
| [architecture/0-overview.md](./architecture/0-overview.md) | Visión general y estado del código |
| [architecture/1-stack.md](./architecture/1-stack.md) | Tecnologías y versiones del proyecto |
| [architecture/2-design-system.md](./architecture/2-design-system.md) | Sistema de diseño (tipografías, paleta, componentes) |
| [architecture/3-tech-stack-org.md](./architecture/3-tech-stack-org.md) | Ecosistema tecnológico de la organización |
| [architecture/4-workspace.md](./architecture/4-workspace.md) | Estructura del Workspace (resultados de agentes) |
| [architecture/5-agents-functional-architecture.md](./architecture/5-agents-functional-architecture.md) | **Arquitectura funcional de agentes** (visual, para negocio) |
| [architecture/6-inventario-agentes.md](./architecture/6-inventario-agentes.md) | **Inventario de agentes** (nombre, objetivo, MCPs, skills, archivos, prompt) |

### Onboarding

| Documento | Descripción |
|----------|-------------|
| [onboarding/01-flujo-primera-interaccion.md](./onboarding/01-flujo-primera-interaccion.md) | Flujo de primera interacción: validar MCPs/CLIs y crear platforms.json |
| [onboarding/02-playwright-mcp-config.md](./onboarding/02-playwright-mcp-config.md) | Configuración opcional de Playwright MCP (exploración interactiva) |
| [onboarding/02-compartir-proyecto-sin-github.md](./onboarding/02-compartir-proyecto-sin-github.md) | Cómo compartir el proyecto sin GitHub (para abrir en Cursor) |

### Runbooks

| Runbook | Descripción |
|---------|-------------|
| [runbook/automation-datadog-alert.md](./runbook/automation-datadog-alert.md) | Automatización Datadog → Cursor: validar alertas, plan y HU en Jira |
| [runbook/levantar-entorno-local.md](./runbook/levantar-entorno-local.md) | Cómo levantar el entorno local |
| [runbook/auditoria-proyecto.md](./runbook/auditoria-proyecto.md) | Cómo auditar el proyecto (errores de consola) |
| [runbook/github-pages.md](./runbook/github-pages.md) | Cómo publicar reportes en GitHub Pages |
| [runbook/migraciones.md](./runbook/migraciones.md) | Migraciones (placeholder; no aplica actualmente) |

### Decisiones técnicas (ADRs)

| Archivo | Título |
|---------|--------|
| [decisions/003-playwright-e2e.md](./decisions/003-playwright-e2e.md) | Por qué Playwright para E2E |

### Plantillas y datos

| Recurso | Uso |
|---------|-----|
| [templates/platforms.example.json](./templates/platforms.example.json) | Plantilla para `{WORKSPACE_ROOT}/config/platforms.json` |
| [templates/automation-datadog-alert-prompt.md](./templates/automation-datadog-alert-prompt.md) | Prompt para Cursor Automation (alertas Datadog → plan + HU) |
| [Asset/](./Asset/) | Plantillas CSS y HTML para reportes publicados en GitHub Pages |
| [data/jira-cycle-2025.json](./data/jira-cycle-2025.json) | Datos de referencia para reportes de ciclo |

### Análisis

| Documento | Descripción |
|----------|-------------|
| [analisis/analisis-ciclo-desarrollo.md](./analisis/analisis-ciclo-desarrollo.md) | Análisis de tiempo por fase del ciclo (Jira) |
| [analisis/ANALISIS_LIMPIEZA_PROYECTO.md](./analisis/ANALISIS_LIMPIEZA_PROYECTO.md) | Análisis histórico de limpieza (proyecto agnóstico) |

---

## Reportes HTML (GitHub Pages)

Los reportes publicados en `docs/` se sirven desde GitHub Pages. Ver [runbook/github-pages.md](./runbook/github-pages.md) para el flujo de publicación.

Las plantillas CSS y HTML reutilizables están en [Asset/](./Asset/).
