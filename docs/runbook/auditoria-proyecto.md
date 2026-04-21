# Runbook: Auditoría del proyecto

## Auditoría de errores de consola

El script `scripts/audit-console-errors.js` navega por las zonas configuradas en el `config/platforms.json` del workspace activo (auditZones) y captura errores, warnings y logs de la consola del navegador.

### Ejecución

```bash
npm run audit
```

### Salida

- `{WORKSPACE_ROOT}/audit/console-audit-report.json` — Reporte estructurado
- `{WORKSPACE_ROOT}/audit/screenshots/` — Capturas por zona

### Zonas auditadas

Definidas en `config/platforms.json` del workspace activo → `auditZones`. Ver plantilla en `docs/templates/platforms.example.json`.

### Interpretación

- Revisar `summary.errors` y `summary.warnings` en el JSON
- Priorizar errores que afecten conversión o UX
- Las capturas ayudan a correlacionar errores con pantallas específicas

### Integración con CI

Para ejecutar en CI y fallar si hay errores críticos, se puede extender el script para que retorne código de salida distinto de 0 cuando `summary.errors > N`.

---

## Auditoría de rendimiento (Lighthouse / PageSpeed)

El script `scripts/audit-lighthouse.js` obtiene métricas de rendimiento (móvil y escritorio) vía **Google PageSpeed Insights API** (variable `GOOGLE_PAGESPEED_API_KEY`) o, si no hay clave, intenta **Lighthouse CLI** local (`npx lighthouse` debe estar disponible).

### Ejecución

```bash
npm run audit:lighthouse
```

También se pueden pasar URLs explícitas; ver comentarios al inicio de `scripts/audit-lighthouse.js`.

### Salida

- `{WORKSPACE_ROOT}/audit/lighthouse/` — JSON y resúmenes por URL y estrategia (mobile/desktop)
