# 🛠️ Stack Tecnológico de Autogestión (v3.3)

Este documento define la configuración técnica exacta para las iniciativas de autogestión. Su contenido es la base para el aprovisionamiento automático de ambientes.

---

## 🏗️ 1. Definiciones por Perfil (Aprovisionamiento Automático)

Cuando un usuario registra una iniciativa, el sistema desplegará un contenedor basado en estos perfiles:

### 🅰️ Perfil: Standard (Usuario Básico/Custom)

*Optimizado para facilidad de uso y estándares corporativos.*

| Capa | Tecnología Seleccionada | Especificación de Versión |
| :--- | :--- | :--- |
| **Frontend** | **Angular** | Versión 17+ (LTS) |
| **Backend** | **Node.js** | Versión 20.x (LTS) |
| **Framework Backend** | **Express.js** | Versión 4.x |
| **Build Tool** | **npm** | Versión 10.x |
| **Persistencia** | **PostgreSQL** | Versión 15.4+ |

## 📚 2. Inventario General de Tecnologías Habilitadas

### Frontend - Frameworks y Librerías

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **Angular** | Angular CLI | 17+ (LTS) | Apps Web corporativas con arquitectura modular. |
| **React** | Vite / React Query | 18.x | Interfaces dinámicas y de alto rendimiento. |
| **TypeScript** | - | 5.x | Tipado estricto para calidad de código en JS/Node. |
| **Vite** | - | 5.x | Build tool rápido y moderno para React/Vue. |
| **React Router** | react-router-dom | 6.x | Navegación y routing en aplicaciones React. |
| **React Query** | @tanstack/react-query | 5.x | State management para datos del servidor y caché. |
| **React Hook Form** | react-hook-form | 7.x | Manejo eficiente de formularios con validación. |
| **Zod** | zod | 3.x | Validación de esquemas TypeScript-first. |

