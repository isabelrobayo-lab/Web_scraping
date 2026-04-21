# Security Rules

> Standardized security rules for AI-assisted development. These rules must be enforced across all projects to ensure compliance with organizational security policies.

---

## 1. Authentication & Authorization

- **Never hardcode credentials** (passwords, API keys, tokens, secrets) in source code, configuration files, or environment files committed to version control.
- Use a **secrets manager** (e.g., Azure Key Vault, AWS Secrets Manager, HashiCorp Vault) to store and retrieve sensitive values at runtime.
- Implement **least-privilege access** for all service accounts, roles, and IAM policies.
- Enforce **multi-factor authentication (MFA)** for all human access to production systems and administrative interfaces.
- Use **short-lived tokens** (OAuth2, JWT) with proper expiration and refresh mechanisms. Never issue tokens without an expiry.
- Validate and verify **JWT signatures** on the server side for every protected endpoint.

## 2. Input Validation & Injection Prevention

- **Validate all external input** at system boundaries (API endpoints, form submissions, file uploads, query parameters).
- Use **parameterized queries** or ORM-provided methods for all database interactions. Never concatenate user input into SQL statements.
- Apply **output encoding** (HTML, URL, JavaScript, CSS) appropriate to the context to prevent Cross-Site Scripting (XSS).
- Sanitize file names and paths to prevent **path traversal** attacks (`../`, encoded variants).
- Restrict allowed HTTP methods, content types, and payload sizes at the API gateway or application level.

## 3. Dependency & Supply Chain Security

- **Scan dependencies** for known vulnerabilities (CVEs) using automated tools (e.g., Dependabot, Snyk, Trivy) in every CI pipeline run.
- Pin dependency versions explicitly. Avoid floating version ranges (e.g., `^`, `~`, `*`) in production manifests.
- Review and approve new dependencies before adoption. Evaluate maintenance status, license compatibility, and known issues.
- Use **private artifact registries** for internal packages and configure registries to proxy and cache public packages.
- Verify **package integrity** using checksums or lock files (`package-lock.json`, `poetry.lock`, `go.sum`).

## 4. Data Protection & Encryption

- Encrypt data **at rest** using AES-256 or equivalent for databases, storage accounts, and backups.
- Encrypt data **in transit** using TLS 1.2+ for all communications. Disable older protocols (SSL, TLS 1.0, TLS 1.1).
- Classify data according to organizational sensitivity levels (public, internal, confidential, restricted) and apply controls accordingly.
- **Never log sensitive data** such as passwords, tokens, credit card numbers, personal identifiable information (PII), or health records.
- Implement proper **key rotation** policies for encryption keys, API keys, and certificates.

## 5. Secure Coding Practices

- Follow the **OWASP Top 10** as a minimum baseline for web application security.
- Implement proper **error handling** that does not expose internal details (stack traces, database errors, internal paths) to end users.
- Use **security headers** in HTTP responses: `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, `Referrer-Policy`.
- Disable **debug mode** and verbose logging in production environments.
- Apply **rate limiting** and **throttling** on public-facing APIs to mitigate brute-force and denial-of-service attacks.

## 6. Secrets Management

- Store secrets exclusively in approved **vault or secrets management** services. Never use `.env` files in production.
- Rotate secrets on a defined schedule and immediately upon suspected compromise.
- Audit and log all **secret access** events for traceability.
- Use **environment-specific secrets** — never share secrets across development, staging, and production.
- Implement **secret scanning** in CI/CD pipelines and pre-commit hooks to prevent accidental exposure (e.g., `gitleaks`, `trufflehog`).

## 7. Logging, Monitoring & Incident Response

- Log all **authentication events** (login success, failure, token refresh, logout) with timestamps and source IPs.
- Log all **authorization failures** and access denied events.
- Centralize logs in a **SIEM or log aggregation platform** (e.g., Azure Sentinel, Splunk, ELK).
- Set up **alerts** for anomalous patterns: repeated failed logins, privilege escalation attempts, unusual API traffic.
- Maintain an **incident response plan** with defined roles, communication channels, and escalation procedures.

## 8. API Security

- Authenticate all API calls. Do not expose unauthenticated endpoints unless explicitly required and approved.
- Implement **CORS policies** that restrict allowed origins to known, trusted domains.
- Use **API gateways** to enforce rate limiting, authentication, request validation, and logging centrally.
- Version APIs explicitly and deprecate old versions with adequate notice.
- Validate **request and response schemas** against OpenAPI/Swagger definitions.

## 9. Container & Runtime Security

- Use **minimal base images** (distroless, Alpine) and avoid running containers as root.
- Scan container images for vulnerabilities before deployment using tools like Trivy, Grype, or Snyk Container.
- Define **read-only file systems** where possible and drop unnecessary Linux capabilities.
- Never store secrets in container images or Dockerfiles. Inject them at runtime via secrets management.
- Enforce **network policies** to restrict container-to-container communication to only what is required.

## 10. Compliance & Governance

- Ensure all projects comply with applicable **regulatory frameworks** (e.g., PCI-DSS, SOC 2, ISO 27001, GDPR, Habeas Data).
- Conduct **security reviews** for all architectural changes and new integrations before deployment to production.
- Perform periodic **penetration testing** and vulnerability assessments on production systems.
- Maintain an up-to-date **asset inventory** of all services, endpoints, and data stores.
- Document and enforce a **secure software development lifecycle (SSDLC)** process for all teams.
