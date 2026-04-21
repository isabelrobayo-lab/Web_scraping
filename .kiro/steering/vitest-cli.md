---
inclusion: fileMatch
fileMatchPattern: ['package.json', 'vitest.config.*', '**/*.test.{js,ts,jsx,tsx}']
---

# Vitest CLI

Cuando configures o uses Vitest en un proyecto, aplica estos patrones:

## Scripts npm en package.json

Añade (o mantén) estos scripts para tests unitarios:

```json
"test:unit": "vitest run",
"test:unit:watch": "vitest watch",
"test:unit:ui": "vitest --ui",
"test:unit:coverage": "vitest run --coverage",
"test:unit:list": "vitest list",
"test:unit:related": "vitest related --run"
```

## Config coverage (vitest.config)

```js
coverage: {
  provider: "v8",
  reporter: ["text", "html", "json"],
  reportsDirectory: "./coverage",
}
```

Instala `@vitest/coverage-v8` como devDependency. Añade `coverage/` al `.gitignore`.

## CLI directa

- Filtrar: `npx vitest run <nombre>` o `-t "regex"`
- Archivo:línea: `npx vitest run ruta/test.js:10`
- Docs: https://vitest.dev/guide/cli.html
