# Vitest CLI

Referencia de comandos Vitest CLI usados en el proyecto. Documentación oficial: [vitest.dev/guide/cli](https://vitest.dev/guide/cli.html).

## Scripts npm disponibles

| Script | Comando | Descripción |
|--------|---------|-------------|
| `npm run test:unit` | `vitest run` | Ejecuta tests unitarios una vez (CI, pre-commit) |
| `npm run test:unit:watch` | `vitest watch` | Modo watch: re-ejecuta al cambiar archivos (desarrollo) |
| `npm run test:unit:ui` | `vitest --ui` | Interfaz visual interactiva |
| `npm run test:unit:coverage` | `vitest run --coverage` | Genera reporte de cobertura → `./coverage/` |
| `npm run test:unit:list` | `vitest list` | Lista todos los tests que coinciden con el filtro |
| `npm run test:unit:related` | `vitest related --run` | Ejecuta solo tests que cubren archivos modificados (para lint-staged/CI) |

## Uso directo de la CLI

### Filtrar por archivo o nombre

```bash
# Solo archivos que contengan "audit" en la ruta
npx vitest run audit

# Por nombre de test (regex)
npx vitest run -t "debe retornar"
```

### Ejecutar un archivo y línea específica (Vitest 3+)

```bash
npx vitest run tests/unit/audit.test.js:10
```

### Coverage con opciones

```bash
# Reportes adicionales (JUnit, TAP, etc.)
npx vitest run --coverage --reporter=junit --outputFile.junit=./junit.xml
```

### Modo related (tests ligados a cambios)

Útil para `lint-staged` o CI: ejecuta solo tests que importan los archivos modificados.

```bash
# Con archivos específicos (relativos a la raíz)
npx vitest related --run tests/unit/audit.test.js scripts/audit-data.js
```

## Configuración

- **Archivo:** `vitest.config.js`
- **Tests:** `tests/unit/**/*.test.js`
- **Coverage:** provider `v8`, reportes en `./coverage/`
- **Environment:** `node`
- **Globals:** `true` (describe, it, expect sin import)

## Integración con lint-staged (opcional)

```js
// .lintstagedrc.js
export default {
  "*.{js,cjs}": ["eslint", "vitest related --run"],
}
```
