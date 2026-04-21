# Kiro CLI — Agentes del Enjambre en Terminal

Guía para usar los agentes especializados del enjambre desde la terminal con [Kiro CLI](https://kiro.dev/docs/cli/).

---

## Requisitos previos

1. **Kiro CLI instalado:**
   ```bash
   curl -fsSL https://cli.kiro.dev/install | bash
   ```
2. **Autenticación:** Iniciar sesión en Kiro CLI (se hace una sola vez).
3. **Variables de entorno** (según el agente que uses):
   - Datadog Alert: `DATADOG_API_KEY`, `DATADOG_APP_KEY`
   - GitHub Repos: Autenticación `gh auth login` o token GitHub
   - Atlassian (Scout): OAuth vía MCP Remote (se autentica al primer uso)

---

## Agentes disponibles

| Agente | Comando | Shortcut | Propósito |
|--------|---------|----------|-----------|
| Scout | `kiro-cli --agent scout` | `ctrl+1` | Explorar Jira/Confluence |
| Guardian | `kiro-cli --agent guardian` | `ctrl+2` | Tests E2E, Lighthouse, QA |
| Historian | `kiro-cli --agent historian` | `ctrl+3` | Explorar repo, git log, impacto |
| GitHub Repos | `kiro-cli --agent github-repos` | `ctrl+4` | Repos externos de la plataforma |
| Datadog Alert | `kiro-cli --agent datadog-alert` | `ctrl+5` | Respuesta a alertas Datadog |

---

## Uso básico

```bash
# Iniciar con un agente específico
kiro-cli --agent guardian

# Iniciar sesión normal y cambiar de agente
kiro-cli
/agent swap

# Resumir conversación anterior en el mismo directorio
kiro-cli chat --resume
```

---

## Arquitectura de los agentes CLI

Cada agente CLI (`.kiro/agents/*.json`) sigue este diseño:

```
prompt ──→ file://../steering/agent-*.md  (reutiliza steering existente)
MCPs   ──→ Solo los que necesita (includeMcpJson: false)
tools  ──→ Mínimo necesario por agente
allowed──→ Pre-aprueba operaciones de lectura
resources → Steering + platforms.json + lineamientos Jira
hooks  ──→ agentSpawn (contexto), preToolUse (validaciones)
```

Esto significa que:
- **Un cambio en el steering** se refleja automáticamente en el agente CLI.
- **Los MCPs son independientes** del `mcp.json` del workspace.
- **Los permisos son restrictivos** por defecto.

---

## Relación IDE ↔ CLI

| Aspecto | IDE (Kiro) | CLI (`kiro-cli`) |
|---------|-----------|-----------------|
| Orquestador | Steering always-on | No aplica (agente directo) |
| Hooks de enforcement | `.kiro/hooks/` (guards MCP) | Hooks en el JSON del agente |
| Steering | `.kiro/steering/` auto-cargado | Cargado vía `resources` |
| Skills | Activación por nombre | Cargado vía `skill://` en resources |
| MCPs | `mcp.json` compartido | Declarados por agente |

---

## Seguridad

- Los agentes CLI **no incluyen secretos** en sus archivos JSON.
- Credenciales se leen de variables de entorno del sistema.
- Atlassian usa OAuth vía MCP Remote (interactivo al primer uso).
- GitHub usa OAuth o `gh auth login`.
- Los archivos `.kiro/agents/` se versionan en git (seguros, sin secretos).

---

## Agregar un nuevo agente CLI

1. Crear `.kiro/agents/<nombre>.json` siguiendo la [referencia](https://kiro.dev/docs/cli/custom-agents/configuration-reference).
2. Apuntar el `prompt` al steering: `file://../steering/agent-<nombre>.md`.
3. Declarar solo los MCPs necesarios.
4. Actualizar `docs/architecture/6-inventario-agentes.md` (sección Agentes CLI).
5. Probar: `kiro-cli --agent <nombre>`.

---

## Referencias

- [Kiro CLI — Docs](https://kiro.dev/docs/cli/)
- [Custom Agents](https://kiro.dev/docs/cli/custom-agents/)
- [Configuration Reference](https://kiro.dev/docs/cli/custom-agents/configuration-reference)
- [Hooks](https://kiro.dev/docs/cli/hooks/)
- [Inventario de agentes](../architecture/6-inventario-agentes.md)
