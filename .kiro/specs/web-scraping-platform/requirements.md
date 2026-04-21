# Documento de Requisitos — Plataforma Paramétrica de Web Scraping Inmobiliario

## Introducción

Este documento define los requisitos para una plataforma paramétrica de web scraping orientada al mercado inmobiliario latinoamericano. El sistema permite configurar URLs objetivo, profundidad de navegación y frecuencia de ejecución a través de una interfaz CRUD (PARAM_FRONT). Un motor de scraping con capacidades anti-bot — rotación de User-Agents, delays aleatorios, Playwright — extrae datos de listados inmobiliarios siguiendo un esquema de 66 campos definido en el Diccionario de Datos. La lógica de datos (DATA_LOGIC) implementa Upsert basado en la combinación única de `Código_Inmueble` + `Sitio_Origen`, con validación de tipos por campo y registro estructurado de errores. Un dashboard permite consultar, visualizar y exportar los datos recolectados.

**Stack tecnológico**: Python 3.12+ con FastAPI (backend), React 18 + TypeScript + Vite (frontend), PostgreSQL 15.4+ (persistencia), SQLAlchemy 2.0+ (ORM), Celery + Redis (cola de tareas), pytest 8.0+ y Vitest 3.x (testing).

## Glosario

- **Plataforma**: El sistema completo de web scraping paramétrico descrito en este documento.
- **PARAM_FRONT**: Módulo de interfaz de usuario para la gestión CRUD de configuraciones de scraping y mapas de selectores.
- **ENGINE**: Módulo motor de scraping responsable de la extracción de datos con capacidades stealth, ejecutado como worker Celery.
- **DATA_LOGIC**: Módulo de lógica de datos que gestiona la validación de campos, persistencia, deduplicación (Upsert) y registro de errores.
- **DASHBOARD**: Módulo de consulta, visualización, monitoreo de ejecuciones y exportación de datos extraídos.
- **Configuración_Scraping**: Registro que define una URL base, profundidad de navegación, tipo de operación (Venta/Arriendo) y modo de ejecución (Manual/Programado).
- **Scheduler**: Componente (Celery Beat) que gestiona la ejecución programada o manual de tareas de scraping.
- **Tarea_Scraping**: Instancia de ejecución de scraping asociada a una Configuración_Scraping, con estado, duración y resumen de resultados.
- **Stealth**: Conjunto de técnicas anti-detección de bots que incluyen rotación de User-Agents, delays aleatorios, rotación de sesiones y emulación de navegador real.
- **User_Agent**: Cadena de identificación del navegador enviada en las cabeceras HTTP de cada solicitud.
- **Selector_CSS**: Expresión CSS utilizada para localizar elementos HTML específicos en una página web.
- **Mapa_Selectores**: Configuración dinámica versionada que asocia Selectores_CSS a campos del Esquema_Inmueble para un Sitio_Origen específico.
- **Upsert**: Operación de base de datos que inserta un registro nuevo si no existe, o actualiza el existente si ha cambiado.
- **Clave_Upsert**: Combinación única de `Código_Inmueble` + `Sitio_Origen` utilizada para identificar registros duplicados.
- **Sitio_Origen**: Dominio o identificador del sitio web inmobiliario del cual se extraen los datos.
- **Código_Inmueble**: Identificador único del inmueble dentro de un Sitio_Origen específico.
- **Esquema_Inmueble**: Estructura de 66 campos que define los atributos de un inmueble extraído, según el Diccionario de Datos.
- **Diccionario_Datos**: Documento de referencia que define los 66 campos del Esquema_Inmueble con sus tipos (Numérico, Texto, Fecha, Enlace URL, Texto Si/No, Numérico/Bool) y descripciones.
- **Log_Error**: Registro estructurado de errores ocurridos durante el proceso de scraping, clasificados por tipo (Timeout, CAPTCHA, Estructura, Conexión).
- **CAPTCHA**: Mecanismo de verificación anti-bot que requiere interacción humana para continuar la navegación.
- **Navegación_Recursiva**: Proceso de seguir enlaces dentro de un dominio base para descubrir páginas de listados y detalle de inmuebles.
- **Profundidad_Navegación**: Número máximo de niveles de enlaces que el ENGINE seguirá desde la URL base (entre 1 y 10).
- **Backoff_Exponencial**: Estrategia de reintento donde el tiempo de espera se duplica en cada intento consecutivo fallido, hasta un máximo definido.
- **Exportación**: Proceso asíncrono de generación de archivos (CSV, Excel, JSON) con datos filtrados del Esquema_Inmueble.
- **Correlation_ID**: Identificador único propagado en cada petición entre capas para trazabilidad de operaciones.

