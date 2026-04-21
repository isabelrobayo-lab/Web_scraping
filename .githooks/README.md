# Git Hooks

Hooks para integrar el flujo de agentes con Git.

## Pre-commit: recordatorio Doc Updater

El hook `pre-commit` muestra un recordatorio cuando hay cambios en código (scripts, tests, tools, miniverse, config) pero no en documentación (`docs/`).

**Objetivo:** Activar el agente Doc Updater antes de hacer commit de una solución definitiva.

### Instalación

```bash
# Opción 1: Usar esta carpeta como hooksPath
git config core.hooksPath .githooks

# Opción 2: Copiar manualmente
cp .githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Comportamiento

- Si staged incluye código y docs → no muestra nada.
- Si staged incluye solo código → muestra recordatorio (no bloquea).
- Para saltar: `git commit --no-verify`

### Referencias

- Agente: `.kiro/steering/agent-doc-updater.md`
- Inventario: `docs/architecture/6-inventario-agentes.md`
