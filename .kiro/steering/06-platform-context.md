---
inclusion: always
---
# Contexto de Plataforma Activa

Este steering carga dinámicamente el contexto de la plataforma activa. Los datos específicos (IDs, URLs, servicios) se leen de `Workspace/config/platforms.json`.

---

## Fuente de verdad

- **Configuración:** `Workspace/config/platforms.json` (no versionado, particular por usuario/plataforma)
- **Plataforma activa:** Determinada por `PLATFORM_ID` (env) o `defaultPlatformId` en el JSON
- **Template agnóstico:** `docs/templates/platforms.example.json`

## Regla para agentes

1. **Nunca hardcodear** URLs, project keys de Jira, IDs de Datadog, nombres de servicios ni repos en código versionable.
2. **Siempre leer** de `platforms.json` usando `scripts/get-platform-config.js` o consultando el JSON directamente.
3. **Contexto particular** de cada plataforma (aprendizajes, baselines, runbooks) vive en `Workspace/{plataforma}/`.

## Estructura esperada por plataforma

```
Workspace/{plataforma}/
├── config/platforms.json    # Fuente de verdad (URLs, Jira, Datadog, GitHub)
├── steering/                # Steering particular (contexto, aprendizajes)
├── specs/                   # Specs de features particulares
├── plans/                   # Planes generados por agentes
├── reports/                 # Reportes y evidencias
├── observabilidad/          # Runbooks y baselines de observabilidad
├── audit/                   # Auditorías (Lighthouse, consola)
├── scripts/                 # Scripts particulares (upload evidencias, etc.)
└── data/                    # Datos de referencia (Clarity projects, etc.)
```

## Cómo cargar contexto particular

Si existe `Workspace/{plataforma}/steering/`, los agentes pueden leer esos archivos para obtener aprendizajes y contexto operativo específico de la plataforma. Ejemplo:

- `Workspace/ciencuadras/steering/06-ciencuadras-context.md`
- `Workspace/jelpit-conjuntos/steering/contexto-jelpit.md`

## Archivos de referencia

| Archivo | Contenido |
|---------|-----------|
| `Workspace/config/platforms.json` | Fuente de verdad — IDs, URLs, servicios |
| `docs/templates/platforms.example.json` | Template agnóstico para onboarding |
| `scripts/get-platform-config.js` | Helper para leer config desde scripts |
| `scripts/workspace-root.js` | Resolución de WORKSPACE_ROOT |
