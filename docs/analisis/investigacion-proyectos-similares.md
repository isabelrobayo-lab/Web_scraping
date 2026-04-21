# Investigación: Proyectos similares a SQUAD-AGENTES-IA

> **Fecha:** 23 marzo 2025  
> **Objetivo:** Identificar mejores prácticas y posibles evoluciones para la iniciativa de workspace agnóstico con orquestación de agentes IA.

---

## Resumen ejecutivo

Esta investigación analiza proyectos y frameworks alineados con **SQUAD-AGENTES-IA**: workspace agnóstico, pruebas E2E, auditoría, integración Jira/Datadog/GitHub vía MCP, y equipo de agentes (Scout, Historian, Guardian, PO-Agile). Se identifican **6 áreas de evolución** priorizables.

---

## 1. Proyectos comparables

### 1.1 PO Agent (ideyaLabs) — Agente PO autónomo

**Enfoque:** "Vision to Strategy" — transforma ideas en backlogs y documentación ejecutable.

| Aspecto | PO Agent | SQUAD-AGENTES-IA |
|---------|----------|------------------|
| Integración Jira/Confluence | ✅ One-click export | ✅ MCP Atlassian |
| Documentación automática | BRD, PRD, FRD, SRS | docs/ + runbooks |
| Backlog / Historias de Usuario | Decomposición automática | PO-Agile (INVEST, Dado-Cuando-Entonces) |
| Diagramas | Flowcharts, mind maps, MoSCoW | Draw.io MCP |
| Fases | 9 fases (Research → Approval) | 4 fases (Análisis → Validación) |
| Human-in-the-Loop | Gates de aprobación | Plan en Workspace/plans/ antes de código |

**Práctica adoptable:** Fases explícitas de "Approval/Review" antes de implementación, con trazabilidad a stakeholders.

---

### 1.2 APOX (AI Product Orchestration eXtended)

**Enfoque:** Orquestación multi-agente con agentes especializados por etapa (PRD, PO, UX, UI, Architect, Developer, Implementation, Coding).

| Aspecto | APOX | SQUAD-AGENTES-IA |
|---------|------|------------------|
| Agentes especializados | 8+ (PRD, PO, UX, Architect…) | Scout, Historian, Guardian, PO-Agile, Doc Updater |
| Gates humanos | Obligatorios en cada etapa | Implícito en planificación |
| Auditoría | Trazabilidad de prompts y outputs | Workspace/plans/, reportes ciclo |

**Práctica adoptable:** Gates explícitos de confirmación humana entre fases críticas; registro de prompts/outputs para auditoría.

---

### 1.3 AWS Multi-Agent Orchestrator

**Enfoque:** Infraestructura para gestionar múltiples agentes con clasificación de intenciones, contexto entre conversaciones y despliegue flexible.

| Aspecto | AWS MAO | SQUAD-AGENTES-IA |
|---------|---------|------------------|
| Idiomas | Python, TypeScript | Node.js / JavaScript |
| Despliegue | Lambda, local, cloud | Local + scripts |
| Contexto | Entre conversaciones | Workspace/plans/, platforms.json |

**Práctica adoptable:** Evaluar uso de clasificación de intenciones para enrutar tareas al agente adecuado (Scout vs Historian vs Guardian).

---

### 1.4 AgentX (Harness-Oriented Architecture)

**Enfoque:** Enrutamiento a ~20 agentes especializados con fases Plan → Execute → Iterate → Review → Validate.

| Aspecto | AgentX | SQUAD-AGENTES-IA |
|---------|--------|------------------|
| Fases | Plan, Execute, Iterate, Review, Validate | Análisis, Contexto, Planificación, Validación |
| Skills | 69 skills (arquitectura, AI, dev, ops) | MCPs: Atlassian, Datadog, GitHub, Draw.io |
| Validación | Integrada en flujo | Guardian + Playwright |

**Práctica adoptable:** Fase explícita de "Review" post-implementación (antes de Guardian) para revisión de código generado.

---

### 1.5 Agent² y Multi-Agent Coordination MCP

**Enfoque:** Orquestación de agentes en Cursor/IDEs vía MCP.

