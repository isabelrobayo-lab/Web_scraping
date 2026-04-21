# Validar integración Miniverse ↔ IDE (hooks)

Objetivo: comprobar que, al lanzar un subagente, el IDE (Kiro o Cursor) ejecuta los hooks correspondientes y Miniverse recibe los heartbeats en `http://localhost:4321`, **sin** usar Jira ni crear historias de usuario.

## Compatibilidad IDE

| IDE | Script | Invocación |
|-----|--------|------------|
| **Kiro** | `miniverse/scripts/kiro-miniverse-sync.mjs` | Args posicionales: `node kiro-miniverse-sync.mjs <agentKey> working\|idle ["<task>"]` |
| **Cursor (legacy)** | `miniverse/scripts/cursor-miniverse-sync.mjs` | Stdin JSON: `.cursor/hooks.json` → `subagentStart\|subagentStop` |

## Prerrequisitos

1. **Workspace de confianza** en Cursor (Trusted) para que corran los hooks del proyecto.
2. **Miniverse** con API viva en `:4321` y UI en `:5173`:
   ```bash
   cd miniverse && npm install && npm run dev
   ```
3. Ciudadanos del inventario (una vez por entorno o tras borrar datos locales):
   ```bash
   cd miniverse && npm run seed:agents
   ```
4. Archivos presentes:
   - **Kiro:** `miniverse/scripts/kiro-miniverse-sync.mjs` (invocado por hooks de `.kiro/hooks/`)
   - **Cursor (legacy):** `miniverse/scripts/cursor-miniverse-sync.mjs` (invocado por `.cursor/hooks.json`)

## Procedimiento de validación

### A. Comprobar API antes del Task

En otra terminal:

```bash
curl -s http://localhost:4321/api/agents | head -c 500
```

Debe responder JSON con agentes `inv-orquestador`, `inv-scout`, etc.

### B. Abrir la UI de Miniverse

Abre en el navegador: `http://localhost:5173` y deja la vista visible (o refresca tras el paso C).

### C. Disparar un Task de prueba en Cursor (Agent)

En el chat del **Agent** (no hace falta que el subagente haga trabajo real):

1. Pide explícitamente una tarea mínima que use la herramienta **Task** con un subagente (por ejemplo `explore` o `generalPurpose`).
2. El **prompt del Task** debe empezar por la etiqueta Miniverse, por ejemplo:
   ```text
   [miniverse:historian]

   Ignora la primera línea. Lista solo el archivo README.md en la raíz del repo y responde con su primera línea.
   ```
   (Cualquier CLAVE del inventario sirve: `scout`, `guardian`, `cloud-datadog`, etc.)

**Alcance:** esto valida hooks + heartbeat. **No** configures `platforms.json` para Jira ni ejecutes el flujo de `automation-datadog-alert` si solo quieres probar Miniverse.

### D. Qué debe ocurrir (criterio de éxito)

- En **Miniverse**, el **Orquestador** pasa brevemente a estado de trabajo con una tarea tipo “Activando → …” y el agente elegido (p. ej. Historian) muestra **working** con un fragmento del task.
- Al terminar el subagente, ambos vuelven a **idle** (o equivalente).
- Si no ves cambios: revisa la salida de **Cursor** (logs / Output de hooks) por errores `[cursor-miniverse-sync]` o `node` / `EADDRINUSE` en `:4321`.

### E. Prueba directa del script (opcional, sin Task)

**Kiro** (args posicionales):

```bash
cd /path/al/repo/SQUAD-AGENTES-IA
node miniverse/scripts/kiro-miniverse-sync.mjs guardian working "Prueba manual"
node miniverse/scripts/kiro-miniverse-sync.mjs guardian idle
node miniverse/scripts/kiro-miniverse-sync.mjs historian working "Exploración de repo"
node miniverse/scripts/kiro-miniverse-sync.mjs historian idle
```

**Cursor (legacy)** (stdin JSON, debe imprimir `{"permission":"allow"}`):

```bash
cd /path/al/repo/SQUAD-AGENTES-IA
printf '%s' '{"subagent_type":"explore","task":"[miniverse:historian]\nPrueba manual"}' | node miniverse/scripts/cursor-miniverse-sync.mjs subagentStart
printf '%s' '{"subagent_type":"explore","task":"[miniverse:historian]\nPrueba manual"}' | node miniverse/scripts/cursor-miniverse-sync.mjs subagentStop
```

Sustituye `/path/al/repo/SQUAD-AGENTES-IA` por la ruta real del clon.

## Qué queda fuera de esta validación

- Crear o buscar **HUs en Jira** (no es necesario `jira.cloudId` / `projectKey` ni MCP Atlassian para este check).
- Validar monitores Datadog ni el runbook `automation-datadog-alert.md` completo.

## Referencias

- `miniverse/README.md` — arranque y variable `MINIVERSE_URL`.
- `miniverse/scripts/kiro-miniverse-sync.mjs` — adaptador Kiro (args posicionales).
- `miniverse/scripts/cursor-miniverse-sync.mjs` — adaptador Cursor legacy (stdin JSON).
- `.kiro/steering/00-swarm-orchestrator.md` — mapa `[miniverse:CLAVE]` por agente.
