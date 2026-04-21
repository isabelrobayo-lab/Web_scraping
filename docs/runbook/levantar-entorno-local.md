# Runbook: Levantar entorno local

## Requisitos previos

- Node.js 18+
- `npm install` en la raíz
- `npx playwright install` (primera vez)
- **Configuración**: `{WORKSPACE_ROOT}/config/platforms.json` (ver [onboarding](../onboarding/01-flujo-primera-interaccion.md) y [4-workspace](../architecture/4-workspace.md))

## Pasos

### 1. Instalar dependencias

```bash
# Raíz (Playwright, ESLint, Prettier, Vitest)
npm install

# Playwright browsers (primera vez)
npx playwright install
```

### 2. Ejecutar tests E2E

```bash
npm test
```

Los tests usan `baseURL` y `smokePaths` desde el `config/platforms.json` del workspace activo (o `BASE_URL` si no hay config). Ver `playwright.config.js`, `scripts/get-platform-config.js` y `scripts/workspace-root.js`.

### 3. Tests unitarios

```bash
npm run test:unit
```

Ejecuta Vitest sobre `tests/unit/**/*.test.js` (audit-data, get-platform-config, analyze-cycle-time, etc.).

### 4. Auditoría de consola

```bash
npm run audit
```

Genera reporte en `Workspace/audit/console-audit-report.json` y capturas en `Workspace/audit/screenshots/`. URL y zonas desde config.

### 5. Miniverse (opcional)

```bash
cd miniverse && npm install && npm run dev
```

En otra terminal, desde la raíz del repo:

```bash
npx playwright test --project=miniverse
```

La UI suele estar en `http://localhost:5173` y la API en `http://localhost:4321`. Ver `miniverse/README.md` y `docs/architecture/1-stack.md`.

### 6. Tests E2E de la página de reportes (opcional)

`tests/reportes.spec.js` comprueba `reportes.html` en la URL publicada. Por defecto apunta a GitHub Pages del repo de referencia; para otro entorno:

```bash
REPORTES_BASE_URL=https://tu-usuario.github.io/tu-repo/reportes.html npx playwright test tests/reportes.spec.js
```

## Troubleshooting

| Problema | Solución |
|----------|----------|
| Playwright no encuentra navegadores | `npx playwright install` |
| Tests fallan por timeout | Verificar conectividad a la URL configurada en platforms.json |
| "baseURL" o "smokePaths" undefined | Crear `{WORKSPACE_ROOT}/config/platforms.json` desde `docs/templates/platforms.example.json` |
