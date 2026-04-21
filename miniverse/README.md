# Miniverse (upstream)

Mundo pixel art para agentes IA, basado en el proyecto open source **[ianscott313/miniverse](https://github.com/ianscott313/miniverse)** (paquetes npm `@miniverse/core` y `@miniverse/server`).

## Requisitos

- Node.js 18+

## Desarrollo

```bash
cd miniverse
npm install
npm run dev
```

Levanta:

- **Vite** (interfaz): [http://localhost:5173](http://localhost:5173)
- **API / WebSocket** (`miniverse --no-browser`): [http://localhost:4321](http://localhost:4321)

El alias `npm run dev:full` es equivalente a `npm run dev`.

## API para agentes

Misma API que documenta el upstream: `POST /api/heartbeat`, `POST /api/act`, `GET /api/agents`, `GET /api/inbox`, etc. Ver el [README del repositorio](https://github.com/ianscott313/miniverse#readme).

## Claude Code

Copia `.claude/settings.json.example` a la carpeta `.claude` del repo (o del proyecto donde uses Claude Code) y ajusta `MINIVERSE_URL` si el servidor no está en `http://localhost:4321`.

## Cursor (Orquestador ↔ Miniverse)

El **Orquestador** (regla `.kiro/steering/00-swarm-orchestrator.md`) debe elegir el especialista según la actividad y, en **cada Task**, poner como **primera línea** del prompt el metadato `[miniverse:CLAVE]` (p. ej. `[miniverse:scout]`, `[miniverse:historian]`). Así Miniverse muestra **quién se activa** acorde al mapa de dominio → agente.

1. Arranca Miniverse (`npm run dev` en esta carpeta) para tener API `:4321` y WebSocket.
2. Ejecuta una vez `npm run seed:agents` para crear los ciudadanos `inv-*` del inventario.
3. **`legacy .cursor/hooks.json (Cursor-specific)`** llama a `miniverse/scripts/cursor-miniverse-sync.mjs` en `subagentStart` / `subagentStop`:
   - **Prioridad:** parsea `[miniverse:CLAVE]` en el prompt del hook (`task`, `description`, `summary`, etc.; Cursor no siempre rellena solo `task`).
   - **Orquestador** en pantalla: `working` con “Activando → …” al iniciar un Task; `idle` al terminar.
   - **Especialista:** `working` / `idle` según el mismo ciclo.
   - Si falta la etiqueta, se usa **heurística** por `subagent_type` (normalizado) + texto; los tipos internos de Cursor ya no fuerzan Scout por defecto.

**Límites:** solo refleja **Task (subagentes)**. Con **varios Task en paralelo**, el último `subagentStop` puede dejar al Orquestador en `idle` mientras otro subagente sigue (caso raro). Si Miniverse no está levantado, el hook **no bloquea** al agente.

Si `subagentStop` llega **sin texto de task**, el script usa el último especialista guardado en **`.cursor/.miniverse-last-subagent.json (legacy)`** (escrito en `subagentStart`, ignorado por git) y luego lo borra, para no marcar `idle` en el agente equivocado (p. ej. Scout por defecto).

La entrada **stdin** del hook se lee con **`readFileSync(0)`**: en Node reciente, `fs.promises.readFile(0)` puede rechazar el fd y dejar el JSON vacío (todo se resolvía como Scout).

Variable opcional: `MINIVERSE_URL` (mismo significado que en los scripts de seed).

## GitHub Pages

En `main`, el workflow `.github/workflows/deploy-miniverse-github-pages.yml` genera el sitio desde esta carpeta.

1. En GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. Tras un push que toque `miniverse/`, la URL será  
   `https://<usuario-o-org>.github.io/<nombre-repo>/`  
   (ej. `https://CARLOSPATINOVELEZ19.github.io/prueba-agente-po/`).

El build usa `VITE_BASE_PATH=/<repo>/` y conecta la UI al mundo público  
`https://miniverse-public-production.up.railway.app` (API + WebSocket `wss://`), como en el [README upstream](https://github.com/ianscott313/miniverse#join-a-public-world). Para desarrollo local se sigue usando `localhost:4321` sin variables.

## Licencia

El código de los paquetes `@miniverse/*` sigue la licencia MIT del proyecto original. Los assets del mundo (`public/worlds/`, etc.) provienen del scaffold oficial.
