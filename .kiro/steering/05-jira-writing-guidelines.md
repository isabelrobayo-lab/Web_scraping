---
inclusion: always
---
# Lineamientos de Escritura en Jira — Agentes Scout y PO-Agile

Reglas obligatorias para todo agente que cree o edite issues en Jira vía MCP Atlassian.

---

## 1. Consultar metadata ANTES de crear

Antes del primer `createJiraIssue` en un proyecto, **siempre** invocar:

```
getJiraIssueTypeMetaWithFields(projectIdOrKey, issueTypeId)
```

Esto devuelve los campos requeridos, sus tipos (`string`, `option`, `cmdb-object-field`, etc.) y los `allowedValues`. No asumir que `summary` + `description` son suficientes — cada proyecto puede tener campos obligatorios adicionales.

**Flujo correcto:**
1. `getJiraProjectIssueTypesMetadata` → obtener el `id` del tipo de issue (ej. Historia = 11001).
2. `getJiraIssueTypeMetaWithFields(project, issueTypeId)` → listar campos requeridos y sus schemas.
3. Preparar el payload con todos los campos `required: true`.
4. `createJiraIssue` con el payload completo.

---

## 2. Campos obligatorios conocidos (ejemplo de referencia)

La siguiente tabla documenta campos obligatorios descubiertos en proyectos del workspace. Sirve como **caché de referencia** para evitar llamadas repetidas a `getJiraIssueTypeMetaWithFields`, pero **no reemplaza** el paso 1 — siempre verificar si el proyecto destino tiene campos adicionales.

| Proyecto (ejemplo) | Campo | customfield | Tipo | Notas |
|---------------------|-------|------------|------|-------|
| Ciencuadras & Ecosistema Home | Enfoque de Historia | `customfield_13801` | `option` (select) | Valores: Técnica, Funcional, Ciberseguridad, Obsolescencia, Normativo Externo, Normativo Interno |
| Ciencuadras & Ecosistema Home | Criterios de aceptación | `customfield_10332` | `ADF` (rich text) | **NO acepta texto plano ni markdown.** Debe ser JSON ADF. Ver sección 3. |
| Ciencuadras & Ecosistema Home | Aplicación Impactada - CMDB | `customfield_31136` | `cmdb-object-field` | Requiere `workspaceId` + `objectId`. Consultar issues hermanas para obtener el valor correcto. |

> **Importante:** Cada proyecto Jira puede tener campos obligatorios distintos. Siempre ejecutar el paso 1 para descubrirlos antes de la primera creación.

---

## 3. Formato ADF para campos rich-text

