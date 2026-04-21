# Documento de Requisitos — Agent Hooks para Enforcement del Enjambre

## Introducción

Este documento define los requisitos para implementar Kiro Agent Hooks que refuercen las responsabilidades de cada agente especialista dentro de la arquitectura de enjambre (swarm). El sistema cuenta con 8+ agentes especializados coordinados por un Orquestador. Actualmente, las restricciones de dominio (qué agente puede usar qué herramienta MCP) se definen solo en archivos de steering/rules como convenciones textuales. Los hooks proporcionan un mecanismo de enforcement activo que intercepta llamadas a herramientas y operaciones de archivos en tiempo real, actuando como checkpoints de autorización.

La implementación debe ser completamente transversal (agnóstica de plataforma), sin referencias a proyectos específicos como Ciencuadras, Jira keys concretos ni dashboards particulares.

## Glosario

- **Hook**: Archivo JSON en `.kiro/hooks/` que define una regla de interceptación con un disparador (`when`) y una acción (`then`).
- **Orquestador**: Agente coordinador del enjambre que delega tareas a agentes especialistas. No ejecuta herramientas MCP ni CLI directamente.
- **Agente_Especialista**: Cualquiera de los 8 agentes del inventario (Scout, Historian, Guardian, Cloud_Datadog, GitHub_Repos, PO_Agile, Doc_Updater, Clarity_Behavior) con dominio y herramientas asignadas.
- **MCP**: Model Context Protocol. Servidores que exponen herramientas externas (Atlassian, Datadog, GitHub, Playwright, Chrome DevTools, Clarity) al agente.
- **preToolUse**: Tipo de hook que se ejecuta antes de que el agente invoque una herramienta. Permite bloquear o advertir.
- **postToolUse**: Tipo de hook que se ejecuta después de que el agente invoque una herramienta. Permite validar resultados.
- **fileEdited**: Tipo de hook que se ejecuta cuando un archivo es modificado.
- **postTaskExecution**: Tipo de hook que se ejecuta al finalizar una tarea completa.
- **askAgent**: Tipo de acción del hook donde se envía un prompt al agente para que evalúe una condición y decida si proceder.
- **Política_de_Dominio**: Regla que asocia un conjunto de herramientas MCP a uno o más agentes autorizados para usarlas.
- **Validación_Agnóstico_Particular**: Regla transversal que exige que el código y la configuración no contengan datos hardcodeados de una plataforma específica.

## Requisitos

### Requisito 1: Guardia de acceso a herramientas MCP de Clarity

**User Story:** Como arquitecto del enjambre, quiero que las herramientas del MCP de Microsoft Clarity solo sean accesibles por el agente Clarity_Behavior, para que ningún otro agente invoque accidentalmente herramientas de analítica de comportamiento fuera de su dominio.

#### Criterios de Aceptación

1. WHEN el agente intenta invocar una herramienta del MCP de Clarity (query-analytics-dashboard, list-session-recordings, query-documentation-resources), THE Hook_Clarity_Guard SHALL solicitar al agente que evalúe si su rol actual corresponde a Clarity_Behavior antes de permitir la ejecución.
2. IF el agente determina que su rol actual no corresponde a Clarity_Behavior, THEN THE Hook_Clarity_Guard SHALL instruir al agente a cancelar la invocación y sugerir delegar la tarea al agente Clarity_Behavior.
3. IF el usuario ha solicitado explícitamente una correlación entre Clarity y otro dominio en el mismo turno, THEN THE Hook_Clarity_Guard SHALL permitir la ejecución documentando la excepción.

### Requisito 2: Guardia de acceso a herramientas MCP de Chrome DevTools

**User Story:** Como arquitecto del enjambre, quiero que las herramientas del MCP de Chrome DevTools solo sean accesibles por el agente Guardian dentro del contexto del skill prueba, para que otros agentes no ejecuten herramientas de depuración del navegador fuera del flujo E2E.

#### Criterios de Aceptación

