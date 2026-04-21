# Infrastructure Rules

> Standardized infrastructure rules for AI-assisted development. These rules define how cloud and on-premise infrastructure must be provisioned, configured, and managed across all projects.

---

## 1. Infrastructure as Code (IaC)

- **All infrastructure must be defined as code** using approved tools (Terraform, Bicep, ARM Templates, Pulumi, CloudFormation).
- Never provision or modify infrastructure manually through cloud consoles in production environments.
- Store IaC definitions in **version-controlled repositories** with the same branching and review standards as application code.
- Use **modules and reusable components** to avoid duplication and enforce consistency across environments.
- Validate IaC changes with **plan/preview** commands before applying (`terraform plan`, `az deployment what-if`).

## 2. Naming Conventions & Tagging

- Follow the organization's **resource naming convention** consistently: `{company}-{environment}-{region}-{service}-{resource-type}`.
- Apply mandatory **tags** to every resource: `environment`, `owner`, `cost-center`, `project`, `managed-by`.
- Use consistent **abbreviations** for resource types (e.g., `rg` for resource group, `vnet` for virtual network, `aks` for Kubernetes service).
- Enforce naming and tagging compliance via **Azure Policy**, AWS Config Rules, or equivalent governance tools.
- Document all naming conventions in a central, accessible location and keep them updated.

## 3. Network Architecture

- Design networks using a **hub-and-spoke** or **mesh topology** according to organizational standards.
- Isolate workloads using **virtual networks (VNets/VPCs)** and **subnets** with proper segmentation by tier (web, app, data).
- Use **Network Security Groups (NSGs)** or security groups with **deny-by-default** rules. Allow only required traffic.
- Deploy **private endpoints** for PaaS services (databases, storage, key vaults) to avoid public internet exposure.
- Implement **DNS resolution** through centralized private DNS zones to ensure consistent name resolution across environments.
- Use **Web Application Firewalls (WAF)** in front of all public-facing web applications.

## 4. Compute & Scaling

- Right-size compute resources based on **performance baselines** and load testing data. Avoid over-provisioning.
- Configure **auto-scaling** policies with defined minimum, maximum, and target thresholds based on CPU, memory, or custom metrics.
- Use **managed services** (PaaS, serverless) over self-managed VMs whenever the workload allows.
- Define and enforce **approved VM SKUs and instance types** per environment to control costs and maintain consistency.
- Schedule **non-production environments** to shut down outside business hours to reduce costs.

## 5. Storage & Data Services

- Enable **geo-redundant storage** (GRS, cross-region replication) for production data to meet disaster recovery requirements.
- Configure **lifecycle policies** to automatically transition data to cooler storage tiers or delete expired data.
- Restrict storage account access using **private endpoints**, network rules, and service-level firewalls. Disable public blob access by default.
- Enable **soft delete** and **versioning** on critical storage accounts and blob containers.
- Define and enforce **backup policies** for databases, file shares, and critical storage with documented RPO/RTO targets.

## 6. Identity & Access for Infrastructure

- Manage infrastructure access through **role-based access control (RBAC)** using groups, not individual user assignments.
- Use **managed identities** (system-assigned or user-assigned) for service-to-service authentication. Avoid storing credentials.
- Apply **Just-In-Time (JIT)** access for elevated privileges on production infrastructure.
- Audit all infrastructure access using **Azure Activity Logs**, AWS CloudTrail, or equivalent logging services.
- Restrict **subscription/account owner** roles to a minimal set of trusted administrators.

## 7. Monitoring & Observability

- Deploy **centralized monitoring** using Azure Monitor, CloudWatch, Datadog, or equivalent for all infrastructure resources.
- Define **alerts** for resource health, performance degradation, and availability (CPU > 85%, memory > 90%, disk > 80%).
- Enable **diagnostic logging** on all critical resources (load balancers, firewalls, databases, API gateways).
- Implement **dashboards** for real-time visibility into resource utilization, costs, and operational health.
- Configure **log retention policies** that meet compliance requirements (minimum 90 days hot, 1 year archive).

## 8. Disaster Recovery & Business Continuity

- Define **RPO (Recovery Point Objective)** and **RTO (Recovery Time Objective)** for every production workload.
- Implement **cross-region replication** for critical databases, storage, and compute resources.
- Document and maintain **disaster recovery runbooks** with step-by-step failover and failback procedures.
- Conduct **DR drills** at least quarterly and document results, gaps, and remediation actions.
- Use **availability zones** within regions for high availability of critical services.

## 9. Cost Management

- Set up **budgets and cost alerts** at the subscription, resource group, or project level.
- Review infrastructure costs **monthly** and identify optimization opportunities (reserved instances, savings plans, right-sizing).
- Use **cost allocation tags** consistently to attribute spend to specific teams, projects, and environments.
- Decommission **unused resources** (orphaned disks, unattached IPs, idle load balancers) through automated or periodic reviews.
- Prefer **reserved capacity** or **savings plans** for predictable, steady-state workloads.

## 10. Compliance & Governance

- Enforce organizational policies using **Azure Policy**, AWS Service Control Policies, or GCP Organization Policies.
- Maintain an **approved services catalog** — do not provision unapproved resource types or SKUs.
- Apply **resource locks** (CanNotDelete, ReadOnly) on critical production resources to prevent accidental deletion.
- Conduct periodic **compliance audits** against CIS benchmarks, organizational standards, and regulatory requirements.
- Document all infrastructure decisions and changes in **Architecture Decision Records (ADRs)** or equivalent documentation.
