---
inclusion: always
---

# Reglas de Seguridad — Organización

Reglas estandarizadas de seguridad para desarrollo asistido por IA. Deben enforcarse en todos los proyectos para cumplir con las políticas de seguridad organizacionales.

---

## 1. Authentication & Authorization

- **Nunca hardcodear credenciales** (passwords, API keys, tokens, secretos) en código fuente o archivos de configuración versionados.
- Usar **secrets manager** (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault) para almacenar y recuperar valores sensibles en runtime.
- Implementar **least-privilege access** para todas las cuentas de servicio, roles y políticas IAM.
- Enforcar **MFA** para todo acceso humano a sistemas de producción e interfaces administrativas.
- Usar **tokens de corta vida** (OAuth2, JWT) con expiración y refresh adecuados.
- Validar y verificar **firmas JWT** en el servidor para cada endpoint protegido.

## 2. Input Validation & Injection Prevention

- **Validar todo input externo** en boundaries del sistema (API endpoints, forms, file uploads, query params).
- Usar **parameterized queries** o métodos ORM para toda interacción con base de datos. Nunca concatenar input de usuario en SQL.
- Aplicar **output encoding** (HTML, URL, JavaScript, CSS) apropiado al contexto para prevenir XSS.
- Sanitizar nombres de archivo y paths para prevenir **path traversal**.
- Restringir métodos HTTP, content types y payload sizes permitidos.

## 3. Dependency & Supply Chain Security

- **Escanear dependencias** por vulnerabilidades conocidas (CVEs) con herramientas automatizadas (Dependabot, Snyk, Trivy) en cada pipeline CI.
- Fijar versiones de dependencias explícitamente. Evitar rangos flotantes (`^`, `~`, `*`) en manifiestos de producción.
- Revisar y aprobar nuevas dependencias antes de adopción.
- Usar **registros privados de artefactos** para paquetes internos.
- Verificar **integridad de paquetes** con checksums o lock files.

## 4. Data Protection & Encryption

- Encriptar datos **at rest** con AES-256 o equivalente.
- Encriptar datos **in transit** con TLS 1.2+ para todas las comunicaciones. Deshabilitar protocolos antiguos.
- Clasificar datos según niveles de sensibilidad (público, interno, confidencial, restringido).
- **Nunca loguear datos sensibles** (passwords, tokens, tarjetas de crédito, PII, datos de salud).
- Implementar **key rotation** para encryption keys, API keys y certificados.

## 5. Secure Coding Practices

- Seguir **OWASP Top 10** como baseline mínimo para seguridad de aplicaciones web.
- Implementar **error handling** que no exponga detalles internos (stack traces, errores de DB, paths internos).
- Usar **security headers** en respuestas HTTP: `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, `Referrer-Policy`.
- Deshabilitar **debug mode** y logging verbose en producción.
- Aplicar **rate limiting** y **throttling** en APIs públicas.

## 6. Secrets Management

- Secretos exclusivamente en **vault o secrets management** aprobados. Nunca `.env` files en producción.
- Rotar secretos en schedule definido e inmediatamente ante sospecha de compromiso.
- Auditar y loguear todo **acceso a secretos**.
- Usar **secretos por ambiente** — nunca compartir secretos entre dev, staging y producción.
- Implementar **secret scanning** en CI/CD y pre-commit hooks (gitleaks, trufflehog).

## 7. Logging, Monitoring & Incident Response

- Loguear todos los **eventos de autenticación** (login success/failure, token refresh, logout) con timestamps y source IPs.
- Loguear todos los **authorization failures** y access denied events.
- Centralizar logs en **SIEM o plataforma de log aggregation**.
- **Alertas** para patrones anómalos: failed logins repetidos, privilege escalation, tráfico API inusual.
- Mantener **incident response plan** con roles, canales de comunicación y procedimientos de escalación.

## 8. API Security

- Autenticar todas las llamadas API. No exponer endpoints sin autenticación salvo aprobación explícita.
- Implementar **CORS policies** que restrinjan orígenes a dominios conocidos y confiables.
- Usar **API gateways** para enforcar rate limiting, autenticación, validación y logging centralmente.
- Versionar APIs explícitamente y deprecar versiones antiguas con aviso adecuado.
- Validar **request y response schemas** contra definiciones OpenAPI/Swagger.

## 9. Container & Runtime Security

- Usar **minimal base images** (distroless, Alpine) y no ejecutar contenedores como root.
- Escanear imágenes de contenedores por vulnerabilidades antes de deployment.
- Definir **read-only file systems** donde sea posible y eliminar Linux capabilities innecesarias.
- Nunca almacenar secretos en imágenes de contenedores o Dockerfiles. Inyectar en runtime.
- Enforcar **network policies** para restringir comunicación container-to-container.

## 10. Compliance & Governance

- Cumplir con **frameworks regulatorios** aplicables (PCI-DSS, SOC 2, ISO 27001, GDPR, Habeas Data).
- **Security reviews** para todos los cambios arquitectónicos y nuevas integraciones antes de producción.
- **Penetration testing** y vulnerability assessments periódicos en sistemas de producción.
- Mantener **asset inventory** actualizado de todos los servicios, endpoints y data stores.
- Documentar y enforcar un proceso **SSDLC** (Secure Software Development Lifecycle).
