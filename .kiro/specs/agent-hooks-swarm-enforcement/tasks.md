# Plan de Implementación: Agent Hooks para Enforcement del Enjambre

## Visión General

Implementación incremental de 8 archivos de hooks JSON en `.kiro/hooks/` que enforcen las políticas de dominio del enjambre de agentes, acompañados de tests unitarios y tests basados en propiedades con fast-check. Cada tarea crea hooks funcionales y se valida progresivamente.

## Tareas

- [ ] 1. Configurar dependencias y crear hooks preToolUse de guardias de dominio
  - [x] 1.1 Instalar fast-check como devDependency y crear directorio `.kiro/hooks/`
    - Ejecutar `npm install --save-dev fast-check`
    - Crear el directorio `.kiro/hooks/` si no existe
    - _Requisitos: 9.1_

  - [x] 1.2 Crear `clarity-mcp-guard.json` — Guardia de acceso a Clarity MCP
    - Crear `.kiro/hooks/clarity-mcp-guard.json` con tipo `preToolUse`, toolTypes `[".*clarity.*"]`, acción `askAgent`
    - El prompt debe instruir al agente a evaluar si su rol es Clarity_Behavior, cancelar si no lo es, e incluir cláusula de excepción explícita del usuario
    - Seguir el esquema exacto definido en el diseño (name, version "1.0.0", description, when, then)
    - _Requisitos: 1.1, 1.2, 1.3, 9.2, 9.3, 9.4_

  - [x] 1.3 Crear `devtools-mcp-guard.json` — Guardia de acceso a Chrome DevTools MCP
    - Crear `.kiro/hooks/devtools-mcp-guard.json` con tipo `preToolUse`, toolTypes `[".*chrome.devtools.*"]`, acción `askAgent`
    - El prompt debe evaluar rol Guardian + contexto skill prueba, cancelar si no aplica, incluir cláusula de excepción
    - _Requisitos: 2.1, 2.2, 2.3, 9.2, 9.3, 9.4_

  - [x] 1.4 Crear `atlassian-write-guard.json` — Guardia de escritura en Atlassian MCP
    - Crear `.kiro/hooks/atlassian-write-guard.json` con tipo `preToolUse`, toolTypes `[".*atlassian.*(create|update|edit|delete).*"]`, acción `askAgent`
    - El prompt debe evaluar rol Scout o PO_Agile, cancelar si no aplica, permitir sin restricción si el rol coincide
    - _Requisitos: 3.1, 3.2, 3.3, 9.2, 9.3, 9.4_

  - [x] 1.5 Crear `datadog-mcp-guard.json` — Guardia de acceso a Datadog MCP
    - Crear `.kiro/hooks/datadog-mcp-guard.json` con tipo `preToolUse`, toolTypes `[".*datadog.*"]`, acción `askAgent`
    - El prompt debe evaluar rol Cloud_Datadog, cancelar si no aplica, incluir cláusula de excepción
    - _Requisitos: 4.1, 4.2, 4.3, 9.2, 9.3, 9.4_

  - [-] 1.6 Crear `github-mcp-guard.json` — Guardia de acceso a GitHub MCP
    - Crear `.kiro/hooks/github-mcp-guard.json` con tipo `preToolUse`, toolTypes `[".*github.*"]`, acción `askAgent`
    - El prompt debe evaluar rol GitHub_Repos, cancelar si no aplica, incluir cláusula de excepción
    - _Requisitos: 8.1, 8.2, 8.3, 9.2, 9.3, 9.4_