## Requisitos

### Requisito 1: Gestión CRUD de Configuraciones de Scraping

**Historia de Usuario:** Como operador de la plataforma, quiero crear, leer, actualizar y eliminar configuraciones de scraping, para poder gestionar las fuentes de datos inmobiliarios de forma flexible.

#### Criterios de Aceptación

1. THE PARAM_FRONT SHALL provide a form to create a new Configuración_Scraping with the following fields: URL base, Profundidad_Navegación, tipo de operación (Venta/Arriendo), and modo de ejecución (Manual/Programado).
2. WHEN a new Configuración_Scraping is submitted, THE PARAM_FRONT SHALL validate that the URL base is a well-formed HTTP or HTTPS URL before persisting the record.
3. WHEN a Configuración_Scraping is submitted with a Profundidad_Navegación value, THE PARAM_FRONT SHALL validate that the value is an integer between 1 and 10.
4. WHEN a Configuración_Scraping has modo de ejecución set to Programado, THE PARAM_FRONT SHALL require a valid cron expression and display a human-readable preview of the schedule.
5. THE PARAM_FRONT SHALL display a paginated list of all existing Configuración_Scraping records with their URL base, tipo de operación, modo de ejecución, estado activo, and fecha de última ejecución.
6. WHEN an operator selects an existing Configuración_Scraping, THE PARAM_FRONT SHALL allow editing of all configurable fields and persist the changes.
7. WHEN an operator requests deletion of a Configuración_Scraping, THE PARAM_FRONT SHALL perform a soft delete by marking the record as inactive rather than removing the record from the database.
8. IF a Configuración_Scraping submission fails validation, THEN THE PARAM_FRONT SHALL display specific error messages indicating which fields are invalid and the reason for each validation failure.

### Requisito 2: Programación y Ejecución de Tareas de Scraping

**Historia de Usuario:** Como operador de la plataforma, quiero programar ejecuciones automáticas y lanzar ejecuciones manuales de scraping, para poder recolectar datos de forma continua o bajo demanda.

#### Criterios de Aceptación

1. WHEN an operator triggers a manual execution for a Configuración_Scraping, THE Scheduler SHALL create and enqueue a Tarea_Scraping for that configuration within 5 seconds.
2. WHILE a Configuración_Scraping has modo de ejecución set to Programado, THE Scheduler SHALL execute the Tarea_Scraping at the configured cron interval.
3. WHEN a scheduled execution time arrives, THE Scheduler SHALL create a new Tarea_Scraping and pass the associated Configuración_Scraping to the ENGINE.
4. IF a Tarea_Scraping is already running for a given Configuración_Scraping when a new execution is triggered, THEN THE Scheduler SHALL skip the new execution and log a warning indicating the overlap.
5. WHEN a Tarea_Scraping completes, THE Scheduler SHALL record the execution end time, duration in seconds, number of pages processed, records extracted, records inserted, records updated, records skipped, and final status (success, partial_success, failure).
6. THE Scheduler SHALL allow operators to configure cron expressions for scheduled executions through the PARAM_FRONT.
7. WHEN a Tarea_Scraping changes status, THE Plataforma SHALL notify connected PARAM_FRONT clients via WebSocket with the updated task status and summary.

### Requisito 3: Motor de Scraping con Navegación Recursiva

**Historia de Usuario:** Como operador de la plataforma, quiero que el motor de scraping navegue recursivamente dentro de los dominios configurados, para poder extraer datos de todas las páginas de listados y detalle de inmuebles.

#### Criterios de Aceptación

1. WHEN a Tarea_Scraping is started, THE ENGINE SHALL load the Mapa_Selectores associated with the Sitio_Origen of the Configuración_Scraping.
2. WHEN the ENGINE processes a listing page, THE ENGINE SHALL extract all internal links within the same base domain and add discovered links to the crawl queue up to the configured Profundidad_Navegación.
3. WHILE navigating recursively, THE ENGINE SHALL track all visited URLs and skip URLs that have already been processed in the current execution.
4. WHEN the ENGINE identifies a property detail page, THE ENGINE SHALL extract data for all 66 fields of the Esquema_Inmueble using the Mapa_Selectores.
5. WHEN a field defined in the Esquema_Inmueble is not found on the page, THE ENGINE SHALL set the field value to null rather than omitting the field from the extracted record.
6. THE ENGINE SHALL respect the configured Profundidad_Navegación and stop following links beyond the specified depth level.
7. WHEN the ENGINE encounters an unrecoverable error on a specific URL, THE ENGINE SHALL log the error, skip the URL, and continue processing the remaining URLs in the crawl queue.