| Proyecto | Característica | Aplicabilidad |
|----------|----------------|----------------|
| **Agent²** | Pipeline: decompose → optimize → execute → validate | Reforzar fase de validación con agentes especializados |
| **Multi-Agent Coordination MCP** | File locking, dependencias, Projects → Tasks → Todos | Evitar conflictos cuando múltiples agentes toquen el mismo codebase |

**Práctica adoptable:** Considerar MCP de coordinación para tareas complejas donde intervienen Scout + Historian + Guardian en paralelo.

---

### 1.6 Spec Kit (GitHub) — Spec-Driven Development

**Enfoque:** Especificación como fuente de verdad; comandos estructurados (`/specify`, `/plan`, `/tasks`, `/implement`).

| Aspecto | Spec Kit | SQUAD-AGENTES-IA |
|---------|----------|------------------|
| SDD | ✅ Especificación ejecutable | ✅ Spec Driven Development (PRD → plan → código) |
| Comandos | /specify, /plan, /tasks, /implement | Plan en Workspace/plans/ antes de código |
| Integración | Cursor, Claude, Copilot, Windsurf | Cursor + reglas .cursorrules |
| Clarificación | /clarify antes de /plan | Implícito en fases Scout/Historian |
| Análisis | /analyze (cobertura, consistencia) | Auditoría consola, reportes ciclo |

**Práctica adoptable:**  
- Comando `/clarify` explícito antes de planificación para resolver ambigüedades.  
- `/analyze` para verificar consistencia cross-artifact (spec vs plan vs código).

---

### 1.7 ChatPRD y SpecWeave

| Proyecto | Característica | Aplicabilidad |
|----------|----------------|----------------|
| **ChatPRD** | PRD en IDE vía MCP; criterios de aceptación, edge cases | PO-Agile podría enriquecer HUs con edge cases explícitos |
| **SpecWeave** | /sw:increment, /sw:auto, /sw:done para shipping autónomo | Inspiración para flujo de "done" con validación y deploy |

---

### 1.8 Playwright Test Agents (Planner, Generator, Healer)

**Enfoque:** Agentes nativos de Playwright (v1.56+) para explorar apps, generar tests y reparar fallos.

| Agente | Función | Relación con SQUAD-AGENTES-IA |
|--------|---------|------------------------------|
| **Planner** | Explora la app y crea planes de tests en Markdown | Complementa smoke tests actuales; descubre escenarios |
| **Generator** | Convierte planes en tests TypeScript ejecutables | Posible evolución: tests generados desde spec/plan |
| **Healer** | Detecta y corrige tests rotos por cambios de UI | Reduce mantenimiento de selectores; alinea con Guardian |

**Práctica adoptable:**  
- Evaluar Planner para ampliar cobertura de smoke tests de forma guiada por IA.  
- Healer como complemento al Guardian para auto-reparación de tests E2E.

---

## 2. Patrones de orquestación multi-agente (2024-2026)

### 2.1 Patrones identificados

| Patrón | Descripción | Uso en SQUAD-AGENTES-IA |
|--------|-------------|-------------------------|
| **Hub-and-Spoke (Supervisor)** | Orquestador central coordina agentes | ✅ Orquestador actual (00-swarm-orchestrator) |
| **Pipeline (Secuencial)** | Agentes en secuencia, cada uno refina output | ✅ 4 fases: Análisis → Contexto → Planificación → Validación |
| **Peer-to-Peer** | Agentes en paralelo, mínima coordinación | Parcial (GitHub Repos + Doc Updater pueden operar en paralelo) |
| **Hierárquico** | Managers dirigen especialistas en niveles | Posible evolución para equipos grandes |

### 2.2 Primitivos de diseño recomendados

1. **Message passing:** Instrucciones y resultados entre agentes — actualmente implícito en fases.
2. **State management:** Orquestador dueño del estado; agentes stateless — Workspace/plans/ y platforms.json cumplen.
3. **Error handling:** Detección y recuperación de fallos — reforzar con retry y fallback entre fases.
4. **Monitoring:** Latencia, coste, corrección — Datadog + reportes ciclo ya presentes.

---

## 3. Mejores prácticas identificadas

