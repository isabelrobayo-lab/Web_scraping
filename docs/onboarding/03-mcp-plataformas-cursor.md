# Conectar Jira, Datadog y Clarity desde Cursor

> Guía alineada al onboarding: **mismo tipo de pasos** (abrir enlace / instalar / iniciar sesión en la plataforma) que para Jira y Datadog. Incluye la **diferencia real** con Microsoft Clarity: hoy **no** hay OAuth remoto en el MCP oficial; el “quedar conectado” es **token de exportación** guardado en Cursor (o variable de entorno), no un login OAuth gestionado por Cursor como en Atlassian o Datadog.

## Resumen: cómo autentica cada integración

| Plataforma | En Cursor suele usarse | Cómo “te logueas” y quedas conectado |
|------------|------------------------|--------------------------------------|
| **Jira / Confluence (Atlassian)** | Servidor MCP remoto (`url` en config) | Cursor abre el **navegador** (OAuth con Atlassian). Tras autorizar, la sesión queda enlazada al MCP. Ver [Setting up IDEs (Atlassian Rovo MCP)](https://support.atlassian.com/rovo/docs/setting-up-ides). |
| **Datadog** | Extensión + MCP gestionado | Instalas la extensión, **Sign in** a Datadog **desde el IDE**; reinicio y el MCP queda disponible. Ver [Set up the Datadog MCP Server (Cursor)](https://docs.datadoghq.com/bits_ai/mcp_server/setup?tab=cursor). |
| **Microsoft Clarity** | `npx @microsoft/clarity-mcp-server` (stdio) | **Instalación en un clic** (abajo). Luego entras a [clarity.microsoft.com](https://clarity.microsoft.com/) con tu cuenta Microsoft, generas un **API token** (Data Export) y lo configuras **una vez** en la entrada MCP del servidor (args o `CLARITY_API_TOKEN`). No es el mismo mecanismo OAuth que Jira/Datadog. |

Directorio general de MCP en Cursor: [Cursor – MCP / Directory](https://cursor.com/docs/mcp/directory).

---

## 1. Jira y Confluence (Atlassian)

1. Abre **Cursor Settings** → **MCP** (o **Tools & MCP**, según versión).
2. Añade el servidor según la documentación actual de Atlassian, por ejemplo servidor remoto con URL tipo `https://mcp.atlassian.com/v1/mcp` (el detalle exacto puede variar; sigue la guía enlazada).
3. Guarda y, cuando Cursor lo pida, completa el **flujo OAuth en el navegador** con tu cuenta Atlassian.
4. Reinicia el asistente de IA si hace falta.

**Documentación oficial:** [Setting up IDEs (desktop clients) | Atlassian Rovo MCP](https://support.atlassian.com/rovo/docs/setting-up-ides).

---

## 2. Datadog

1. Instala la extensión Datadog para el IDE (en la guía de Datadog viene el comando `cursor --install-extension ...` o el paso equivalente).
2. **Inicia sesión** en tu organización Datadog desde la extensión / flujo que indique la doc.
3. Reinicia Cursor si lo pide la documentación.
4. Comprueba que el servidor MCP Datadog aparece en la lista de MCP.

**Documentación oficial:** [Set up the Datadog MCP Server – pestaña Cursor](https://docs.datadoghq.com/bits_ai/mcp_server/setup?tab=cursor).

---

## 3. Microsoft Clarity (mismo “primer paso” con enlace; luego token)

### 3.1 Instalar el servidor MCP en Cursor (un clic)

Microsoft publica un enlace de instalación compatible con **VS Code** y con editores basados en VS Code (p. ej. **Cursor**):

**[Instalar Microsoft Clarity MCP en el editor (redirect oficial)](https://insiders.vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522clarity-server%2522%252C%2522command%2522%253A%2522npx%2522%252C%2522args%2522%253A%255B%2522%2540microsoft%252Fclarity-mcp-server%2522%255D%257D)**

- Abre el enlace; el editor debería registrar el servidor `clarity-server` con `npx` y `@microsoft/clarity-mcp-server`.
- Si el navegador no abre el editor, añade el servidor a mano: **Cursor Settings** → **MCP** → nuevo servidor con comando `npx` y args `-y`, `@microsoft/clarity-mcp-server` (como en [microsoft/clarity-mcp-server](https://github.com/microsoft/clarity-mcp-server)).

### 3.2 “Loguearte” en Clarity y obtener credencial para el MCP

Aquí **sí** usas la web con cuenta Microsoft (como cuando trabajas en el dashboard):

1. Entra a **[https://clarity.microsoft.com](https://clarity.microsoft.com/)** e inicia sesión.
2. Abre tu **proyecto** → **Settings** → **Data Export** → **Generate new API token**.
3. Copia el token y **no** lo subas al repositorio.

Ese token es lo que el MCP usa como `Bearer`; es la vía soportada por la [Clarity Data Export API](https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-data-export-api).

### 3.3 Dejar el MCP “conectado” en Cursor

El servidor **no** implementa OAuth con Cursor; opciones habituales:

- Añadir en los **args** del servidor (solo en tu máquina / config global de Cursor):  
  `"--clarity_api_token=TU_TOKEN"`  
  Tras guardar, el proceso del MCP arranca ya autenticado hasta que revoques el token.
- O definir **`CLARITY_API_TOKEN`** en el entorno del sistema y arrancar el servidor **sin** el flag en `args` (ver `docs/onboarding/02-playwright-mcp-config.md`).

### 3.4 Validación

- En la lista de MCP de Cursor debe aparecer el servidor Clarity.
- En chat, una pregunta de prueba al agente **Clarity Behavior** (Orquestador con `[miniverse:clarity-behavior]`) sobre métricas o documentación de Clarity.

Más detalle y matices: `docs/onboarding/02-playwright-mcp-config.md` (sección Microsoft Clarity MCP).

---

## Referencias cruzadas en este repo

- Onboarding general: `docs/onboarding/01-flujo-primera-interaccion.md`
- Playwright / Chrome DevTools / Clarity (JSON de ejemplo): `docs/onboarding/02-playwright-mcp-config.md`
- Agente Clarity: `.kiro/steering/agent-clarity-behavior.md`, inventario #9 en `docs/architecture/6-inventario-agentes.md`