### Requisito 4: Mapeo Dinámico de Selectores CSS

**Historia de Usuario:** Como operador de la plataforma, quiero configurar mapeos de selectores CSS por sitio de origen, para poder adaptar la extracción a la estructura HTML de cada sitio inmobiliario.

#### Criterios de Aceptación

1. THE PARAM_FRONT SHALL provide an interface to create and edit a Mapa_Selectores for each Sitio_Origen, associating each campo del Esquema_Inmueble with one or more Selectores_CSS.
2. WHEN a Mapa_Selectores is saved, THE PARAM_FRONT SHALL validate that each Selector_CSS entry is a syntactically valid CSS selector.
3. WHEN the ENGINE applies a Mapa_Selectores to a page, THE ENGINE SHALL attempt each configured Selector_CSS for a field in order and use the first match that returns a non-empty value.
4. IF none of the configured Selectores_CSS for a field return a value, THEN THE ENGINE SHALL set the field to null and log a warning with the field name, Sitio_Origen, and URL of the page.
5. WHEN an operator updates a Mapa_Selectores, THE PARAM_FRONT SHALL increment the version number and preserve the previous version so that historical extractions can reference the selectors used at the time of extraction.

### Requisito 5: Estrategia Anti-Bot y Stealth

**Historia de Usuario:** Como operador de la plataforma, quiero que el motor de scraping implemente técnicas de evasión anti-bot, para poder extraer datos sin ser bloqueado por los sitios objetivo.

#### Criterios de Aceptación

1. WHEN the ENGINE sends an HTTP request, THE ENGINE SHALL select a User_Agent string at random from a pool of at least 20 current browser User_Agent strings.
2. WHEN the ENGINE navigates between pages, THE ENGINE SHALL introduce a random delay between 2 and 7 seconds before each request.
3. THE ENGINE SHALL use Playwright to render pages with full JavaScript execution, emulating a real browser session.
4. WHEN the ENGINE starts a new browser session, THE ENGINE SHALL configure the browser to disable WebDriver detection flags, set a realistic viewport size selected randomly from common resolutions (1280x720, 1366x768, 1920x1080), and enable standard browser plugins emulation.
5. IF the ENGINE receives an HTTP 429 (Too Many Requests) response, THEN THE ENGINE SHALL apply Backoff_Exponencial starting at 30 seconds and doubling on each consecutive 429 response, up to a maximum of 10 minutes.
6. IF the ENGINE detects a CAPTCHA challenge on a page, THEN THE ENGINE SHALL log the CAPTCHA event as a Log_Error of type CAPTCHA, skip the current page, and continue with the next URL in the crawl queue.
7. WHEN the ENGINE has processed 50 requests within a single browser session, THE ENGINE SHALL rotate the browser session by clearing cookies, localStorage, and creating a new browser context with a fresh fingerprint.

### Requisito 6: Lógica Upsert de Datos Inmobiliarios

**Historia de Usuario:** Como operador de la plataforma, quiero que el sistema deduplique registros inmobiliarios usando la combinación de código de inmueble y sitio de origen, para poder mantener datos actualizados sin duplicados.

#### Criterios de Aceptación

1. WHEN the DATA_LOGIC receives an extracted record, THE DATA_LOGIC SHALL compute the Clave_Upsert by combining the values of Código_Inmueble and Sitio_Origen.
2. WHEN the DATA_LOGIC processes a record whose Clave_Upsert does not exist in the database, THE DATA_LOGIC SHALL insert the record as a new entry with Fecha_Control set to the current timestamp and Estado_Activo set to true.
3. WHEN the DATA_LOGIC processes a record whose Clave_Upsert already exists in the database and at least one field value has changed, THE DATA_LOGIC SHALL update the existing record with the new values and set Fecha_Actualizacion to the current timestamp.
4. WHEN the DATA_LOGIC processes a record whose Clave_Upsert already exists in the database and no field values have changed, THE DATA_LOGIC SHALL skip the update and leave the existing record unchanged.
5. WHEN the DATA_LOGIC detects a price change during an Upsert update, THE DATA_LOGIC SHALL compute the difference between the new Precio_Local and the previous Precio_Local, store the result in Cambio_Precio_Valor, and set Precio_Bajo to true if the new price is lower than the previous price, or false otherwise.
6. THE DATA_LOGIC SHALL enforce a unique constraint on the combination of Código_Inmueble and Sitio_Origen at the database level using PostgreSQL ON CONFLICT.
7. THE DATA_LOGIC SHALL execute each Upsert operation within a database transaction to guarantee consistency.
8. FOR ALL valid Esquema_Inmueble records, inserting a record and then querying by its Clave_Upsert SHALL return a record equivalent to the original (round-trip property).

