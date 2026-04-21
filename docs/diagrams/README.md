# Diagramas del proyecto

> Los diagramas están embebidos en los documentos fuente como **Mermaid**. Este directorio contiene la fuente persistente y los enlaces para abrir en Draw.io.

---

## 📋 Checklist de validación para el usuario

Antes de dar por válido un diagrama, verificar:

| # | Verificación | Referencia |
|---|--------------|------------|
| 1 | **Agentes** — Los 8 agentes están correctos y alineados con el inventario | [6-inventario-agentes.md](../architecture/6-inventario-agentes.md) |
| 2 | **Agnóstico vs Particular** — Flujos transversales vs acciones específicas del proyecto | [esquema-funcionamiento-agnostico](esquema-funcionamiento-agnostico.html), [esquema-acciones-particulares](esquema-acciones-particulares.html) |
| 3 | **Archivos** — Rutas de código, reglas y prompts son las actuales | Inventario + reglas en `.kiro/steering/` |
| 4 | **MCPs** — Datadog, Atlassian, GitHub usados según corresponda | Inventario sección MCPs por agente |

---

## Metadatos en diagramas

Cada diagrama incluye un bloque **📋 Metadatos** visible en Draw.io con:

| Campo | Descripción |
|-------|-------------|
| **Título** | Nombre del diagrama |
| **Objetivo** | Propósito o descripción breve |
| **Ruta archivo** | `docs/diagrams/[nombre].mmd` |

Los metadatos están en los archivos `.mmd`. Al abrir un `.html` o pegar el Mermaid en Draw.io, se mostrarán en la parte superior del diagrama.

---

## Persistencia

Los diagramas persisten en `docs/diagrams/` de dos formas:

| Formato | Archivo | Uso |
|---------|---------|-----|
| **Mermaid** | `*.mmd` | Fuente de verdad, versionable; copiar/pegar en Draw.io para editar |
| **HTML** | `*.html` | Enlace corto que redirige a Draw.io con el diagrama precargado |

Para editar y guardar cambios: abre el `.html`, en Draw.io usa **File → Save as** y guarda como `.drawio` en este directorio si quieres persistir la versión gráfica.

---

## Archivos persistentes

| Fuente (.mmd) | Enlace (.html) | Descripción |
|---------------|----------------|-------------|
| [flujo-estructura.mmd](./flujo-estructura.mmd) | [flujo-estructura.html](./flujo-estructura.html) | Flujos de configuración, E2E, auditoría, reportes y agentes |
| [flujo-onboarding.mmd](./flujo-onboarding.mmd) | [flujo-onboarding.html](./flujo-onboarding.html) | Flujo de onboarding (validación → platforms.json) |
| [flujo-workspace.mmd](./flujo-workspace.mmd) | [flujo-workspace.html](./flujo-workspace.html) | Generadores → Workspace → deploy |
| [flujo-github-pages.mmd](./flujo-github-pages.mmd) | [flujo-github-pages.html](./flujo-github-pages.html) | Flujo deploy:pages → GitHub Pages |
| [codigo-vs-artefactos.mmd](./codigo-vs-artefactos.mmd) | [codigo-vs-artefactos.html](./codigo-vs-artefactos.html) | Separación código vs artefactos |
| [equipo-agentes.mmd](./equipo-agentes.mmd) | [equipo-agentes.html](./equipo-agentes.html) | **8 agentes** (Orquestador, Scout, Historian, Guardian, GitHub Repos, PO-Agile, Doc Updater, Cloud Agent) |
| [4-fases-protocolo.mmd](./4-fases-protocolo.mmd) | [4-fases-protocolo.html](./4-fases-protocolo.html) | 4 fases del protocolo (Análisis → Validación) |
| [flujo-automation-datadog-alert.mmd](./flujo-automation-datadog-alert.mmd) | [flujo-automation-datadog-alert.html](./flujo-automation-datadog-alert.html) | Cloud Agent Datadog (6 pasos) |
| [esquema-proyecto-completo.mmd](./esquema-proyecto-completo.mmd) | [esquema-proyecto-completo.html](./esquema-proyecto-completo.html) | Esquema general del proyecto |
| [esquema-funcionamiento-agnostico.mmd](./esquema-funcionamiento-agnostico.mmd) | [esquema-funcionamiento-agnostico.html](./esquema-funcionamiento-agnostico.html) | Funcionamiento transversal del proyecto agnóstico |
| [esquema-acciones-particulares.mmd](./esquema-acciones-particulares.mmd) | [esquema-acciones-particulares.html](./esquema-acciones-particulares.html) | Acciones particulares del proyecto (datos en platforms.json) |
| — | [agentes-mcps-cli-skills-actividades.html](./agentes-mcps-cli-skills-actividades.html) | Vista HTML (no Mermaid): agentes ↔ MCP/CLI/skills + actividades; alinear con [6-inventario-agentes.md](../architecture/6-inventario-agentes.md) |

---

## Ubicación en documentos

| Documento | Enlace |
|-----------|--------|
| `../ESTRUCTURA.md` | `diagrams/flujo-estructura.html` |
| `../onboarding/01-flujo-primera-interaccion.md` | `diagrams/flujo-onboarding.html` |
| `../architecture/4-workspace.md` | `diagrams/flujo-workspace.html` |
| `../architecture/0-overview.md` | `diagrams/codigo-vs-artefactos.html` |
| `../architecture/5-agents-functional-architecture.md` | `diagrams/equipo-agentes.html`, `diagrams/4-fases-protocolo.html` |
| `../architecture/6-inventario-agentes.md` | Todos los diagramas de agentes; [agentes-mcps-cli-skills-actividades.html](./agentes-mcps-cli-skills-actividades.html) |
| `../runbook/github-pages.md` | `diagrams/flujo-github-pages.html` |
| `../runbook/automation-datadog-alert.md` | `diagrams/flujo-automation-datadog-alert.html` |
| `../esquema-proyecto.md` | `diagrams/esquema-proyecto-completo.mmd` |
| `../esquema-proyecto.md` | `diagrams/esquema-funcionamiento-agnostico.html`, `diagrams/esquema-acciones-particulares.html` |
| `.kiro/steering/03-validacion-agnostico-particular.mdc` | `diagrams/esquema-funcionamiento-agnostico.html`, `diagrams/esquema-acciones-particulares.html` |

---

## Cómo editar en Draw.io

1. **Enlace corto:** Cada documento incluye una nota con el enlace **[Abrir en Draw.io]** que apunta a un archivo HTML con nombre descriptivo (ej. `flujo-workspace.html`). La página redirige automáticamente a Draw.io con el diagrama.
2. **Desde Cursor:** Pide al agente que use el skill `diagramas-drawio` o el MCP `drawio-mcp` con el contenido Mermaid del documento.
3. **Manual:** Copia el bloque Mermaid del `.mmd` y pégalo en [diagrams.net](https://app.diagrams.net/) → Arrange → Insert → Advanced → Mermaid.
4. **Exportar:** File → Export as → .drawio para guardar en este directorio si lo deseas.
5. **Tras actualizar .mmd:** Regenera los `.html` con `npm run diagrams:regenerate-html`. El script codifica cada `.mmd` (deflate+base64) y genera los enlaces a Draw.io.
