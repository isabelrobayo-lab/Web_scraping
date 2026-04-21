---
inclusion: always
---
# Onboarding - Primera Interacción

Al iniciar una sesión de trabajo, **antes de cualquier tarea**, verificar dos condiciones:

## 0. Comprobar si existe configuración de MCPs

Si **no existe** `.kiro/settings/mcp.json`:

1. Copiar `.kiro/settings/mcp.example.json` → `.kiro/settings/mcp.json`.
2. Informar al usuario que se creó la configuración base de MCPs.
3. Indicar que puede agregar MCPs adicionales (Datadog, GitHub, Draw.io, AWS) editando el archivo o desde su config global (`~/.kiro/settings/mcp.json`).
4. Los MCPs que el usuario ya tenga configurados a nivel global (`~/.kiro/settings/mcp.json`) se respetan — Kiro hace merge con precedencia: user < workspace.

**Nota:** `.kiro/settings/mcp.json` está en `.gitignore` para no sobreescribir la configuración de otros usuarios. La plantilla versionada es `.kiro/settings/mcp.example.json`.

## 1. Comprobar si existe configuración de plataformas

Si **no existe** `Workspace/config/platforms.json`:

1. Ejecutar el **Paso 1** del flujo: validar MCPs (Atlassian, Datadog, GitHub) y CLIs (`gh`, `node`, `npm`, `npx playwright`).
2. Ejecutar el **Paso 2**: crear `Workspace/config/platforms.json` desde `docs/templates/platforms.example.json` y solicitar al usuario:
   - URLs de la aplicación
   - Rutas del proyecto en Jira (projectKey, projectUrl)
   - Tablero de incidentes
   - Tablero de incidentes de seguridad
   - Tablero/Dashboards de Datadog
3. No continuar con otras tareas hasta completar el onboarding o hasta que el usuario indique que lo hará después.

## 2. Si ya existe configuración

Usar `Workspace/config/platforms.json` como fuente de verdad para URLs, Jira y Datadog. No hardcodear plataformas en código ni docs.

## Referencia

Flujo detallado: `docs/onboarding/01-flujo-primera-interaccion.md`