1. WHEN el agente intenta invocar una herramienta del MCP de Chrome DevTools, THE Hook_DevTools_Guard SHALL solicitar al agente que evalúe si su rol actual corresponde a Guardian y si la invocación ocurre dentro del contexto del skill prueba.
2. IF el agente determina que su rol no corresponde a Guardian o que la invocación ocurre fuera del skill prueba, THEN THE Hook_DevTools_Guard SHALL instruir al agente a cancelar la invocación y sugerir delegar al agente Guardian con el skill prueba.
3. IF el usuario ha solicitado explícitamente el uso de Chrome DevTools por otro agente en ese turno, THEN THE Hook_DevTools_Guard SHALL permitir la ejecución documentando la excepción.

### Requisito 3: Guardia de acceso a operaciones de escritura en Atlassian

**User Story:** Como arquitecto del enjambre, quiero que las operaciones de escritura en el MCP de Atlassian solo sean ejecutadas por los agentes Scout o PO_Agile, para que otros agentes no modifiquen tickets de Jira ni páginas de Confluence sin autorización.

#### Criterios de Aceptación

1. WHEN el agente intenta invocar una herramienta de escritura del MCP de Atlassian (crear, actualizar o eliminar issues, páginas o comentarios), THE Hook_Atlassian_Write_Guard SHALL solicitar al agente que evalúe si su rol actual corresponde a Scout o PO_Agile.
2. IF el agente determina que su rol no corresponde a Scout ni a PO_Agile, THEN THE Hook_Atlassian_Write_Guard SHALL instruir al agente a cancelar la operación de escritura y sugerir delegar al agente Scout o PO_Agile según el tipo de operación.
3. WHILE el agente opera con rol de Scout o PO_Agile, THE Hook_Atlassian_Write_Guard SHALL permitir las operaciones de escritura en Atlassian sin restricción adicional.

### Requisito 4: Guardia de acceso a herramientas MCP de Datadog

**User Story:** Como arquitecto del enjambre, quiero que las herramientas del MCP de Datadog solo sean accesibles por el agente Cloud_Datadog, para que la observabilidad y las alertas se gestionen exclusivamente desde el dominio especializado.

#### Criterios de Aceptación

1. WHEN el agente intenta invocar una herramienta del MCP de Datadog, THE Hook_Datadog_Guard SHALL solicitar al agente que evalúe si su rol actual corresponde a Cloud_Datadog.
2. IF el agente determina que su rol actual no corresponde a Cloud_Datadog, THEN THE Hook_Datadog_Guard SHALL instruir al agente a cancelar la invocación y sugerir delegar la tarea al agente Cloud_Datadog.
3. IF el usuario ha solicitado explícitamente una correlación entre Datadog y otro dominio (por ejemplo, Datadog + código del repo), THEN THE Hook_Datadog_Guard SHALL permitir la ejecución documentando la excepción.

### Requisito 5: Validación post-escritura de datos agnósticos vs particulares

**User Story:** Como arquitecto del enjambre, quiero que después de cada operación de escritura se valide que no se hayan introducido datos hardcodeados de una plataforma específica, para que el código y la configuración se mantengan transversales.

#### Criterios de Aceptación