### Requisito 7: Registro Estructurado de Errores

**Historia de Usuario:** Como operador de la plataforma, quiero que todos los errores de scraping se registren de forma estructurada y clasificada, para poder diagnosticar problemas y mejorar la fiabilidad del sistema.

#### Criterios de Aceptación

1. WHEN an error occurs during scraping, THE DATA_LOGIC SHALL create a Log_Error record with the following fields: timestamp, Sitio_Origen, URL, error type (Timeout, CAPTCHA, Estructura, Conexión), error message, error metadata as JSON, and Tarea_Scraping identifier.
2. IF the ENGINE encounters a request timeout, THEN THE DATA_LOGIC SHALL classify the error as type Timeout and record the configured timeout threshold and elapsed time in the error metadata.
3. IF the ENGINE detects a CAPTCHA challenge, THEN THE DATA_LOGIC SHALL classify the error as type CAPTCHA and record the URL and page title where the CAPTCHA was encountered in the error metadata.
4. IF the ENGINE fails to extract a required field due to a missing or changed HTML structure, THEN THE DATA_LOGIC SHALL classify the error as type Estructura and record the field name, expected Selector_CSS, and the Sitio_Origen in the error metadata.
5. IF the ENGINE encounters a network connection failure, THEN THE DATA_LOGIC SHALL classify the error as type Conexión and record the URL and the connection error details in the error metadata.
6. THE DATA_LOGIC SHALL persist all Log_Error records in a dedicated error table separate from the main Esquema_Inmueble data table.
7. WHEN a Tarea_Scraping completes, THE DATA_LOGIC SHALL generate an execution summary containing total pages processed, total records extracted, total records inserted, total records updated, total records skipped, total errors grouped by type, and execution duration in seconds.

### Requisito 8: Esquema de Datos de 66 Campos

**Historia de Usuario:** Como operador de la plataforma, quiero que todos los inmuebles extraídos se almacenen siguiendo un esquema estandarizado de 66 campos, para poder consultar y comparar datos de diferentes fuentes de forma uniforme.

#### Criterios de Aceptación

