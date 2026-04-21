# Esquema del proyecto SQUAD-AGENTES-IA

> Vista general de componentes, flujos y configuraciones.

---

## Diagrama principal

```mermaid
flowchart TB
    subgraph proyecto ["Proyecto SQUAD-AGENTES-IA"]
        subgraph codigo ["Código fuente"]
            tests[tests/]
            scripts[scripts/]
            tools[tools/scripts/]
            docs[docs/]
            cursorRules[.kiro/steering/]
        end

        subgraph workspace ["Workspace - artefactos (.gitignore)"]
            platformsJson["platforms.json en WORKSPACE_ROOT/config/"]
            plans[plans/]
            reports[reports/]
            audit[audit/]
            observabilidad[observabilidad/]
        end
    end

    subgraph platformsConfig ["platforms.json (ejemplo: una plataforma configurada)"]
        jiraConfig[Jira projectKey + tableros]
        datadogConfig[Datadog site + dashboards]
        serviceToRepos[serviceToRepos]
        githubRepos[github.repos]
    end

    subgraph automation ["Automation Datadog Alert"]
        trigger[Schedule cada 15 min]
        p0[P0: search status:alert]
        p1[P1: Validar servicios]
        p2[P2: Consultar repos]
        p3[P3: Generar plan]
        p4[P4: Buscar HU]
        p5[P5: Crear HU]
    end

    subgraph mcps ["MCPs"]
        mcpDatadog[Datadog]
        mcpAtlassian[Atlassian]
        mcpGitHub[GitHub]
    end

    subgraph externos ["Externos"]
        datadog[Datadog]
        jira[Jira]
        github[GitHub]
    end

    platformsJson --> platformsConfig
    serviceToRepos --> p2
    githubRepos --> p2

    trigger --> p0
    p0 --> p1
    p1 --> p2
    p2 --> p3
    p3 --> p4
    p4 --> p5

    p0 --> mcpDatadog
    p1 --> mcpDatadog
    p2 --> mcpGitHub
    p4 --> mcpAtlassian
    p5 --> mcpAtlassian

    mcpDatadog --> datadog
    mcpAtlassian --> jira
    mcpGitHub --> github

    p3 --> plans
```

> **Editar en Draw.io:** Abre [diagrams.net](https://app.diagrams.net) → Arrange → Insert → Advanced → Mermaid, y pega el contenido de [diagrams/esquema-proyecto-completo.mmd](../diagrams/esquema-proyecto-completo.mmd).

### Diagramas de análisis: Agnóstico vs Particular

| Diagrama | Descripción |
|----------|-------------|
| [Esquema funcionamiento agnóstico](./diagrams/esquema-funcionamiento-agnostico.html) | Flujos transversales: onboarding, E2E, auditoría, reportes, agentes |
| [Esquema acciones particulares](./diagrams/esquema-acciones-particulares.html) | Acciones específicas del proyecto: Automation Datadog, Jira, serviceToRepos (datos en platforms.json) |

---

## Resumen por capa

| Capa | Componentes |
|------|-------------|
| **Código** | tests/, scripts/, tools/scripts/, miniverse/, docs/, .kiro/steering/ |
| **Workspace** | Por producto bajo `Workspace/<nombre>/`: `config/platforms.json`, `plans/`, `reports/`, `audit/`, `observabilidad/`, `playwright/`, etc. (ver `docs/architecture/4-workspace.md`) |
| **Config** | Por plataforma en platforms.json (Jira, Datadog, serviceToRepos, github.repos) |
| **Automation** | Schedule → 6 pasos (MCP Datadog → validar → repos → plan → Jira) |
| **MCPs** | Datadog, Atlassian, GitHub |
| **Externos** | Datadog, Jira, GitHub |

---

## Flujos principales

| Flujo | Entrada | Salida |
|-------|---------|--------|
| **Automation Datadog** | Schedule + MCP Datadog `status:alert` | plan en plans/, HU en Jira |
| **Tests E2E** | platforms.json (baseURL, smokePaths) | playwright report |
| **Auditoría** | platforms.json (auditZones) | Workspace/audit/ |
| **Reportes** | jira-cycle-*.json | Workspace/reports/ → deploy:pages |

---

## Ejemplo de configuración local (no versionada)

Los valores concretos viven en `{WORKSPACE_ROOT}/config/platforms.json` (`.gitignore`; ver `docs/architecture/4-workspace.md`). La plantilla puede rellenarse así (los números pueden cambiar según el JSON):

| Sección | Ejemplo de contenido |
|---------|----------------------|
| **Jira** | projectKey, URLs de proyecto, tableros de incidentes y seguridad |
| **Datadog** | site (`us1`, etc.), IDs de dashboards, `serviceToRepos` |
| **serviceToRepos** | Mapa servicio Datadog → repos GitHub (varias entradas) |
| **github.repos** | Lista de repos de la plataforma bajo la org configurada |

---

## Referencias

- [ESTRUCTURA.md](./ESTRUCTURA.md) — Árbol de directorios
- [runbook/automation-datadog-alert.md](./runbook/automation-datadog-alert.md) — Flujo de automation
- [architecture/0-overview.md](./architecture/0-overview.md) — Visión general
