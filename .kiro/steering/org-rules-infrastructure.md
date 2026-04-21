---
inclusion: always
---

# Reglas de Infraestructura — Organización

Reglas estandarizadas de infraestructura para desarrollo asistido por IA. Definen cómo la infraestructura cloud y on-premise debe ser aprovisionada, configurada y gestionada.

---

## 1. Infrastructure as Code (IaC)

- **Toda infraestructura debe definirse como código** usando herramientas aprobadas (Terraform, Bicep, ARM Templates, Pulumi, CloudFormation).
- Nunca aprovisionar o modificar infraestructura manualmente por consola en producción.
- IaC en **repositorios versionados** con los mismos estándares de branching y review que el código de aplicación.
- Usar **módulos y componentes reutilizables** para evitar duplicación.
- Validar cambios con **plan/preview** antes de aplicar (`terraform plan`, `az deployment what-if`).

## 2. Naming Conventions & Tagging

- Seguir la convención de naming organizacional: `{company}-{environment}-{region}-{service}-{resource-type}`.
- Tags obligatorios en cada recurso: `environment`, `owner`, `cost-center`, `project`, `managed-by`.
- Enforcar compliance de naming y tagging vía **Azure Policy**, AWS Config Rules o equivalente.

## 3. Network Architecture

- Diseñar redes con topología **hub-and-spoke** o **mesh** según estándares organizacionales.
- Aislar workloads con **VNets/VPCs** y **subnets** segmentadas por tier (web, app, data).
- **NSGs** con reglas **deny-by-default**. Solo permitir tráfico requerido.
- **Private endpoints** para servicios PaaS (databases, storage, key vaults).
- **WAF** frente a todas las aplicaciones web públicas.

## 4. Compute & Scaling

- Right-size basado en **performance baselines** y load testing.
- **Auto-scaling** con umbrales definidos (CPU, memory, custom metrics).
- Preferir **managed services** (PaaS, serverless) sobre VMs self-managed cuando sea posible.
- Programar **apagado de ambientes no-productivos** fuera de horario laboral.

## 5. Storage & Data Services

- **Geo-redundant storage** para datos de producción.
- **Lifecycle policies** para transición automática a storage tiers más fríos.
- Restringir acceso a storage con **private endpoints** y network rules. Deshabilitar acceso público por defecto.
- **Soft delete** y **versioning** en storage accounts y blob containers críticos.
- **Backup policies** con RPO/RTO documentados.

## 6. Identity & Access for Infrastructure

- Acceso vía **RBAC** usando grupos, no asignaciones individuales.
- **Managed identities** para autenticación service-to-service. Evitar almacenar credenciales.
- **Just-In-Time (JIT)** access para privilegios elevados en producción.
- Auditar todo acceso con **Activity Logs**, CloudTrail o equivalente.

## 7. Monitoring & Observability

- **Monitoreo centralizado** (Azure Monitor, CloudWatch, Datadog) para todos los recursos.
- **Alertas** para health, degradación de performance y disponibilidad (CPU > 85%, memory > 90%, disk > 80%).
- **Diagnostic logging** en recursos críticos (load balancers, firewalls, databases, API gateways).
- **Log retention** que cumpla compliance (mínimo 90 días hot, 1 año archive).

## 8. Disaster Recovery & Business Continuity

- Definir **RPO** y **RTO** para cada workload de producción.
- **Cross-region replication** para databases, storage y compute críticos.
- **DR runbooks** con procedimientos paso a paso de failover y failback.
- **DR drills** al menos trimestrales con resultados documentados.
- **Availability zones** para alta disponibilidad de servicios críticos.

## 9. Cost Management

- **Budgets y cost alerts** a nivel de subscription, resource group o proyecto.
- Revisión mensual de costos e identificación de optimizaciones.
- **Cost allocation tags** consistentes para atribuir gasto a equipos y proyectos.
- Decomisionar **recursos no usados** (discos huérfanos, IPs no asociadas, load balancers idle).
- **Reserved capacity** o **savings plans** para workloads predecibles.

## 10. Compliance & Governance

- Enforcar políticas con **Azure Policy**, AWS SCPs o GCP Organization Policies.
- Mantener **catálogo de servicios aprobados** — no aprovisionar tipos no aprobados.
- **Resource locks** en recursos críticos de producción.
- **Compliance audits** periódicos contra CIS benchmarks y estándares regulatorios.
- Documentar decisiones de infraestructura en **ADRs**.
