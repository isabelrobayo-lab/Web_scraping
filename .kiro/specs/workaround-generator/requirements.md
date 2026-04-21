# Documento de Requisitos — Generador de Workaround

## Introducción

Este documento define los requisitos para implementar un **Generador de Workaround** dentro del workspace SQUAD-AGENTES-IA. El objetivo es automatizar la creación de soluciones temporales (workarounds) cuando se detectan incidentes, alertas o errores en las plataformas monitoreadas. El generador combina información de múltiples fuentes (Datadog, Jira, código fuente, Clarity) para producir un documento de workaround estructurado con pasos de mitigación, impacto estimado y criterios de reversión.

La implementación debe ser completamente transversal (agnóstica de plataforma), sin referencias a proyectos específicos. La configuración de plataforma (URLs, servicios, repos) se obtiene de `platforms.json` del workspace activo.

## Glosario

- **Workaround**: Solución temporal documentada que mitiga un incidente o error sin resolver la causa raíz. Incluye pasos de aplicación, impacto, riesgos y criterios de reversión.
- **Generador_Workaround**: Componente principal que orquesta la recopilación de contexto y produce el documento de workaround.
- **Fuente_de_Contexto**: Cualquier origen de datos que alimenta al generador: alertas de Datadog, tickets de Jira, código fuente del repositorio, sesiones de Clarity, logs.
- **Documento_Workaround**: Archivo Markdown generado con la estructura estándar del workaround (resumen, pasos, impacto, reversión, seguimiento).
- **Incidente**: Evento que afecta el funcionamiento normal de una plataforma, detectado por monitores de Datadog, reportado en Jira o identificado manualmente por el usuario.
- **Causa_Raíz**: Origen técnico del incidente. El workaround no la resuelve, pero la documenta para facilitar la solución definitiva.
- **Criterio_de_Reversión**: Condición medible que indica cuándo el workaround debe ser revertido (por ejemplo, tras el despliegue de la solución definitiva).
- **Plantilla_Workaround**: Template Markdown que define la estructura estándar de un documento de workaround.
- **Contexto_Enriquecido**: Conjunto de datos recopilados de múltiples fuentes (Datadog, Jira, código, Clarity) que alimentan la generación del workaround.
- **Workspace_Activo**: Directorio de artefactos del producto actual, resuelto por `scripts/workspace-root.js` (por defecto `Workspace/ciencuadras/`).

## Requisitos

### Requisito 1: Recopilación de contexto desde múltiples fuentes

**User Story:** Como ingeniero de soporte, quiero que el generador recopile automáticamente contexto relevante desde Datadog, Jira y el código fuente, para que el workaround se base en información completa y actualizada del incidente.

#### Criterios de Aceptación

1. WHEN el usuario proporciona un identificador de incidente (ID de monitor Datadog, clave de issue Jira o descripción textual del problema), THE Generador_Workaround SHALL consultar las Fuentes_de_Contexto disponibles para recopilar información relacionada con el incidente.
2. WHEN se proporciona un ID de monitor de Datadog, THE Generador_Workaround SHALL obtener el estado del monitor, los logs recientes, las métricas asociadas y los servicios afectados utilizando el MCP de Datadog.
3. WHEN se proporciona una clave de issue de Jira, THE Generador_Workaround SHALL obtener el resumen, la descripción, los comentarios y el estado del ticket utilizando el MCP de Atlassian.
4. WHEN se identifican servicios afectados, THE Generador_Workaround SHALL resolver los repositorios asociados mediante el mapeo `datadog.serviceToRepos` de `platforms.json` y obtener archivos relevantes del código fuente.
5. IF una Fuente_de_Contexto no está disponible o falla la consulta, THEN THE Generador_Workaround SHALL continuar la generación con las fuentes restantes y documentar en el workaround qué fuentes no pudieron ser consultadas.

### Requisito 2: Generación del documento de workaround

**User Story:** Como ingeniero de soporte, quiero que el generador produzca un documento de workaround estructurado y completo, para que el equipo pueda aplicar la mitigación de forma clara y sin ambigüedades.

#### Criterios de Aceptación