| Práctica | Fuente | Aplicabilidad |
|----------|--------|----------------|
| Gates humanos obligatorios entre fases críticas | APOX, PO Agent | Añadir checkpoint explícito post-planificación |
| Clarificación estructurada antes de planificar | Spec Kit | `/clarify` o equivalente en flujo PO |
| Auditoría de prompts y outputs | APOX | Log de decisiones en Workspace/ para trazabilidad |
| Análisis cross-artifact (spec vs plan vs código) | Spec Kit | Script o skill de consistencia |
| File locking / coordinación multi-agente | Multi-Agent Coordination MCP | Para tareas paralelas complejas |
| Playwright Planner/Healer nativos | Playwright | Extender cobertura E2E y auto-reparación |
| Locators basados en accesibilidad (role, label) | Playwright best practices | Revisar smoke tests actuales |
| Mock de dependencias externas en tests | Playwright | Evitar flakiness por servicios terceros |

---

## 4. Posibles evoluciones priorizadas

### 4.1 Corto plazo (1-3 meses)

1. **Fase de clarificación explícita**  
   Antes de generar el plan en `Workspace/plans/`, el Orquestador pregunta al usuario para resolver ambigüedades (similar a Spec Kit `/clarify`).

2. **Revisión de locators en Playwright**  
   Priorizar selectores por rol y label (accesibilidad) en `tests/smoke.spec.js` y `tests/miniverse.spec.js` según mejores prácticas.

3. **Evaluar Playwright Healer**  
   Si está disponible en la versión actual, documentar uso para auto-reparación de tests rotos.

### 4.2 Medio plazo (3-6 meses)

4. **Checkpoint de aprobación humana**  
   Gate explícito tras planificación: "¿Apruebas este plan antes de que Guardian ejecute?" — con opción de editar o rechazar.

5. **Integración Spec Kit (opcional)**  
   Si el equipo adopta Spec Kit, alinear comandos `/specify`, `/plan`, `/tasks` con el flujo actual de Workspace/plans/.

6. **Análisis de consistencia cross-artifact**  
   Script o skill que verifique: spec/PRD ↔ plan en Workspace/plans/ ↔ criterios de aceptación en Jira ↔ tests implementados.

### 4.3 Largo plazo (6+ meses)

7. **Playwright Planner para descubrimiento de escenarios**  
   Usar Planner para explorar la app y proponer nuevos smoke paths basados en uso real.

8. **MCP de coordinación multi-agente**  
   Para tareas donde Scout, Historian y Guardian trabajen en paralelo con file locking y gestión de dependencias.

9. **Enriquecimiento de HUs con edge cases**  
   PO-Agile podría incorporar edge cases explícitos en criterios de aceptación (inspiración ChatPRD).

---

## 5. Referencias

| Recurso | URL / Fuente |
|---------|--------------|
| PO Agent (ideyaLabs) | https://ideyalabs.com/agent/po-agent/ |
| Spec Kit (GitHub) | https://speckit.org/ , https://github.com/github/spec-kit |
| Agent² (agent-squared) | https://github.com/alexhatzo/agent-squared |
| Multi-Agent Coordination MCP | https://github.com/AndrewDavidRivers/multi-agent-coordination-mcp |
| Playwright Best Practices | https://playwright.dev/docs/next/best-practices |
| Multi-Agent Orchestration Patterns | Collabnix, Amir Brooks, Fast.io (2024-2026) |
| MCP Ecosystem | mcp-toolbox.com, Anthropic MCP docs |
| ChatPRD | https://www.chatprd.ai/ |
| SpecWeave | https://spec-weave.com/ |

---

## 6. Conclusión

**SQUAD-AGENTES-IA** está bien alineado con las tendencias actuales en:
- Orquestación multi-agente (Hub-and-Spoke + Pipeline)
- Spec Driven Development
- Integración MCP (Jira, Datadog, GitHub, Draw.io)
- Validación automática con Playwright

Las evoluciones más impactantes y de menor esfuerzo son: **(1) fase de clarificación**, **(2) checkpoint de aprobación humana**, **(3) revisión de locators por accesibilidad**, **(4) evaluación de Playwright Healer** y **(5) análisis de consistencia cross-artifact**.

---

*Documento generado en el marco de la investigación de proyectos similares para la iniciativa SQUAD-AGENTES-IA.*
