---
inclusion: always
---

# Validación: Agnóstico vs Particular

Antes de implementar o documentar una **acción nueva**, el agente **debe validar con el usuario**:

## Pregunta obligatoria

> **"¿Esta acción debe ser transversal (agnóstica) para cualquier plataforma, o es específica del proyecto actual (ej. Ciencuadras)?"**

## Criterios de clasificación

| Tipo | Ubicación | Ejemplos |
|------|-----------|----------|
| **Transversal (agnóstico)** | Código fuente, docs genéricos, templates | `get-platform-config.js`, `platforms.example.json`, flujos de onboarding, tests E2E genéricos |
| **Particular** | `Workspace/config/`, runbooks específicos, automation con datos concretos | `platforms.json` con project keys de Jira, Automation Datadog con serviceToRepos, `jira-cycle-*.json` |

## Regla de decisión

- **Transversal**: Se añade al código versionado, usa config desde `platforms.json`, no hardcodea URLs/proyectos.
- **Particular**: Se documenta en runbooks o config; los datos viven en `Workspace/config/platforms.json` o `docs/data/`.

## No continuar sin confirmación

Si el usuario no responde, **preguntar explícitamente** antes de:
- Añadir scripts que asuman un proyecto Jira concreto
- Crear automatizaciones con IDs de tablero o dashboards fijos
- Documentar flujos que dependan de un producto específico

## Referencias

- Diagramas: `docs/diagrams/esquema-funcionamiento-agnostico.html`, `docs/diagrams/esquema-acciones-particulares.html`
- Config: `docs/templates/platforms.example.json`, `Workspace/config/platforms.json`