1. THE DATA_LOGIC SHALL store each extracted property record with exactly 66 fields as defined in the Diccionario_Datos: Id_Interno, Código_Inmueble, Tipo_Inmueble, Habitaciones, Baños, Operacion, Estacionamiento, Administracion_Valor, Antiguedad_Detalle, Rango_Antiguedad, Tipo_Estudio, Es_Loft, Dueño_Anuncio, Telefono_Principal, Telefono_Opcional, Correo_Contacto, Tipo_Publicador, Descripcion_Anuncio, Fecha_Control, Fecha_Actualizacion, Municipio, Amoblado, Titulo_Anuncio, Metros_Utiles, Metros_Totales, Orientacion, Latitud, Longitud, Url_Anuncio, Url_Imagen_Principal, Sector, Barrio, Estrato, Sitio_Origen, Fecha_Publicacion, Direccion, Estado_Activo, Fecha_Desactivacion, Precio_USD, Precio_Local, Simbolo_Moneda, Piso_Propiedad, Tiene_Ascensores, Tiene_Balcones, Tiene_Seguridad, Tiene_Bodega_Deposito, Tiene_Terraza, Cuarto_Servicio, Baño_Servicio, Tiene_Calefaccion, Tiene_Alarma, Acceso_Controlado, Circuito_Cerrado, Estacionamiento_Visita, Cocina_Americana, Tiene_Gimnasio, Tiene_BBQ, Tiene_Piscina, En_Conjunto_Residencial, Uso_Comercial, Cambio_Precio_Valor, Precio_Bajo, Tipo_Empresa, Glosa_Administracion, Area_Privada, Area_Construida.
2. THE DATA_LOGIC SHALL auto-generate the Id_Interno field as a unique sequential identifier for each new record inserted.
3. WHEN a numeric field (Habitaciones, Baños, Estacionamiento, Administracion_Valor, Metros_Utiles, Metros_Totales, Latitud, Longitud, Estrato, Precio_USD, Precio_Local, Piso_Propiedad, Cambio_Precio_Valor, Area_Privada, Area_Construida) contains a non-numeric extracted value, THE DATA_LOGIC SHALL attempt to parse the numeric portion and log a warning if parsing fails.
4. WHEN a boolean field (Tipo_Estudio, Es_Loft, Tiene_Ascensores, Tiene_Balcones, Tiene_Seguridad, Tiene_Bodega_Deposito, Tiene_Terraza, Cuarto_Servicio, Baño_Servicio, Tiene_Calefaccion, Tiene_Alarma, Acceso_Controlado, Circuito_Cerrado, Estacionamiento_Visita, Cocina_Americana, Tiene_Gimnasio, Tiene_BBQ, Tiene_Piscina, En_Conjunto_Residencial, Uso_Comercial, Precio_Bajo) contains a value that cannot be interpreted as true or false, THE DATA_LOGIC SHALL set the field to null and log a warning.
5. WHEN a date field (Fecha_Control, Fecha_Actualizacion, Fecha_Publicacion, Fecha_Desactivacion) contains a value, THE DATA_LOGIC SHALL parse the value into a valid date format and log a warning if parsing fails.
6. THE DATA_LOGIC SHALL validate that Latitud is a decimal value between -90 and 90 and Longitud is a decimal value between -180 and 180 when the values are present.
7. THE DATA_LOGIC SHALL validate that Url_Anuncio and Url_Imagen_Principal are well-formed URLs when the values are present.

### Requisito 9: Serialización y Deserialización de Registros Inmobiliarios

**Historia de Usuario:** Como operador de la plataforma, quiero que los registros inmobiliarios se puedan serializar a JSON y deserializar de vuelta sin pérdida de datos, para poder exportar, importar y transferir datos de forma fiable.

#### Criterios de Aceptación

1. THE DATA_LOGIC SHALL serialize any Esquema_Inmueble record to a JSON string preserving all 66 fields, including null values.
2. WHEN the DATA_LOGIC deserializes a JSON string, THE DATA_LOGIC SHALL reconstruct an Esquema_Inmueble record with all field types correctly restored (strings, numbers, booleans, dates, nulls).
3. FOR ALL valid Esquema_Inmueble records, serializing to JSON and then deserializing SHALL produce a record equivalent to the original (round-trip property).
4. IF a JSON string contains fields not defined in the Esquema_Inmueble, THEN THE DATA_LOGIC SHALL ignore the extra fields and log a warning.
5. IF a JSON string is missing required fields (Código_Inmueble, Sitio_Origen), THEN THE DATA_LOGIC SHALL return a descriptive error indicating the missing fields.

### Requisito 10: Dashboard de Consulta y Exportación

**Historia de Usuario:** Como operador de la plataforma, quiero consultar los datos extraídos mediante filtros y exportarlos en diferentes formatos, para poder analizar la información inmobiliaria recolectada.

#### Criterios de Aceptación

1. THE DASHBOARD SHALL provide a search interface that allows filtering Esquema_Inmueble records by any combination of: Sitio_Origen, Tipo_Inmueble, Operacion, Municipio, Sector, Barrio, Estrato, rango de Precio_Local, rango de Metros_Totales, Estado_Activo, and rango de Fecha_Control.
2. WHEN an operator applies filters, THE DASHBOARD SHALL display matching records in a paginated table showing a configurable subset of the 66 fields.
3. WHEN an operator requests an export, THE DASHBOARD SHALL generate a downloadable file in the selected format (CSV, Excel, JSON) containing all records matching the current filter criteria.
4. THE DASHBOARD SHALL display a summary panel showing total records by Sitio_Origen, total records by Operacion, total active records, and the timestamp of the last successful Tarea_Scraping.
5. WHEN an operator selects a single record in the DASHBOARD, THE DASHBOARD SHALL display a detail view showing all 66 fields of the Esquema_Inmueble for that record.
6. THE DASHBOARD SHALL display the Log_Error records with filters for error type, Sitio_Origen, Tarea_Scraping, and date range.
7. WHEN an export contains more than 100,000 records, THE DASHBOARD SHALL generate the export file asynchronously via a background worker and notify the operator via the UI when the file is ready for download.

