# Cómo compartir el proyecto sin GitHub

> **Guía para pasar el proyecto **SQUAD-AGENTES-IA** a otra persona que no tiene acceso a GitHub, para que lo abra en Kiro.

---

## Qué incluir (archivos a pasar)

Incluye **todo el proyecto** excepto lo que se indica en la sección "Qué excluir".

### Estructura mínima necesaria

```
SQUAD-AGENTES-IA/
├── .kiro/                # Steering, hooks, skills y specs (obligatorio)
├── docs/                 # Documentación completa
├── rules/                # Reglas técnicas (Playwright, Datadog, etc.)
├── scripts/              # Scripts de auditoría y config
├── tests/                # Tests E2E y unitarios
├── tools/                # Scripts de reportes y deploy
├── package.json
├── playwright.config.js
├── vitest.config.js
├── .eslintrc.cjs
├── .prettierrc
├── .prettierignore
├── .gitignore
└── README.md
```

---

## Qué excluir (no pasar)

| Carpeta/archivo | Motivo |
|-----------------|--------|
| `node_modules/` | Se reinstala con `npm install` |
| `.git/` | Historial de Git (opcional; si no usan GitHub, no lo necesitan) |
| `Workspace/` | Artefactos generados, config específica, repos clonados. La otra persona creará su propia config en el onboarding |
| `test-results/` | Resultados de Playwright (se regeneran) |
| `playwright-report/` | Reportes de Playwright (se regeneran) |
| `reporte-visual/` | Artefactos visuales (se regeneran) |
| `.env`, `.env.local` | Variables de entorno (sensibles, cada uno las configura) |

---

## Formas de compartir

### Opción 1: ZIP (recomendada)

Desde la raíz del proyecto, crea un ZIP excluyendo lo anterior:

```bash
# En macOS/Linux (desde la raíz del proyecto)
zip -r squad-agentes-ia.zip . \
  -x "node_modules/*" \
  -x ".git/*" \
  -x "Workspace/*" \
  -x "test-results/*" \
  -x "playwright-report/*" \
  -x "reporte-visual/*" \
  -x ".env*"
```

### Opción 2: Carpeta comprimida manual

1. Copia todo el proyecto a una carpeta nueva.
2. Elimina: `node_modules`, `.git`, `Workspace`, `test-results`, `playwright-report`, `reporte-visual`, `.env*`.
3. Comprime la carpeta (ZIP, 7z, etc.).

### Opción 3: USB, Drive, Dropbox, etc.

Usa el ZIP o la carpeta limpia y compártela por el medio que prefieras.

---

## Pasos para quien recibe el proyecto

1. **Descomprimir** el ZIP en la carpeta deseada.
2. **Abrir en Cursor**: `File → Open Folder` y seleccionar la carpeta `SQUAD-AGENTES-IA`.
3. **Instalar dependencias**:
   ```bash
   npm install
   npx playwright install
   ```
4. **Configurar plataformas**: Al abrir el proyecto, el agente seguirá el flujo de primera interacción y creará `Workspace/config/platforms.json` a partir de `docs/templates/platforms.example.json`. La persona debe indicar sus URLs, Jira, Datadog, etc.

---

## Nota sobre Workspace/config/platforms.json

Si **tú ya tienes** `Workspace/config/platforms.json` configurado y quieres que la otra persona empiece con esa misma configuración:

- **Incluye** `Workspace/config/platforms.json` en el paquete (aunque `Workspace/` suele excluirse).
- O pásale una copia del archivo por separado y dile que lo coloque en `Workspace/config/platforms.json` antes de ejecutar tests.

Si no lo incluyes, el agente creará uno nuevo en la primera interacción siguiendo `docs/onboarding/01-flujo-primera-interaccion.md`.

---

## Referencias

- [Flujo de primera interacción](./01-flujo-primera-interaccion.md)
- [Resumen del proyecto](../resumen-proyecto.md)
- [Estructura del proyecto](../ESTRUCTURA.md)
