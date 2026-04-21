# Configuración de Playwright MCP (opcional)

> Playwright MCP permite que el agente controle un navegador en tiempo real durante la conversación. Es **complementario** a Playwright Test (CLI); no lo sustituye.

## Cuándo usar cada uno

| Caso | Usar | Motivo |
|------|------|--------|
| Smoke tests, regresión, CI | `npm test` (Playwright Test) | Tests deterministas, versionados, eficientes en tokens |
| Explorar una página concreta | Playwright MCP | Interacción iterativa, snapshot de accesibilidad |
| Verificar ad hoc sin escribir test | Playwright MCP | El agente navega y verifica en la conversación |

## Cómo añadir Playwright MCP en Cursor

1. Abrir **Cursor Settings** → **MCP** → **Add new MCP Server**
2. Nombre: `playwright` (o el que prefieras)
3. Tipo: `command`
4. Comando: `npx @playwright/mcp@latest`

O añadir manualmente en la configuración MCP de Cursor:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

## Requisitos

- Node.js 18+
- `npx` disponible (viene con Node.js)
- Primera ejecución descargará `@playwright/mcp` si no está en caché

## Validación (opcional en onboarding)

Para comprobar que Playwright MCP está operativo:

- Probar una herramienta como `browser_navigate` o `browser_snapshot` en una conversación
- O verificar que el servidor MCP "playwright" aparece en la lista de MCPs de Cursor

## Chrome DevTools MCP (solo flujo E2E en este repo)

En **SQUAD-AGENTES-IA**, el servidor [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) está declarado en **`.kiro/settings/mcp.json`** (nivel proyecto). El servidor queda activo al abrir este workspace.

**Política de agentes:** solo el **Guardian** y el skill **`prueba`** deben usar sus herramientas (rendimiento, Lighthouse, red, consola). El criterio de éxito sigue siendo Playwright por CLI (`npm test`). Detalle: steering `agent-tech-guardian.md`, `04-playwright-cli-vs-mcp.md`, `00-swarm-orchestrator.md`.

## Microsoft Clarity MCP (opcional)

El servidor oficial [microsoft/clarity-mcp-server](https://github.com/microsoft/clarity-mcp-server) expone analítica de Clarity, listado de grabaciones de sesión y consultas a la documentación. En este proyecto lo usa el agente **Clarity Behavior** (inventario #9, steering `agent-clarity-behavior.md`); el Orquestador lo activa vía subagente.

**Flujo “como Jira/Datadog” (enlace + login en plataforma):** guía unificada con el **enlace de instalación en un clic** y los pasos en [docs/onboarding/03-mcp-plataformas-cursor.md](./03-mcp-plataformas-cursor.md) (sección Microsoft Clarity). Este archivo profundiza en JSON, variables de entorno y expectativas OAuth vs token.

### OAuth frente a token (expectativas)

- **No hay flujo OAuth documentado** para este MCP ni para la [Clarity Data Export API](https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-data-export-api): el acceso programático usa un **token JWT** que genera un **admin del proyecto** en Clarity (**Settings → Data Export → Generate new API token**), enviado como `Authorization: Bearer …`. Eso no es “iniciar sesión con Microsoft” desde Cursor; es credencial de proyecto.
- El código del servidor solo lee **`--clarity_api_token`** o variables de entorno equivalentes (p. ej. `CLARITY_API_TOKEN`); no implementa OAuth del protocolo MCP.
- Iniciar sesión en [clarity.microsoft.com](https://clarity.microsoft.com/) con cuenta Microsoft es OAuth para la **interfaz web**; sigue siendo distinto del token de exportación que necesita el MCP.
- Si en el futuro Microsoft publicara un MCP remoto con OAuth, habría que revisar la config que indique Cursor para ese servidor; hoy la vía oficial es la del repositorio anterior.

**Recomendación:** no pegues el token en el JSON del repo. Define **`CLARITY_API_TOKEN`** (o `clarity_api_token`) en el entorno del usuario o en `.kiro/settings/mcp.json` si tu versión permite `env` sin commitear secretos.

Ejemplo de entrada para el IDE **sin token en args** (el proceso hereda `CLARITY_API_TOKEN` del entorno; exporta la variable antes de abrir el IDE o configúrala en el sistema):

```json
{
  "mcpServers": {
    "clarity": {
      "command": "npx",
      "args": ["-y", "@microsoft/clarity-mcp-server"]
    }
  }
}
```

Si prefieres argumentos explícitos (solo en máquina local, no en git):

```json
{
  "mcpServers": {
    "clarity": {
      "command": "npx",
      "args": ["-y", "@microsoft/clarity-mcp-server", "--clarity_api_token=REEMPLAZAR_CON_TOKEN"]
    }
  }
}
```

Equivalente en terminal: `npx @microsoft/clarity-mcp-server` con `CLARITY_API_TOKEN` definida, o `npx @microsoft/clarity-mcp-server --clarity_api_token=TU_TOKEN`.

Ejemplo de entrada (versionada en el repo, `.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--no-usage-statistics"]
    },
    "clarity-server": {
      "command": "npx",
      "args": ["-y", "@microsoft/clarity-mcp-server"]
    }
  }
}
```

**Token Clarity:** no va en el JSON del repo. Define `CLARITY_API_TOKEN` en el entorno antes de abrir el IDE, o en la configuración MCP del servidor `clarity-server` añade el argumento `--clarity_api_token=TU_TOKEN` solo en tu máquina (config que no se commitea).

**Referencias de tableros por producto:** se almacenan en `{WORKSPACE_ROOT}/data/clarity-projects.md` con enlace al dashboard y ventana temporal típica (*Last 3 days*).

## Referencias

- [Playwright MCP - GitHub](https://github.com/microsoft/playwright-mcp)
- [Chrome DevTools MCP - GitHub](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [Microsoft Clarity MCP Server - GitHub](https://github.com/microsoft/clarity-mcp-server)
- [Jira, Datadog y Clarity desde Cursor](./03-mcp-plataformas-cursor.md)