1. WHEN el Contexto_Enriquecido ha sido recopilado, THE Generador_Workaround SHALL producir un Documento_Workaround en formato Markdown que contenga las secciones obligatorias: Resumen del incidente, Impacto, Causa raíz probable, Pasos del workaround, Riesgos y limitaciones, Criterios de reversión y Seguimiento.
2. THE Generador_Workaround SHALL numerar cada paso del workaround de forma secuencial e incluir comandos, configuraciones o acciones concretas cuando aplique.
3. THE Generador_Workaround SHALL incluir en la sección de Seguimiento un enlace al ticket de Jira asociado (si existe) y al monitor de Datadog (si aplica), utilizando las URLs resueltas desde `platforms.json`.
4. IF el Generador_Workaround no puede determinar una causa raíz probable con la información disponible, THEN THE Generador_Workaround SHALL indicar explícitamente que la causa raíz requiere investigación adicional y sugerir los pasos de diagnóstico recomendados.

### Requisito 3: Almacenamiento del documento de workaround

**User Story:** Como ingeniero de soporte, quiero que los workarounds generados se almacenen en una ubicación predecible del workspace, para que el equipo pueda consultarlos y mantener un historial de mitigaciones.

#### Criterios de Aceptación

1. THE Generador_Workaround SHALL almacenar cada Documento_Workaround en el directorio `{WORKSPACE_ROOT}/workarounds/` del Workspace_Activo.
2. THE Generador_Workaround SHALL nombrar cada archivo siguiendo el patrón `workaround-{identificador}-{timestamp}.md`, donde `{identificador}` es el ID del monitor, la clave de Jira o un slug derivado de la descripción, y `{timestamp}` es la fecha en formato `YYYYMMDD-HHmm`.
3. WHEN se genera un workaround para un incidente que ya tiene workarounds previos, THE Generador_Workaround SHALL crear un nuevo archivo sin sobrescribir los existentes, permitiendo mantener el historial completo.

### Requisito 4: Uso de plantilla configurable

**User Story:** Como arquitecto del proyecto, quiero que el generador utilice una plantilla Markdown configurable, para que la estructura del workaround pueda adaptarse a las necesidades del equipo sin modificar el código.

#### Criterios de Aceptación

1. THE Generador_Workaround SHALL utilizar una Plantilla_Workaround almacenada en `docs/templates/workaround-template.md` como base para generar cada documento.
2. WHEN la Plantilla_Workaround no existe en la ruta esperada, THE Generador_Workaround SHALL utilizar una plantilla por defecto embebida en el código y generar una advertencia indicando que no se encontró la plantilla personalizada.
3. THE Plantilla_Workaround SHALL contener marcadores de posición (placeholders) para cada sección obligatoria del documento, permitiendo que el generador los reemplace con el contenido específico del incidente.

### Requisito 5: Integración con Jira para trazabilidad

**User Story:** Como ingeniero de soporte, quiero que el generador pueda crear o actualizar un ticket de Jira con el workaround generado, para que exista trazabilidad entre el incidente y la mitigación aplicada.

#### Criterios de Aceptación

1. WHEN el usuario solicita publicar el workaround en Jira, THE Generador_Workaround SHALL crear un comentario en el ticket de Jira asociado con el contenido del Documento_Workaround, utilizando el MCP de Atlassian.
2. IF no existe un ticket de Jira asociado al incidente, THEN THE Generador_Workaround SHALL ofrecer al usuario la opción de crear un nuevo ticket de tipo "Task" con el workaround como descripción, utilizando el `projectKey` de `platforms.json`.
3. WHEN se publica el workaround en Jira, THE Generador_Workaround SHALL incluir en el Documento_Workaround local la clave del ticket de Jira donde fue publicado.

### Requisito 6: Enriquecimiento opcional con datos de Clarity

**User Story:** Como ingeniero de soporte, quiero que el generador pueda incorporar datos de comportamiento de usuarios desde Microsoft Clarity, para que el workaround incluya información sobre el impacto real en la experiencia del usuario.

#### Criterios de Aceptación

1. WHERE el usuario solicita enriquecimiento con datos de Clarity, THE Generador_Workaround SHALL consultar el MCP de Clarity para obtener métricas de sesiones afectadas (errores JavaScript, rage clicks, sesiones con la URL del incidente) y añadirlas a la sección de Impacto del Documento_Workaround.
2. IF el MCP de Clarity no está configurado o el token no es válido, THEN THE Generador_Workaround SHALL omitir el enriquecimiento de Clarity y documentar en el workaround que los datos de comportamiento de usuario no están disponibles.
3. WHILE se consultan datos de Clarity, THE Generador_Workaround SHALL respetar las políticas de privacidad y no incluir datos personales identificables de usuarios en el Documento_Workaround.

