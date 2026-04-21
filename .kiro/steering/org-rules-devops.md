---
inclusion: always
---

# Reglas DevOps — Organización

Reglas estandarizadas de DevOps para desarrollo asistido por IA. Gobiernan pipelines CI/CD, automatización, gestión de releases y prácticas operativas.

---

## 1. CI/CD Pipeline Standards

- Todo repositorio debe tener un pipeline CI/CD definido como código (GitHub Actions, Azure DevOps YAML, GitLab CI, Jenkins Pipeline).
- Pipelines deben incluir mínimo: **build**, **test**, **static analysis**, **security scan** y **deploy**.
- Usar **workflow templates reutilizables** para consistencia entre equipos.
- Cambios en pipelines pasan por el mismo proceso de code review que el código de aplicación.

## 2. Branching & Version Control

- Seguir una estrategia de branching definida (GitFlow, GitHub Flow, trunk-based) consistentemente.
- Proteger **main/master** — requerir PRs, al menos una aprobación y CI passing antes de merge.
- Usar **semantic versioning** (SemVer: `MAJOR.MINOR.PATCH`) para todos los releases.
- Branches de corta vida — feature branches no deben permanecer abiertas más de unos días.

## 3. Build & Artifact Management

- Builds deben ser **reproducibles** — mismo commit = artefactos idénticos.
- Artefactos en **registro centralizado** (JFrog Artifactory, GitHub Packages, Nexus).
- Etiquetar artefactos con **Git commit SHA**, build number y versión semántica.
- Nunca construir artefactos localmente para producción. Todo viene del **pipeline CI**.

## 4. Testing in Pipelines

- **Unit tests** en cada commit y PR. Fallar el pipeline si no pasan.
- **Integration tests** para servicios con dependencias externas.
- Enforcar **cobertura mínima** (ej. 80%) y fallar si baja del umbral.
- **Static analysis** (SonarQube, ESLint) y **security scanning** (SAST, SCA) como stages obligatorios.
- **Smoke tests** después de cada deployment.

## 5. Deployment Strategies

- Usar **progressive deployment** (blue-green, canary, rolling updates) para producción.
- Implementar **rollback automático** por health check failures o error rate.
- Desplegar a ambientes inferiores **antes** de producción — nunca saltar ambientes.
- Usar **feature flags** para desacoplar deployment de release.

## 6. Environment Management

- Configuraciones por ambiente en **variable files** o configuration services. Nunca hardcodear valores.
- **Promotion** automatizada con approval gates para producción.
- **Ephemeral environments** para feature testing y PR previews cuando sea factible.

## 7. Containerization & Orchestration

- **Multi-stage Dockerfiles** para minimizar tamaño e imagen de ataque.
- Dockerfiles en el **repositorio de la aplicación**.
- **Health probes** (liveness, readiness, startup) para todos los servicios containerizados.
- **Helm charts** o Kustomize en version control.

## 8. Monitoring, Logging & Alerting

- Tres pilares de observabilidad: **metrics, logs, traces** para cada servicio.
- **Structured logging** (JSON) con campos consistentes: `timestamp`, `level`, `service`, `correlation-id`, `message`.
- Definir **SLIs** y **SLOs** para servicios críticos.
- **Alertas accionables** con severidad, escalación y runbooks. Evitar alert fatigue.

## 9. GitOps & Configuration Management

- Gestionar estado de Kubernetes/infra con **GitOps** — Git como single source of truth.
- Herramientas como **ArgoCD** o **Flux** para reconciliar estado deseado vs actual.
- **Drift detection** para alertar desviaciones.
- Cambios a producción vía **PRs con aprobaciones** — no ediciones directas.

## 10. Operational Excellence

- Mantener **runbooks** para tareas operativas comunes.
- **Post-incident reviews** (blameless postmortems) después de cada incidente de producción.
- Automatizar **toil** — toda tarea manual repetitiva que pueda automatizarse.
- Trackear y mejorar **DORA metrics**: deployment frequency, lead time, change failure rate, time to restore.
