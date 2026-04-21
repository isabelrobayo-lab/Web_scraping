---
inclusion: always
---

# Reglas de Arquitectura — Seguros Bolívar (v1.0)

Reglas obligatorias que el Architect agent debe aplicar al diseñar soluciones para **Seguros y Servicios Bolívar**. Estas reglas aplican a todo tipo de proyecto (backend-only, full-stack, APIs, microservicios, etc.) — el agente debe evaluar cuáles son relevantes según el alcance de cada iniciativa.

---

## Regla Principal: Consistencia

**"Un proyecto debe parecer escrito por una sola persona"**

- Antes de modificar código, identificar el patrón estándar existente y replicarlo.
- Se prohíbe el *vibe coding* (programar por intuición del momento). No inventar nuevas formas.
- El código debe ser lo suficientemente claro para permitir correcciones en menos de **1 día** en casos críticos y **5 días** para temas no productivos.

> Para convenciones de naming, type hints, imports y estilo Python, ver `code-standard.md`.

---

## Estándar de Solución: Separación de Capas

Cuando el proyecto lo requiera, estructurar en capas independientes:

- **Presentación (Frontend):** Renderizado de UI y eventos de usuario. **NUNCA** lógica de negocio. *Aplica solo si el proyecto tiene frontend.*
- **Lógica (Backend/API):** Reglas de dominio, cálculos y validaciones de seguridad. *Siempre aplica.*
- **Persistencia (Datos):** Repositorios oficiales. Conexión siempre vía API, nunca directa desde frontend. *Aplica si hay capa de datos.*

El agente debe determinar qué capas son necesarias según el tipo de proyecto y documentar la decisión.

**Regla de Usabilidad:** Si hay interfaz de usuario, toda funcionalidad principal debe ser ejecutable en un máximo de **5 clics**.

---

## Seguridad y Protección de Datos

Aplican a **todo** tipo de proyecto:

- **Identidad y Acceso (IAM):**
  - Uso obligatorio de **OAuth 2.0 y OpenID Connect (OIDC)** para autenticación y autorización.
  - Comunicación entre capas/servicios protegida mediante **JWT** firmados por el proveedor de identidad institucional.
  - Autorización basada en **Roles y Scopes (RBAC)** validados en el Backend; no se permite lógica de permisos quemada en el código.
- **Enmascaramiento:** 100% de datos sensibles (PII, financiero, salud) enmascarados en respuestas de API.
- **Comunicación DNS:** Prohibido el uso de IPs fijas. Comunicación exclusivamente mediante nombres de dominio o DNS.
- **Gestión de Secretos:** No incluir API keys o credenciales en código fuente. Uso obligatorio de **Variables de Entorno** o **Secret Manager**.
- **Tokens:** No almacenar en `localStorage`; usar `httpOnly cookies` cuando aplique frontend.
- **Sanitización:** Definición estricta de tipos de datos en todos los campos para evitar inyecciones.
- **Retención de Datos:** Políticas de borrado que no superen **90 días**.

---

## Resiliencia, Desempeño y Operación

- **Métricas de Desempeño:**
  - Frontend (si aplica): respuesta en menos de **3 segundos**.
  - Backend/APIs: procesamiento no mayor a **15 segundos**.
- **Capacidad de Concurrencia:** La solución debe operar adecuadamente según la volumetría definida.
- **Trazabilidad:** Inserción obligatoria de un `Correlation-ID` en cada petición entre capas/servicios.
- **Observabilidad:** Logs estandarizados enviados a servicios centrales definidos por la compañía (validados con el área de observabilidad). Nunca almacenados localmente.
- **Manejo de Fallos:** Implementar **Retries** y **Circuit Breakers** para el 100% de los errores sin provocar cierres inesperados.
- **Asincronía:** Tareas de larga duración (reportes masivos, modelos de IA) en segundo plano para no bloquear la UI o el caller.
- **Throttling:** Rate Limiting para proteger componentes core como **CONECTA** o **COMUNES**.
- **Versionamiento de API (API First):** Cambios en estructura de datos entre servicios deben ser versionados con prefijos en rutas (ej: `/v1/api/`, `/v2/api/`).

---

## Ciclo de Vida y Gobierno de TI

- **Fuentes Oficiales:** Toda librería debe descargarse del repositorio institucional (**JFrog**).
- **Versionamiento:** Código obligatoriamente en el repositorio oficial de la compañía.
- **Separación de Entornos:** Desarrollo, Stage y Producción físicamente separados.
- **Cierre Limpio (Graceful Shutdown):** La aplicación debe completar transacciones en curso antes de finalizar procesos de reinicio o despliegue.