### Requisito 7: Ejecución como script transversal

**User Story:** Como arquitecto del proyecto, quiero que el generador sea un script Node.js ejecutable desde la línea de comandos, para que pueda integrarse con el flujo de trabajo existente del proyecto y ser invocado por agentes o automations.

#### Criterios de Aceptación

1. THE Generador_Workaround SHALL implementarse como un script en `scripts/generate-workaround.js` ejecutable con Node.js 18+.
2. THE Generador_Workaround SHALL aceptar parámetros de entrada por línea de comandos: `--monitor-id` (ID de monitor Datadog), `--jira-key` (clave de issue Jira), `--description` (descripción textual del problema) y `--enrich-clarity` (flag para activar enriquecimiento con Clarity).
3. THE Generador_Workaround SHALL registrar un comando npm en `package.json` con el nombre `workaround:generate` que ejecute el script con los parámetros proporcionados.
4. THE Generador_Workaround SHALL utilizar `scripts/get-platform-config.js` para resolver la configuración de plataforma del Workspace_Activo, manteniendo la consistencia con el resto de scripts del proyecto.
5. IF se ejecuta sin ningún parámetro de entrada, THEN THE Generador_Workaround SHALL mostrar un mensaje de ayuda con los parámetros disponibles y ejemplos de uso.

### Requisito 8: Generación de la plantilla de workaround

**User Story:** Como arquitecto del proyecto, quiero que el sistema incluya una plantilla de workaround por defecto, para que el equipo tenga una estructura base desde la primera ejecución.

#### Criterios de Aceptación

1. THE Generador_Workaround SHALL incluir un archivo `docs/templates/workaround-template.md` con la estructura estándar del Documento_Workaround.
2. THE Plantilla_Workaround SHALL contener las siguientes secciones con marcadores de posición: Título, Fecha, Autor, Resumen del incidente, Servicios afectados, Impacto (con subsección opcional de datos de Clarity), Causa raíz probable, Pasos del workaround (numerados), Riesgos y limitaciones, Criterios de reversión, Seguimiento (enlaces a Jira y Datadog) y Estado (Activo/Revertido).
3. THE Plantilla_Workaround SHALL incluir comentarios en Markdown que expliquen el propósito de cada sección para guiar al usuario en caso de edición manual.

### Requisito 9: Parseo y formateo del documento de workaround

**User Story:** Como desarrollador, quiero que el generador parsee la plantilla Markdown y produzca un documento válido, para que los workarounds sean consistentes y legibles.

#### Criterios de Aceptación

1. WHEN el Generador_Workaround procesa la Plantilla_Workaround, THE Parser SHALL reemplazar cada marcador de posición con el contenido correspondiente del Contexto_Enriquecido.
2. THE Pretty_Printer SHALL formatear el Documento_Workaround resultante como Markdown válido, respetando la indentación, los encabezados y las listas numeradas de la plantilla.
3. FOR ALL Documentos_Workaround válidos, parsear la plantilla, rellenar con datos y formatear el resultado SHALL producir un documento Markdown equivalente al esperado (propiedad round-trip de plantilla → documento → validación de estructura).
4. IF un marcador de posición no tiene datos disponibles en el Contexto_Enriquecido, THEN THE Parser SHALL reemplazar el marcador con el texto "No disponible — requiere investigación adicional" en lugar de dejar el marcador sin resolver.

### Requisito 10: Integración con el flujo de automatización Datadog

**User Story:** Como arquitecto del proyecto, quiero que el generador de workaround pueda ser invocado desde la automatización existente de alertas Datadog, para que cuando se detecte una alerta se genere automáticamente un workaround junto con el plan de trabajo.

#### Criterios de Aceptación

1. WHEN el Cloud Agent Datadog detecta un monitor en estado de alerta y genera un plan de trabajo, THE Generador_Workaround SHALL poder ser invocado como paso adicional del flujo para generar un Documento_Workaround asociado a la alerta.
2. THE Generador_Workaround SHALL aceptar como entrada el contexto ya recopilado por el Cloud Agent (monitor, servicios, repos) para evitar consultas duplicadas a los MCPs.
3. WHEN se genera un workaround desde el flujo de automatización, THE Generador_Workaround SHALL incluir en el Documento_Workaround una referencia al plan de trabajo generado en `{WORKSPACE_ROOT}/plans/`.