- [ ] 2. Crear hooks postToolUse, fileEdited y postTaskExecution
  - [~] 2.1 Crear `agnostic-write-validator.json` — Validación post-escritura agnóstico/particular
    - Crear `.kiro/hooks/agnostic-write-validator.json` con tipo `postToolUse`, toolTypes `["write"]`, acción `askAgent`
    - El prompt debe instruir al agente a buscar datos hardcodeados (URLs, Jira keys, dashboard IDs, tokens), reemplazar por referencias a platforms.json, y omitir validación en directorios particulares (Workspace/*/config/, docs/data/)
    - _Requisitos: 5.1, 5.2, 5.3, 9.2, 9.3, 9.4_

  - [~] 2.2 Crear `doc-update-reminder.json` — Recordatorio de actualización de documentación
    - Crear `.kiro/hooks/doc-update-reminder.json` con tipo `fileEdited`, patterns para archivos de código (`**/*.js`, `**/*.ts`, `**/*.tsx`, `**/*.cjs`, `**/*.mjs`, `**/*.json`) con exclusiones (`!docs/**`, `!node_modules/**`, `!.kiro/**`, `!.cursor/**`)
    - El prompt debe evaluar si los cambios requieren actualización en docs/ según el mapeo del agente Doc_Updater, y sugerir delegación
    - _Requisitos: 6.1, 6.2, 6.3, 9.2, 9.3, 9.4_

  - [~] 2.3 Crear `test-runner-post-task.json` — Ejecución de tests post-tarea
    - Crear `.kiro/hooks/test-runner-post-task.json` con tipo `postTaskExecution`, acción `askAgent`
    - El prompt debe evaluar si la tarea involucró código testeable, ejecutar tests relevantes (npm test, vitest --run), reportar fallos, y omitir para cambios solo en docs/config
    - _Requisitos: 7.1, 7.2, 7.3, 7.4, 9.2, 9.3, 9.4_

- [~] 3. Checkpoint — Verificar estructura completa de hooks
  - Verificar que los 8 archivos JSON existen en `.kiro/hooks/` y son JSON válido
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Implementar tests unitarios para todos los hooks
  - [~] 4.1 Crear archivo de tests unitarios `tests/unit/hooks.test.js`
    - Crear `tests/unit/hooks.test.js` que lea y valide los 8 archivos JSON de `.kiro/hooks/`
    - Implementar los 10 tests unitarios definidos en la estrategia de testing del diseño:
      1. Validación de estructura JSON: cada hook es JSON válido y parseable
      2. Campos obligatorios presentes: cada hook contiene name, version, when, then
      3. Prompt contiene instrucciones de cancelación en cada guardia preToolUse
      4. Prompt contiene cláusula de excepción en hooks Clarity, DevTools, Datadog, GitHub
      5. Prompt de Atlassian menciona Scout y PO_Agile
      6. Prompt de agnostic-validator lista patrones de datos hardcodeados (URLs, Jira keys, dashboard IDs)
      7. Prompt de agnostic-validator excluye directorios particulares (Workspace/*/config/, docs/data/)
      8. Hook doc-update-reminder excluye docs/ (patrón `!docs/**` presente)
      9. Hook test-runner incluye cláusula de omisión para docs
      10. Versión "1.0.0" en todos los hooks
    - _Requisitos: 9.2, 9.3, 9.4, 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2, 5.1, 5.3, 6.1, 6.3, 7.1, 7.4, 8.1, 8.2_

- [ ] 5. Implementar tests basados en propiedades con fast-check
  - [ ]* 5.1 Escribir test de propiedad para discriminación de dominio por regex
    - **Propiedad 1: Discriminación de dominio por regex**
    - Generar nombres de herramientas aleatorios (con y sin el dominio guardado) y verificar que cada regex de los 5 hooks preToolUse matchea correctamente su dominio y no matchea otros dominios
    - Tag: `Feature: agent-hooks-swarm-enforcement, Property 1: Discriminación de dominio por regex`
    - **Valida: Requisitos 1.1, 2.1, 4.1, 8.1**

  - [ ]* 5.2 Escribir test de propiedad para discriminación escritura vs lectura en Atlassian
    - **Propiedad 2: Discriminación escritura vs lectura en Atlassian**
    - Generar nombres de herramientas Atlassian aleatorios (operaciones de lectura y escritura) y verificar que el regex `.*atlassian.*(create|update|edit|delete).*` solo matchea escrituras
    - Tag: `Feature: agent-hooks-swarm-enforcement, Property 2: Discriminación escritura vs lectura en Atlassian`
    - **Valida: Requisitos 3.1**

  - [ ]* 5.3 Escribir test de propiedad para discriminación archivos código vs docs en fileEdited
    - **Propiedad 3: Discriminación de archivos de código vs documentación en fileEdited**
    - Generar rutas de archivo aleatorias (con extensiones de código y dentro/fuera de docs/) y verificar que los patrones glob discriminan correctamente
    - Tag: `Feature: agent-hooks-swarm-enforcement, Property 3: Discriminación de archivos de código vs documentación en fileEdited`
    - **Valida: Requisitos 6.1, 6.3**

  - [ ]* 5.4 Escribir test de propiedad para conformidad de esquema y convención de hooks
    - **Propiedad 4: Conformidad de esquema y convención de hooks**
    - Para cada archivo de hook en `.kiro/hooks/`, verificar convención de nombres, campos obligatorios, versión "1.0.0", y consistencia name/filename
    - Tag: `Feature: agent-hooks-swarm-enforcement, Property 4: Conformidad de esquema y convención de hooks`
    - **Valida: Requisitos 9.2, 9.3, 9.4**

  - [ ]* 5.5 Escribir test de propiedad para serialización round-trip de hooks JSON
    - **Propiedad 5: Serialización round-trip de hooks JSON**
    - Para objetos hook válidos generados aleatoriamente, serializar a JSON y deserializar debe producir un objeto equivalente al original
    - Tag: `Feature: agent-hooks-swarm-enforcement, Property 5: Serialización round-trip de hooks JSON`
    - **Valida: Requisitos 9.3**

- [~] 6. Checkpoint final — Verificar que todos los tests pasan
  - Ejecutar `npx vitest run tests/unit/hooks.test.js` y verificar que todos los tests unitarios y de propiedades pasan
  - Ensure all tests pass, ask the user if questions arise.

## Notas

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- Cada tarea referencia requisitos específicos para trazabilidad
- Los checkpoints aseguran validación incremental
- Los tests de propiedades validan comportamientos universales con fast-check (mínimo 100 iteraciones)
- Los tests unitarios validan ejemplos específicos y edge cases
- El proyecto usa CommonJS (`"type": "commonjs"`) — los tests usan vitest con `import` (ESM en vitest)