### Requisito 11: Detección de Desactivación de Inmuebles

**Historia de Usuario:** Como operador de la plataforma, quiero que el sistema detecte cuando un inmueble ya no está publicado en el sitio de origen, para poder mantener el estado de los listados actualizado.

#### Criterios de Aceptación

1. WHEN the ENGINE completes processing a Sitio_Origen and a previously active record (Estado_Activo = true) with a matching Clave_Upsert is not found in the current extraction results, THE DATA_LOGIC SHALL set Estado_Activo to false and Fecha_Desactivacion to the current timestamp for that record.
2. WHEN a previously deactivated record (Estado_Activo = false) is found again in a subsequent extraction, THE DATA_LOGIC SHALL set Estado_Activo to true and set Fecha_Desactivacion to null.
3. THE DATA_LOGIC SHALL only evaluate deactivation for records belonging to the Sitio_Origen being processed in the current Tarea_Scraping, leaving records from other Sitio_Origen values unchanged.

### Requisito 12: Seguridad y Control de Acceso

**Historia de Usuario:** Como administrador de la plataforma, quiero que el acceso al sistema esté protegido por autenticación y autorización basada en roles, para poder controlar quién puede gestionar configuraciones y acceder a los datos.

#### Criterios de Aceptación

1. THE Plataforma SHALL require authentication via username and password before granting access to any module (PARAM_FRONT, DASHBOARD).
2. WHEN a user provides valid credentials, THE Plataforma SHALL issue a JWT access token with an expiration of 30 minutes and a refresh token stored in an httpOnly cookie.
3. WHEN a user provides invalid credentials, THE Plataforma SHALL deny access and display a generic error message without revealing whether the username or password was incorrect.
4. THE Plataforma SHALL enforce role-based access control (RBAC) with at least two roles: Administrador (full access to all modules including configuration write operations and task execution) and Operador (read access to PARAM_FRONT and full access to DASHBOARD including exports).
5. WHEN a JWT access token expires, THE Plataforma SHALL allow token renewal using the refresh token without requiring re-authentication.
6. WHEN a user session has been inactive for more than 30 minutes, THE Plataforma SHALL invalidate the session and require re-authentication.
7. THE Plataforma SHALL hash all user passwords using bcrypt before storing them in the database.

### Requisito 13: Monitoreo de Ejecuciones de Scraping

**Historia de Usuario:** Como operador de la plataforma, quiero visualizar el historial y estado de las ejecuciones de scraping, para poder monitorear el rendimiento del sistema y detectar problemas.

#### Criterios de Aceptación

1. THE DASHBOARD SHALL display a paginated list of all Tarea_Scraping executions with: task identifier, Configuración_Scraping name, status (queued, running, success, partial_success, failure), start time, end time, duration, and record counts.
2. WHEN an operator selects a Tarea_Scraping, THE DASHBOARD SHALL display the execution detail including: records inserted, records updated, records skipped, and errors grouped by type (Timeout, CAPTCHA, Estructura, Conexión).
3. WHILE a Tarea_Scraping is running, THE DASHBOARD SHALL display real-time progress updates received via WebSocket including current page count and record count.
4. THE DASHBOARD SHALL allow filtering Tarea_Scraping records by status, Configuración_Scraping, date range, and Sitio_Origen.

### Requisito 14: Trazabilidad y Observabilidad

**Historia de Usuario:** Como administrador de la plataforma, quiero que todas las operaciones del sistema sean trazables y observables, para poder diagnosticar problemas y auditar el comportamiento del sistema.

#### Criterios de Aceptación

1. WHEN the Plataforma receives an API request, THE Plataforma SHALL generate a unique Correlation_ID and propagate the Correlation_ID through all internal operations, worker tasks, and database operations associated with that request.
2. THE Plataforma SHALL emit structured JSON logs with the following fields for every operation: timestamp, level, service name, Correlation_ID, and message.
3. WHEN the ENGINE starts a Tarea_Scraping, THE ENGINE SHALL log the Configuración_Scraping identifier, Sitio_Origen, Profundidad_Navegación, and Mapa_Selectores version being used.
4. THE Plataforma SHALL apply rate limiting on all API endpoints, allowing a maximum of 100 requests per minute per authenticated user, and return HTTP 429 with a Retry-After header when the limit is exceeded.
