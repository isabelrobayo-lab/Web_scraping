# Runbook: Agente Doc Updater

> Cómo activar y usar el agente experto en actualización de documentación.

---

## Objetivo

Mantener la documentación viva (`docs/`) sincronizada con el código. El agente se activa cuando se actualiza código con una **solución definitiva** y se va a hacer commit.

---

## Activación

### 1. Automática (globs)

El agente se activa al editar archivos que coinciden con:

- Código: `**/*.{js,ts,tsx,cjs,mjs}`, `scripts/`, `tests/`, `tools/`, `miniverse/`, `playwright.config.js`, `package.json`
- Documentación: `docs/**`, `rules/**`

### 2. Pre-commit (recordatorio)

Un hook de Git muestra un recordatorio cuando hay cambios en código pero no en docs:

```bash
# Instalar el hook (una vez por repo)
git config core.hooksPath .githooks
```

Tras instalar, al hacer `git commit` con solo código modificado:

```
📋 DOC UPDATER: Has modificado código. ¿Actualizaste la documentación?
   Si la solución es definitiva, invoca el agente Doc Updater antes del commit:
   → @agent-doc-updater o menciona 'actualizar docs' en el chat.
```

### 3. Manual

- Mencionar `@agent-doc-updater` en el chat de Cursor.
- O escribir: "actualizar docs según los cambios realizados".

---

## Qué actualiza el agente

| Cambios en | Docs a revisar |
|------------|----------------|
| scripts/, get-platform-config | ESTRUCTURA, resumen-proyecto, onboarding |
| tests/, playwright | ESTRUCTURA, 0-overview, 3-tech-stack-org |
| tools/scripts | ESTRUCTURA, tools/scripts/README |
| miniverse/ | 1-stack, ESTRUCTURA |
| .kiro/steering/, agentes | 6-inventario-agentes, docs/architecture/6-inventario-agentes, 5-agents-functional-architecture |
| platforms.json, config | platforms.example.json, onboarding |
| Runbooks, automatizaciones | runbook/, templates/, inventario |
| Decisiones | docs/decisions/ (ADRs) |
| Comandos npm | resumen-proyecto (tabla Comandos) |

---

## Saltar el recordatorio

Si el commit es WIP o no requiere actualización de docs:

```bash
git commit --no-verify -m "mensaje"
```

---

## Referencias

- Regla: `.kiro/steering/agent-doc-updater.md`
- Inventario: `docs/architecture/6-inventario-agentes.md`
- Hook: `.githooks/pre-commit`, `.githooks/README.md`
