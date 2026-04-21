# Análisis de Limpieza — Proyecto Agnóstico

> **Estado:** Histórico — Limpieza completada. El proyecto es agnóstico.  
> **Objetivo:** Identificar archivos a eliminar o modificar para tener un proyecto agnóstico, sin historial de pruebas realizadas (Jelpit, Seguros Bolívar, etc.).

**Nota:** La estructura actual difiere en parte: las reglas de agentes viven en `.kiro/steering/` y `rules/`; los planes en `Workspace/plans/`. Ver [resumen-proyecto.md](../resumen-proyecto.md) y [architecture/4-workspace.md](../architecture/4-workspace.md).

---

## 1. Archivos a ELIMINAR (historial de pruebas y artefactos generados)

| Archivo/Carpeta                                    | Motivo                                                                                   |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `tests/jelpit-botones.spec.js`                     | Test específico para jelpit.com (validación de botones, screenshots)                     |
| `tests/jelpit-status.spec.js`                      | Test específico para verificar estado de jelpit.com                                      |
| `scripts/ver-pagina.js`                            | Script que abre jelpit.com en el navegador                                               |
| `reporte-visual/` (carpeta completa)               | Reportes HTML y screenshots generados de pruebas en jelpit.com                           |
| `test-results/` (carpeta completa)                 | Resultados de ejecución de Playwright (`.last-run.json`, etc.)                           |
| `PLAN_DE_TRABAJO.md`                               | Plan específico de JELHRC-21371 (Jelpit Conjuntos, Jelpit Pagos)                         |
| `ANALISIS_INCIDENTES_NOTIFICACIONES_JUDICIALES.md` | Análisis específico de incidentes Portal Libertador / Seguros Bolívar                    |
| `CURSOR_RULES_ALIGNMENT.md`                        | Alineación de reglas con index.html, header y componentes específicos de Seguros Bolívar |

---

## 2. Archivos a MODIFICAR (hacer agnósticos)

### 2.1 `package.json`

**Problema:** Scripts específicos de Jelpit.

```json
// ELIMINAR o reemplazar:
"test:jelpit": "playwright test jelpit-status",
"test:botones": "playwright test jelpit-botones",
"reporte:abrir": "open reporte-visual/reporte-botones.html",
"ver:jelpit": "node scripts/ver-pagina.js"
```

**Acción:** Dejar solo `"test": "playwright test"` o definir scripts genéricos si se mantiene estructura de tests.

---

### 2.2 `rules/.cursorrules`

**Problema:** Referencias explícitas a:

- "Grupo Bolívar Multi-Company API Portal"
- "Seguros Bolívar, El Libertador, Servicios Bolívar, Agencia Proyectiva"
- "Jelpit" en el Design System
- DESIGN_SYSTEM.md con marcas específicas

**Acción:** Reemplazar por contexto genérico (ej: "Portal API multi-empresa", "Design System con soporte multi-marca") o dejar plantilla vacía para que el usuario defina su contexto.

---

### 2.3 `rules/workflow-01-implementar.mdc`

**Problema:** 843 líneas específicas de "Seguros Bolívar UI", componentes `sb-ui-*`, marcas (Seguros Bolívar, Jelpit, etc.), URLs CDN de `seguros-bolivar-ui`.

**Acción:**

- **Opción A:** Eliminar si el proyecto no usará esa librería.
- **Opción B:** Convertir en plantilla genérica (placeholders para marca, componentes, CDN).

---

### 2.4 `rules/componentes-01-sb-ui.mdc`

**Problema:** Guía completa del Seguros Bolívar UI Design System (sb-ui-button, sb-ui-select, etc.).

**Acción:** Eliminar si no se usará SB UI. Si se quiere mantener un design system genérico, crear una versión abstracta sin referencias a sb-ui-\*.

---

### 2.5 `rules/CSS.mdc`

**Problema:** Referencias a 6 marcas: White Label, Jelpit, Davivienda, Cien Cuadras, Doctor Aki, Seguros Bolívar.

**Acción:** Generalizar a "marcas del design system" o eliminar nombres específicos.

---

### 2.6 `rules/variables-01-css.mdc`

**Problema:** Ejemplo con "Seguros Bolívar" en fuentes.

**Acción:** Reemplazar por ejemplo genérico.

---

### 2.7 `rules/AGENTS.md`

**Problema:** Menor. Menciona Jira, Git, Playwright, Datadog — herramientas genéricas. Las citas `[cite: ...]` pueden ser de un contexto anterior.

**Acción:** Revisar y quitar citas si apuntan a conversaciones específicas. El contenido es bastante agnóstico.

---

## 3. Archivos a MANTENER (ya agnósticos o reutilizables)

| Archivo                              | Motivo                                                             |
| ------------------------------------ | ------------------------------------------------------------------ |
| `playwright.config.js`               | Configuración genérica de Playwright                               |
| `rules/tech-playwright.mdc`          | Reglas genéricas de calidad y validación con Playwright            |
| `rules/tech-datadog.mdc`             | Instrucciones genéricas de observabilidad                          |
| `rules/skill-github-analyzer.mdc`    | Protocolo de analista genérico (mapeo arquitectura, viabilidad)    |
| `rules/process-prd-generation.mdc`   | Estándar de documentación PRD (SPECDD)                             |
| `rules/01-technical-feasibility.mdc` | Casi vacío, agnóstico                                              |
| `rules/skill-playwright.mdc`         | Reglas de Playwright                                               |
| `.kiro/settings/mcp.json`                   | Configuración de MCP (Datadog, Atlassian) — herramientas genéricas |

---

## 4. Resumen de acciones recomendadas

| Categoría     | Cantidad                    | Acción                                              |
| ------------- | --------------------------- | --------------------------------------------------- |
| **Eliminar**  | 8 items (archivos/carpetas) | Borrar completamente                                |
| **Modificar** | 7 archivos                  | Hacer agnósticos o eliminar referencias específicas |
| **Mantener**  | 8+ archivos                 | Sin cambios                                         |

---

## 5. Estructura sugerida post-limpieza

```
SQUAD-AGENTES-IA/
├── .kiro/
│   └── settings/mcp.json
├── rules/
│   ├── .cursorrules          # Modificado: contexto genérico
│   ├── AGENTS.md              # Revisar citas
│   ├── tech-playwright.mdc
│   ├── tech-datadog.mdc
│   ├── skill-github-analyzer.mdc
│   ├── process-prd-generation.mdc
│   └── 01-technical-feasibility.mdc
├── tests/                     # Vacío o con tests de ejemplo genéricos
├── package.json               # Modificado: scripts genéricos
├── playwright.config.js
└── node_modules/
```

**Opcional:** Si se eliminan `workflow-01-implementar.mdc`, `componentes-01-sb-ui.mdc`, `CSS.mdc` y `variables-01-css.mdc`, el proyecto queda como plantilla de agente PO + Playwright + Datadog + Atlassian, sin dependencia de Seguros Bolívar UI.

---

## 6. Nota sobre `.gitignore`

No existe `.gitignore`. Se recomienda crear uno con:

```
node_modules/
test-results/
reporte-visual/screenshots/
reporte-visual/*.html
.env
*.log
```

Así se evita versionar artefactos generados y dependencias.
