---
inclusion: always
---

# Stack Tecnológico de la Organización (v3.3)

Stack de referencia para las iniciativas de desarrollo. Los agentes deben usar este documento como fuente de verdad para tecnologías aprobadas al diseñar soluciones.

---

## 1. Perfil Standard (Aprovisionamiento por defecto)

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Frontend | Angular | 17+ (LTS) |
| Backend | Node.js | 20.x (LTS) |
| Framework Backend | Express.js | 4.x |
| Build Tool | npm | 10.x |
| Persistencia | PostgreSQL | 15.4+ |

---

## 2. Frontend — Frameworks y Librerías

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Angular CLI | 17+ (LTS) | Apps Web corporativas con arquitectura modular |
| React + Vite | 18.x | Interfaces dinámicas y de alto rendimiento |
| TypeScript | 5.x | Tipado estricto para JS/Node |
| Vite | 5.x | Build tool rápido y moderno |
| React Router | 6.x | Navegación y routing en React |
| React Query | 5.x | State management para datos del servidor |
| React Hook Form | 7.x | Manejo eficiente de formularios |
| Zod | 3.x | Validación de esquemas TypeScript-first |

### UI Libraries

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Shadcn UI / Radix UI | Latest | Componentes UI accesibles y personalizables |
| Tailwind CSS | 3.x | Estilizado basado en utilidades |
| Lucide React | Latest | Iconos modernos |
| Recharts | 2.x | Gráficos para React |

### Testing Frontend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Vitest | 3.x | Framework de testing rápido para Vite |
| React Testing Library | 16.x | Testing de componentes React |
| Jest DOM | 6.x | Matchers personalizados para DOM |

---

## 3. Backend — Node.js

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Node.js | 20.x (LTS) | Runtime JavaScript |
| Express.js | 4.x | Framework web minimalista |
| Fastify | 4.x | Framework de alto rendimiento |

### Bases de Datos Relacionales

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| PostgreSQL | 15.4+ | BD relacional estándar (PRINCIPAL) |
| Oracle Database | 19c+ / 21c+ | Sistemas legacy y críticos |
| MySQL | 8.0+ | Alternativa open-source |

### Bases de Datos NoSQL

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| MongoDB | 7.0+ | Datos no estructurados |
| Elasticsearch | 8.x+ | Búsqueda y análisis distribuido |

### Bases de Datos Vectoriales (IA/ML)

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Pinecone | Latest | Embeddings para IA |
| pgvector | Latest | Extensión PostgreSQL para vectores |

### Caché y Sesiones

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| ElastiCache (Redis/Memcached) | Latest | Caché en memoria y sesiones |

### Autenticación y Seguridad

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| JWT (jsonwebtoken) | 9.x | Tokens de autenticación |
| Passport.js | 0.x | Middleware de autenticación |
| bcrypt | 6.x | Hashing de contraseñas |
| Helmet | 8.x | Security HTTP headers |
| CORS | 2.x | Cross-Origin Resource Sharing |

### Testing Backend (Node)

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Jest | 30.x | Framework de testing |
| Supertest | 7.x | Testing de APIs HTTP |

---

## 4. Backend — Java

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Java JDK | 21 (LTS) | Lenguaje empresarial |
| Spring Boot | 3.x | Framework empresarial |
| Maven | 3.9+ | Build tool |
| Gradle | 8.x | Build tool alternativo |
| Spring Security | 6.x | Seguridad para Spring |
| JPA / Hibernate | Latest | ORM para Java |
| JUnit | 5.x | Testing para Java |

---

## 5. Backend — Python

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.12+ | Lenguaje de alto nivel |
| FastAPI | 0.115+ | Framework moderno para APIs |
| Django | 5.x | Framework completo web |
| Poetry | 1.8+ | Gestor de dependencias |
| SQLAlchemy | 2.0+ | ORM para Python |
| psycopg2 | 2.9+ | Adaptador PostgreSQL |
| pytest | 8.0+ | Testing para Python |

---

## 6. Automatización y Orquestación

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| n8n (Community) | Latest | Orquestación de flujos |
| Google Apps Script | Latest | Automatización Google Workspace |

---

## 7. Infraestructura y Cloud

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Docker | 24.x+ | Contenedorización |
| Docker Compose | Latest | Orquestación multi-contenedor |
| AWS ECS Fargate | Latest | Contenedores sin servidor |
| AWS S3 | Latest | Almacenamiento de objetos |
| AWS CloudFront | Latest | CDN |
| AWS RDS PostgreSQL | 15.4+ | BD PostgreSQL gestionada |
| AWS ALB | Latest | Application Load Balancer |
| AWS Parameter Store | Latest | Configuración y secretos |
| AWS CloudWatch | Latest | Monitoreo y logging |

---

## 8. CI/CD y Herramientas de Desarrollo

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Git | 2.40+ | Control de versiones |
| GitHub Actions | Latest | CI/CD |
| ESLint | 9.x | Linter JS/TS |
| Prettier | Latest | Formateador de código |
| JFrog Artifactory | Latest | Repositorio institucional |

---

## 9. Estándar Global de IAM

| Componente | Estándar | Propósito |
|-----------|----------|-----------|
| Protocolo | OAuth 2.0 / OIDC | Autenticación y autorización |
| Tokens | JWT | Transporte de identidad |
| Almacenamiento | httpOnly cookies | Refresh Tokens (prevenir XSS) |
| Validación | Firma y Scopes | Backend verifica antes de procesar |

---

## 10. Reglas de Conectividad

- **n8n:** Webhook como único punto de entrada para Frontend. Prohibido nodos de conexión directa a BD.
- **Google Apps Script:** Sincronización obligatoria con repositorio Git. Prohibido usar Sheets como BD.
- **Infraestructura:** Librerías solo desde repositorio institucional (JFrog). Comunicación solo vía DNS. Logs centralizados. Retries y Circuit Breakers obligatorios.