Jira rechaza texto plano en campos de tipo `textarea` que esperan Atlassian Document Format. El formato correcto es:

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {
          "type": "text",
          "text": "Texto del párrafo",
          "marks": [{"type": "strong"}]
        }
      ]
    }
  ]
}
```

**Reglas ADF:**
- Cada párrafo es un objeto `{"type": "paragraph", "content": [...]}`.
- Texto en negrita: agregar `"marks": [{"type": "strong"}]` al nodo de texto.
- Saltos de línea dentro de un párrafo: usar `\n` en el string o nodos `{"type": "hardBreak"}`.
- No usar HTML ni markdown dentro del ADF.

**Campos que requieren ADF (verificar por proyecto con `getJiraIssueTypeMetaWithFields`):**
- `customfield_10332` (Criterios de aceptación) — ejemplo conocido; cada proyecto puede tener campos distintos.

**Campos que aceptan markdown** (vía `contentFormat: "markdown"`):
- `description` (Descripción)
- `commentBody` (Comentarios)

---

## 4. Prefijo "Creado con IA"

Al crear issues en Jira, el texto **"Creado con IA"** debe ir en la **descripción**, nunca en el título/summary.

---

## 5. Evidencias gráficas obligatorias

Toda Historia de Usuario que documente un hallazgo medible (rendimiento, UX, SEO, errores, observabilidad) **debe incluir evidencia gráfica** como adjunto en Jira.

### 5.1 Regla general

> **"Sin evidencia gráfica, la Historia está incompleta."**

Las evidencias gráficas (screenshots, capturas de dashboards, heatmaps) son la prueba objetiva del estado reportado. Deben adjuntarse como archivos en el issue de Jira, no solo referenciarse en texto.

### 5.2 Responsabilidades por agente

| Agente | Responsabilidad de captura |
|--------|---------------------------|
| **Guardian** | Screenshots de PageSpeed Insights, Lighthouse, resultados de tests E2E, consola de errores |
| **Clarity Behavior** | Capturas de dashboard general, heatmaps, sesiones con dead clicks, rage clicks, quick backs |
| **Cloud Agent Datadog Alert** | Screenshots de monitores en alerta, gráficas de métricas APM, dashboards de error rate |
| **Scout / PO-Agile** | Al crear o actualizar HUs, verificar que las evidencias correspondientes estén adjuntas |

### 5.3 Flujo de captura y almacenamiento

1. **Capturar:** El agente que genera el hallazgo toma el screenshot usando las herramientas disponibles (Playwright MCP `browser_take_screenshot`, Chrome DevTools `take_screenshot`, o CLI de Lighthouse).
2. **Almacenar localmente:** Guardar en `Workspace/{plataforma}/reports/evidencias/` con naming convention: `{fuente}-{descripcion}.png` (ej. `pagespeed-home.png`, `clarity-dead-clicks-heatmap.png`, `datadog-leads-ms-error-rate.png`).
3. **Registrar en Jira:** Subir como adjunto al issue correspondiente usando el script `upload-evidencias-jira.sh` o la API REST de Jira (`POST /rest/api/3/issue/{key}/attachments`).
4. **Referenciar en comentario:** Al agregar un comentario en la Historia con datos del hallazgo, mencionar los archivos adjuntos por nombre.

### 5.4 Limitación técnica actual

El MCP de Atlassian **no soporta upload de attachments** (archivos binarios). Para adjuntar evidencias se debe usar:

```bash
# Requiere JIRA_EMAIL y JIRA_API_TOKEN como variables de entorno
curl -X POST \
  -H "Authorization: Basic $(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)" \
  -H "X-Atlassian-Token: no-check" \
  -F "file=@ruta/al/screenshot.png" \
  "https://{instancia}.atlassian.net/rest/api/3/issue/{ISSUE_KEY}/attachments"
```

Script reutilizable: `Workspace/{plataforma}/scripts/upload-evidencias-jira.sh`

### 5.5 Naming convention para evidencias

| Fuente | Prefijo | Ejemplos |
|--------|---------|----------|
| PageSpeed / Lighthouse | `pagespeed-` | `pagespeed-home.png`, `pagespeed-arriendo.png` |
| Clarity | `clarity-` | `clarity-dashboard-general.png`, `clarity-dead-clicks-heatmap.png` |
| Datadog | `datadog-` | `datadog-leads-ms-latency.png`, `datadog-auth-error-rate.png` |
| SEO | `seo-` | `seo-sin-metatags.png`, `seo-schema-missing.png` |
| Tests E2E | `e2e-` | `e2e-login-failure.png`, `e2e-form-submit-error.png` |

### 5.6 Cuándo es obligatorio

- Al crear una HU que reporta un problema medible (baseline, degradación, error).
- Al documentar el estado cero (baseline) de una métrica.
- Al cerrar una HU como resuelta (evidencia del estado "después").
- Al reportar un incidente o alerta.

---

## 6. Errores comunes y cómo evitarlos

| Error | Causa | Solución |
|-------|-------|----------|
| `"campo X es obligatorio"` | No se incluyó un campo required | Ejecutar `getJiraIssueTypeMetaWithFields` antes de crear |
| `"El valor debe ser un documento de Atlassian"` | Se envió texto plano a un campo ADF | Construir el JSON ADF según sección 3 |
| `"Field cannot be set"` | El campo no está en la pantalla de la transición | Verificar qué campos acepta la transición con `getTransitionsForJiraIssue` |
