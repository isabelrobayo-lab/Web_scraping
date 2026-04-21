# Registro de cambios — SQUAD-AGENTES-IA

<!--
Mantenimiento (recomendaciones):
- Actualiza este archivo en el MISMO pull request / commit que el cambio funcional.
- Una entrada por cambio notable; evita listados enormes: agrupa lo menor bajo una sola viñeta.
- Usa [Unreleased] para trabajo ya en main pero sin etiqueta; al publicar, renombra a [X.Y.Z] con fecha ISO (YYYY-MM-DD).
- Sigue SemVer (MAJOR.MINOR.PATCH): rupturas → MAJOR; compatible hacia atrás → MINOR; solo correcciones → PATCH.
- Prefija viñetas con **Ámbito** (Núcleo, Miniverse, Docs, Tooling, Config) para que el changelog único siga siendo legible.
- Generadores (release-please, changesets, conventional changelog): pueden anteponerse a este formato; revisa que las categorías sigan alineadas.
- Para KIRO: en cada release, completa "Notas para migración a KIRO" solo si hay impacto (API, config, dependencias, flujos).
-->

Este documento registra cambios **relevantes** para todos los ámbitos versionados dentro del repositorio **SQUAD-AGENTES-IA** (núcleo de tests y scripts, **Miniverse**, documentación y herramientas). El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto adhiere al [Versionamiento semántico (SemVer)](https://semver.org/lang/es/).

## Ámbitos incluidos en este registro

| Ámbito | Descripción breve |
|--------|-------------------|
| **Núcleo** | Paquete raíz, Playwright, Vitest, scripts en `scripts/`, configuración de pruebas |
| **Miniverse** | Aplicación/workspace de agentes en `miniverse/` |
| **Docs** | Contenido en `docs/`, diagramas, onboarding |
| **Tooling** | Scripts en `tools/scripts/`, automatización y reportes |
| **Config** | Plantillas, `platforms.example.json`, reglas Cursor (cuando afecten uso del repo) |

El número de versión del changelog puede alinearse con `version` en `package.json` del núcleo o con etiquetas Git; documenta en cada release qué etiqueta corresponde.

## [Unreleased]

### Added

- **Config:** 16 Agent Hooks en `.kiro/hooks/` para enforcement de segregación de funciones del enjambre de agentes:
  - 7 guards de control de acceso MCP (preToolUse): `atlassian-write-guard`, `clarity-mcp-guard`, `datadog-mcp-guard`, `chrome-devtools-guard`, `playwright-mcp-guard`, `github-mcp-guard`, `drawio-mcp-guard`
  - 3 guards de seguridad (preToolUse): `secrets-guard`, `git-safety-guard`, `jira-metadata-check`
  - 1 hook de delegación (promptSubmit): `swarm-delegation-enforcer`
  - 5 hooks de calidad (fileEdited/fileCreated/postToolUse/postTaskExecution): `hardcoded-data-validator`, `doc-updater-reminder`, `agnostico-particular-check`, `lint-on-save`, `post-task-tests`

### Changed

- **Docs:** Actualizado `README.md` — sección Hooks de Agentes refleja los 16 hooks reales; corregido agente autorizado de Draw.io MCP (Doc Updater, no Orquestador).
- **Docs:** Actualizado `docs/architecture/6-inventario-agentes.md` — sección Hooks de enforcement con archivos, categorías y propósitos reales.

### Deprecated

### Removed

### Fixed

- **Docs:** Eliminadas referencias a hooks inexistentes en README (`devtools-mcp-guard`, `agnostic-write-validator`, `readme-auto-updater`, `miniverse-agent-start/stop`).

### Security

- **Config:** Hook `secrets-guard` previene escritura de credenciales hardcodeadas en código fuente.
- **Config:** Hook `git-safety-guard` exige dry-run o stash antes de operaciones git destructivas (basado en incidente real).

### Notas para migración a KIRO

- Los 16 hooks en `.kiro/hooks/` se versionan con el repo y se cargan automáticamente en Kiro al clonar. No requieren configuración manual por usuario.

---

## [1.0.0] — 2026-03-28

Versión de referencia inicial alineada con el núcleo publicado como `1.0.0` en `package.json`. Los datos de ejemplo siguientes son **ilustrativos**; sustitúyelos por tu historial real al adoptar el archivo.

### Added

- **Núcleo:** Proyecto Playwright con smoke agnóstico y artefactos bajo `tests/`.
- **Núcleo:** Scripts npm para auditoría de consola (`audit`) y Lighthouse opcional (`audit:lighthouse`).
- **Miniverse:** Paquete interno con scripts `seed:agents` expuestos vía el paquete raíz.
- **Docs:** Guía de primera interacción y arquitectura de workspace en `docs/`.
- **Tooling:** Generador de reporte HTML de ciclo y despliegue asistido a GitHub Pages.
- **Config:** Plantilla `platforms.example.json` para configuración por plataforma.

### Changed

- **Núcleo:** Configuración de `baseURL` y rutas de informes mediante variables de entorno y `platforms.json` (sin URLs fijas en código).
- **Docs:** Estructura de documentación alineada con enfoque agnóstico por plataforma.

### Deprecated

- **Núcleo:** *(ejemplo)* Uso directo de `LEGACY_REPORT_PATH`; sustituir por `WORKSPACE_ROOT`-aware paths en próximas minor.

### Removed

- *(ejemplo ficticio)* **Tooling:** Script experimental `tools/scripts/old-migrate-paths.cjs` retirado tras estabilizar `workspace-root.js`.

### Fixed

- **Núcleo:** *(ejemplo)* Manejo de timeouts en smoke cuando el `baseURL` devolvía redirecciones encadenadas.
- **Docs:** Enlaces rotos en diagramas exportados a HTML.

### Security

- **Config:** *(ejemplo)* Documentación actualizada para no incluir secretos en `platforms.json` versionado; usar variables de entorno o secret manager.

### Notas para migración a KIRO

Relevancia para una futura migración a **KIRO** (personalizar según tu definición de KIRO: producto, plataforma interna, o estándar de referencia):

| Tema | Relevancia |
|------|------------|
| **Compatibilidad de runtime** | Node.js 18+ requerido; validar equivalente en el entorno KIRO. |
| **Contratos de configuración** | Lectura centralizada desde `WORKSPACE_ROOT` y `platforms.json`; cualquier adaptador KIRO debe mapear estas rutas y variables. |
| **Dependencias** | `playwright`, `vitest`, `eslint`, `prettier` en versiones fijadas en el lockfile; revisar políticas de aprobación en KIRO. |
| **Breaking changes** | Ninguno declarado en 1.0.0 de ejemplo; en releases futuros, lista aquí APIs o env vars eliminadas. |
| **Refactorizaciones** | Separación clara Núcleo / Miniverse facilita migración por fases (tests primero, Miniverse después). |

---

## Plantilla rápida por versión (copiar al publicar)

<!--
Al crear [X.Y.Z], pega y completa:

## [X.Y.Z] — YYYY-MM-DD

### Added
- **Ámbito:** …

### Changed
- …

### Deprecated
- …

### Removed
- …

### Fixed
- …

### Security
- …

### Notas para migración a KIRO
- …
-->

<!--
Enlaces tipo Keep a Changelog (opcional). Sustituye OWNER/REPO por tu remoto:
[Unreleased]: https://github.com/OWNER/REPO/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/OWNER/REPO/releases/tag/v1.0.0
-->