### Frontend - UI Libraries y Componentes

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **Shadcn UI** | Radix UI Primitives | Latest | Componentes UI accesibles y personalizables. |
| **Radix UI** | @radix-ui/* | Latest | Primitivos UI sin estilos, accesibles. |
| **Tailwind CSS** | - | 3.x | Estilizado rápido basado en utilidades. |
| **Lucide React** | lucide-react | Latest | Librería de iconos moderna y ligera. |
| **Recharts** | recharts | 2.x | Librería de gráficos para React. |
| **jsPDF** | jspdf | 3.x | Generación de documentos PDF desde JavaScript. |
| **html2canvas** | html2canvas | 1.x | Conversión de elementos HTML a canvas/imagen. |

### Frontend - Utilidades y Helpers

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **Axios** | axios | 1.x | Cliente HTTP para peticiones API. |
| **date-fns** | date-fns | 3.x | Utilidades modernas para manejo de fechas. |
| **clsx** | clsx | 2.x | Utilidad para construir nombres de clases condicionales. |
| **tailwind-merge** | tailwind-merge | 2.x | Merge inteligente de clases Tailwind. |
| **class-variance-authority** | cva | 0.x | Creación de variantes de componentes. |
| **Sonner** | sonner | 1.x | Sistema de notificaciones toast moderno. |

### Frontend - Testing

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **Vitest** | vitest | 3.x | Framework de testing rápido para Vite. |
| **React Testing Library** | @testing-library/react | 16.x | Utilidades para testing de componentes React. |
| **Jest DOM** | @testing-library/jest-dom | 6.x | Matchers personalizados para DOM. |

### Backend - Node.js

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **Node.js** | - | 20.x (LTS) | Runtime de JavaScript para backend. |
| **Express.js** | express | 4.x | Framework web minimalista y flexible. |
| **Fastify** | fastify | 4.x | Framework de Node.js enfocado en rendimiento extremo. |
| **Nodemon** | nodemon | 3.x | Herramienta para desarrollo con auto-reload. |

### Backend - Base de Datos Relacionales

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **PostgreSQL** | - | 15.4+ | Motor de base de datos relacional estándar (PRINCIPAL). |
| **pg** | node-postgres | 8.x | Cliente PostgreSQL para Node.js. |
| **node-pg-migrate** | node-pg-migrate | Latest | Herramienta de migraciones para PostgreSQL. |
| **Oracle Database** | - | 19c+ / 21c+ | Base de datos empresarial para sistemas legacy y críticos. |
| **MySQL** | - | 8.0+ | Base de datos relacional open-source alternativa. |

### Backend - Bases de Datos NoSQL

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **MongoDB** | - | 7.0+ | Almacenamiento NoSQL para datos no estructurados. |
| **Elasticsearch** | - | 8.x+ | Motor de búsqueda y análisis distribuido. |

### Backend - Bases de Datos Vectoriales (IA/ML)

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **Pinecone** | - | Latest | Base de datos vectorial para embeddings (IA). |
| **pgvector** | Extension PostgreSQL | Latest | Extensión de PostgreSQL para almacenamiento vectorial. |

### Backend - Caché y Sesiones

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **ElastiCache** | - | 8.x | Base de datos en memoria para caché y sesiones. |
| **AWS ElastiCache** | Redis/Memcached | Latest | Servicio gestionado de caché en AWS. |

### Backend - Autenticación y Seguridad

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **JWT** | jsonwebtoken | 9.x | Tokens JSON Web para autenticación. |
| **Passport.js** | passport | 0.x | Middleware de autenticación flexible. |
| **Passport JWT** | passport-jwt | 4.x | Estrategia JWT para Passport. |
| **Passport Google OAuth** | passport-google-oauth20 | 2.x | Estrategia OAuth 2.0 de Google. |
| **bcrypt** | bcrypt | 6.x | Librería para hashing de contraseñas. |
| **Helmet** | helmet | 8.x | Middleware de seguridad HTTP headers. |
| **CORS** | cors | 2.x | Middleware para Cross-Origin Resource Sharing. |

### Backend - Utilidades y Servicios

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **Axios** | axios | 1.x | Cliente HTTP para llamadas a APIs externas. |
| **AWS SDK** | aws-sdk | 2.x | SDK oficial de AWS para Node.js. |
| **Multer** | multer | 2.x | Middleware para manejo de multipart/form-data. |
| **UUID** | uuid | 11.x | Generación de identificadores únicos universales. |
| **dotenv** | dotenv | 17.x | Carga variables de entorno desde archivo .env. |
| **Express Session** | express-session | 1.x | Middleware de manejo de sesiones. |
| **Form Data** | form-data | 4.x | Creación y envío de form-data. |

### Backend - Testing

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **Jest** | jest | 30.x | Framework de testing para JavaScript. |
| **Supertest** | supertest | 7.x | Librería para testing de APIs HTTP. |

### Backend - Java

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **Java** | JDK | 21 (LTS) | Lenguaje de programación empresarial. |
| **Spring Boot** | spring-boot | 3.x | Framework para aplicaciones Java empresariales. |
| **Maven** | maven | 3.9+ | Herramienta de gestión y construcción. |
| **Gradle** | gradle | 8.x | Build tool alternativo a Maven. |
| **Spring Security** | spring-security | 6.x | Framework de seguridad para aplicaciones Spring. |
| **JPA / Hibernate** | hibernate | Latest | ORM para Java. |
| **JUnit** | junit | 5.x | Framework de testing para Java. |

### Backend - Python

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **Python** | - | 3.12+ | Lenguaje de programación de alto nivel. |
| **FastAPI** | fastapi | 0.115+ | Framework moderno y rápido para APIs. |
| **Django** | django | 5.x | Framework completo para desarrollo web. |
| **Poetry** | poetry | 1.8+ | Gestor de dependencias y entornos virtuales. |
| **SQLAlchemy** | sqlalchemy | 2.0+ | ORM para Python (usado con FastAPI). |
| **Django ORM** | django | 5.x | ORM incluido en Django. |
| **psycopg2** | psycopg2 | 2.9+ | Adaptador PostgreSQL para Python. |
| **pytest** | pytest | 8.0+ | Framework de testing para Python. |

### Automatización y Orquestación

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **n8n** | Community Edition | Latest | Orquestación de flujos y automatización. |
| **Google Apps Script** | - | Latest | Automatización en Google Workspace. |

### Infraestructura y Cloud

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **Docker** | docker | 24.x+ | Contenedorización de aplicaciones. |
| **Docker Compose** | docker-compose | Latest | Orquestación multi-contenedor. |
| **AWS ECS Fargate** | - | Latest | Contenedores sin servidor en AWS. |
| **AWS S3** | - | Latest | Almacenamiento de objetos en la nube. |
| **AWS CloudFront** | - | Latest | CDN y distribución de contenido. |
| **AWS RDS PostgreSQL** | - | 15.4+ | Base de datos PostgreSQL gestionada. |
| **AWS ALB** | - | Latest | Application Load Balancer. |
| **AWS Parameter Store** | - | Latest | Almacenamiento de configuración y secretos. |
| **AWS CloudWatch** | - | Latest | Monitoreo y logging centralizado. |

### CI/CD y Versionamiento

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **Git** | git | 2.40+ | Sistema de control de versiones distribuido. |
| **GitHub Actions** | - | Latest | CI/CD integrado con GitHub. |

### Herramientas de Desarrollo

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **ESLint** | eslint | 9.x | Linter para JavaScript/TypeScript. |
| **Prettier** | prettier | Latest | Formateador de código automático. |
| **PostCSS** | postcss | 8.x | Herramienta para transformar CSS. |
| **Autoprefixer** | autoprefixer | 10.x | Plugin PostCSS para agregar prefijos CSS. |

### Repositorios y Gestión de Dependencias

| Tecnología | Framework / Herramienta | Versión | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **Jfrog** | Artifactory | Latest | Repositorio institucional de librerías. |
| **npm** | npm | 10.x+ | Gestor de paquetes para Node.js. |
| **npm Registry (Jfrog)** | - | - | Configuración de .npmrc para Jfrog. |

---

## 🔌 3. Anexo de Conectividad y Automatización

| Tecnología | Componente / Regla | Versión / Detalle | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **n8n** | Webhook como API | Exclusivo | Único punto de entrada permitido para el Frontend. |
| **n8n** | Prohibición de Nodos de BD | Estricto | Prohibido el uso de nodos de conexión directa (Postgres/Mongo). Todo acceso es vía API interna. |
| **n8n** | Nodos Obligatorios | Gobierno | 1. Versionamiento (Versión/Autor), 2. Credenciales (Gestión de secretos). |
| **Google Apps Script** | Sincronización | GitHub Assistant | Sincronización obligatoria del código .gs con el repositorio Git oficial. |
| **Google Apps Script** | Persistencia | UrlFetchApp | Prohibido usar Sheets como DB; consumo de servicios vía APIs. |

---

## 🛡️ 4. Estándar Global de Identidad y Acceso (IAM)

| Tecnología | Componente / Regla | Estándar | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **IAM** | Protocolo | OAuth 2.0 / OIDC | Uso mandatorio para autenticación y autorización. |
| **IAM** | Tokens | JWT | Transporte de identidad exclusivo mediante JSON Web Tokens. |
| **IAM** | Almacenamiento | httpOnly cookies | Gestión de Refresh Tokens para evitar ataques XSS. |
| **IAM** | Validación | Firma y Scopes | El Backend debe verificar firma y permisos antes de procesar. |

---

## 🚀 5. Estándares de Infraestructura y Despliegue

| Categoría | Regla / Componente | Detalle | Propósito / Uso |
| :--- | :--- | :--- | :--- |
| **Infraestructura** | Gestión de Librerías | Jfrog | Descarga exclusiva desde el repositorio institucional. Para Python es obligatorio requirements.txt o pyproject.toml. |
| **Infraestructura** | Direccionamiento | DNS | Prohibido el uso de IPs fijas; comunicación solo mediante DNS. |
| **Infraestructura** | Observabilidad | Logs Centralizados | Envío obligatorio de logs a servicios centrales (CloudWatch/Log Explorer). |
| **Infraestructura** | Resiliencia | Estándares Core | Implementación obligatoria de Retries y Circuit Breakers. |