1. WHEN el agente completa una operación de escritura (en archivos de código, configuración o documentación), THE Hook_Agnostic_Validator SHALL solicitar al agente que revise el contenido escrito en busca de datos hardcodeados de plataforma específica (URLs de producción, project keys de Jira, IDs de dashboards de Datadog, nombres de servicios concretos).
2. IF el agente detecta datos hardcodeados de plataforma específica en archivos que deberían ser transversales (código fuente, templates, docs genéricos), THEN THE Hook_Agnostic_Validator SHALL instruir al agente a reemplazar los datos hardcodeados por referencias a `platforms.json` o variables de configuración.
3. WHILE el agente opera sobre archivos dentro de directorios designados como particulares (Workspace/*/config/, docs/data/), THE Hook_Agnostic_Validator SHALL omitir la validación de datos hardcodeados para esos archivos.

### Requisito 6: Recordatorio de actualización de documentación tras edición de código

**User Story:** Como arquitecto del enjambre, quiero que al editar archivos de código se genere un recordatorio para actualizar la documentación correspondiente, para que el agente Doc_Updater mantenga `docs/` sincronizado con el estado actual del código.

#### Criterios de Aceptación

1. WHEN un archivo de código es editado (extensiones .js, .ts, .tsx, .cjs, .mjs, .json en directorios de código fuente), THE Hook_Doc_Reminder SHALL solicitar al agente que evalúe si los cambios realizados requieren actualización en la documentación según el mapeo definido en el steering del agente Doc_Updater.
2. IF el agente determina que los cambios requieren actualización de documentación, THEN THE Hook_Doc_Reminder SHALL instruir al agente a registrar los archivos de documentación afectados y sugerir delegar la actualización al agente Doc_Updater.
3. IF el archivo editado pertenece exclusivamente al directorio `docs/`, THEN THE Hook_Doc_Reminder SHALL omitir el recordatorio para evitar ciclos de auto-referencia.

### Requisito 7: Ejecución de tests tras finalización de tarea

**User Story:** Como arquitecto del enjambre, quiero que al finalizar una tarea se ejecuten los tests relevantes automáticamente, para que el agente Guardian valide que los cambios no introduzcan regresiones.

#### Criterios de Aceptación

1. WHEN una tarea se completa (postTaskExecution), THE Hook_Test_Runner SHALL solicitar al agente que evalúe si la tarea completada involucró cambios en código que requieren validación mediante tests.
2. IF el agente determina que la tarea involucró cambios en código testeable, THEN THE Hook_Test_Runner SHALL instruir al agente a ejecutar los tests relevantes usando el comando definido en el proyecto (npm test o el comando equivalente configurado).
3. IF los tests fallan, THEN THE Hook_Test_Runner SHALL instruir al agente a reportar los fallos con detalle suficiente para que el agente Guardian pueda diagnosticar y corregir.
4. IF la tarea completada involucró exclusivamente cambios en documentación o configuración sin impacto en código ejecutable, THEN THE Hook_Test_Runner SHALL omitir la ejecución de tests.

### Requisito 8: Guardia de acceso a herramientas MCP de GitHub

**User Story:** Como arquitecto del enjambre, quiero que las herramientas del MCP de GitHub solo sean accesibles por el agente GitHub_Repos, para que la lectura y análisis de repositorios externos se gestione desde el dominio especializado.

#### Criterios de Aceptación

1. WHEN el agente intenta invocar una herramienta del MCP de GitHub (get_file_contents, list_pull_requests, list_commits, list_branches, search_code, list_issues, search_repositories), THE Hook_GitHub_Guard SHALL solicitar al agente que evalúe si su rol actual corresponde a GitHub_Repos.
2. IF el agente determina que su rol actual no corresponde a GitHub_Repos, THEN THE Hook_GitHub_Guard SHALL instruir al agente a cancelar la invocación y sugerir delegar la tarea al agente GitHub_Repos.
3. IF el usuario ha solicitado explícitamente una operación que requiere GitHub desde otro agente en ese turno, THEN THE Hook_GitHub_Guard SHALL permitir la ejecución documentando la excepción.

### Requisito 9: Estructura y convención de archivos de hooks

**User Story:** Como arquitecto del enjambre, quiero que todos los hooks sigan una estructura y convención de nombres consistente en `.kiro/hooks/`, para que el sistema sea mantenible y extensible.

#### Criterios de Aceptación

1. THE Sistema_de_Hooks SHALL almacenar cada hook como un archivo JSON individual dentro del directorio `.kiro/hooks/`.
2. THE Sistema_de_Hooks SHALL nombrar cada archivo de hook siguiendo el patrón `{dominio}-{tipo-de-guardia}.json` (por ejemplo: `clarity-mcp-guard.json`, `devtools-mcp-guard.json`).
3. THE Sistema_de_Hooks SHALL incluir en cada archivo de hook los campos obligatorios: name, version, when (con type y toolTypes o patterns según corresponda) y then (con type y prompt).
4. THE Sistema_de_Hooks SHALL usar la versión "1.0.0" como versión inicial para todos los hooks creados en esta implementación.
5. WHEN se añade un nuevo agente al inventario del enjambre, THE Sistema_de_Hooks SHALL permitir la creación de un nuevo hook de guardia siguiendo la misma convención sin modificar los hooks existentes.
