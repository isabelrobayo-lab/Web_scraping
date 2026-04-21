# DevOps Rules

> Standardized DevOps rules for AI-assisted development. These rules govern CI/CD pipelines, automation, release management, and operational practices across all projects.

---

## 1. CI/CD Pipeline Standards

- **Every repository must have a CI/CD pipeline** defined as code (GitHub Actions, Azure DevOps YAML Pipelines, GitLab CI, Jenkins Pipeline).
- Pipeline definitions must live **inside the repository** alongside the application code they build and deploy.
- Pipelines must include at minimum: **build**, **test**, **static analysis**, **security scan**, and **deploy** stages.
- Use **reusable workflow templates** or shared pipeline libraries to enforce consistency across teams and reduce duplication.
- Pipeline changes must go through the **same code review process** as application code (pull request, approval, merge).

## 2. Branching & Version Control

- Follow a defined **branching strategy** (GitFlow, GitHub Flow, trunk-based development) consistently across the organization.
- Protect the **main/master branch** — require pull requests, at least one approval, and passing CI checks before merging.
- Use **semantic versioning** (SemVer: `MAJOR.MINOR.PATCH`) for all releases and tag releases in Git.
- Keep branches **short-lived** — feature branches should not remain open for more than a few days.
- Squash or rebase commits before merging to maintain a **clean commit history** on the main branch.

## 3. Build & Artifact Management

- Builds must be **reproducible** — given the same commit, the build should produce identical artifacts.
- Store build artifacts in a **centralized artifact registry** (Azure Artifacts, JFrog Artifactory, GitHub Packages, Nexus).
- Tag artifacts with the **Git commit SHA**, build number, and semantic version for full traceability.
- Never build artifacts locally for production deployment. All production artifacts must come from the **CI pipeline**.
- Implement **artifact retention policies** — keep production artifacts for a defined period and clean up old development artifacts automatically.

## 4. Testing in Pipelines

- **Unit tests** must run on every commit and pull request. Fail the pipeline if tests do not pass.
- Include **integration tests** in the pipeline for services that depend on external systems (databases, APIs, queues).
- Enforce **minimum code coverage thresholds** (e.g., 80%) and fail the build if coverage drops below the threshold.
- Run **static code analysis** (SonarQube, ESLint, Checkstyle) and **security scanning** (SAST, SCA) as mandatory pipeline stages.
- Include **smoke tests** or health checks after each deployment to verify the release is functional.

## 5. Deployment Strategies

- Use **progressive deployment strategies** (blue-green, canary, rolling updates) for production releases.
- Implement **automated rollback** mechanisms triggered by health check failures or error rate thresholds.
- Deploy to lower environments (dev, QA, staging) **before production** — never skip environments.
- Use **feature flags** to decouple deployment from release, enabling dark launches and controlled rollouts.
- Maintain **environment parity** — staging must mirror production as closely as possible in configuration and infrastructure.

## 6. Environment Management

- Define environment configurations using **environment-specific variable files** or configuration services. Never hardcode environment values.
- Manage environment **promotion** through automated pipelines with proper approval gates for production.
- Document the **purpose and ownership** of each environment (dev, QA, staging, pre-production, production).
- Implement **access controls per environment** — restrict who can deploy to staging and production.
- Use **ephemeral environments** for feature testing and pull request previews when feasible.

## 7. Containerization & Orchestration

- Define container images using **multi-stage Dockerfiles** to minimize image size and attack surface.
- Store Dockerfiles in the **application repository** alongside the source code.
- Use **container orchestration** (Kubernetes, Azure Container Apps, ECS) for production workloads with defined resource requests and limits.
- Implement **health probes** (liveness, readiness, startup) for all containerized services.
- Define **Helm charts**, Kustomize overlays, or equivalent manifests for Kubernetes deployments and store them in version control.

## 8. Monitoring, Logging & Alerting

- Implement the **three pillars of observability**: metrics, logs, and traces for every service.
- Use **structured logging** (JSON format) with consistent fields: `timestamp`, `level`, `service`, `correlation-id`, `message`.
- Configure **centralized log aggregation** — all services must send logs to the organizational logging platform.
- Define **SLIs (Service Level Indicators)** and **SLOs (Service Level Objectives)** for critical services.
- Set up **actionable alerts** with clear severity levels, escalation paths, and runbooks. Avoid alert fatigue.

## 9. GitOps & Configuration Management

- Manage Kubernetes and infrastructure state using **GitOps** principles — Git as the single source of truth.
- Use tools like **ArgoCD** or **Flux** to reconcile desired state (Git) with actual state (cluster).
- Store all environment configurations, Kubernetes manifests, and Helm values in **dedicated Git repositories**.
- Implement **drift detection** to alert when the actual state deviates from the declared state in Git.
- Changes to production configuration must go through **pull requests with approvals** — no direct edits.

## 10. Operational Excellence

- Maintain **runbooks** for common operational tasks: scaling, restarting services, failover, incident triage.
- Conduct **post-incident reviews (blameless postmortems)** after every production incident and document action items.
- Automate **toil** — any manual, repetitive operational task that can be automated should be.
- Define **on-call schedules** and escalation policies with clear responsibilities and response time expectations.
- Track and improve **DORA metrics**: deployment frequency, lead time for changes, change failure rate, and time to restore service.
