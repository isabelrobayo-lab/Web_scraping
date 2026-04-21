# Sistema de Diseño

> Guía visual para el frontend del proyecto. Actualmente el proyecto es principalmente API y tests; este documento sirve como referencia para reportes HTML y futuras interfaces.

## Tipografías

| Uso | Familia | Peso | Notas |
|-----|---------|------|-------|
| Cuerpo | DM Sans | 300–700 | Principal para texto |
| Código / Mono | JetBrains Mono | 400, 500 | Metadatos, IDs, código |

```css
font-family: 'DM Sans', -apple-system, sans-serif;
font-family: 'JetBrains Mono', monospace;
```

## Paleta de colores

| Variable | Hex | Uso |
|----------|-----|-----|
| `--bg-primary` | #0f1419 | Fondo principal |
| `--bg-secondary` | #1a2332 | Fondo secundario |
| `--bg-card` | #1e2a3a | Tarjetas, bloques |
| `--accent` | #00d4aa | Acento, éxito |
| `--accent-muted` | #00a884 | Acento suave |
| `--text-primary` | #e8edf4 | Texto principal |
| `--text-secondary` | #8b9cb3 | Texto secundario |
| `--border` | #2d3d52 | Bordes |
| `--success` | #00d4aa | Estados éxito |
| `--warning` | #f0b429 | Estados advertencia |
| `--critical` | #e85d75 | Estados error/crítico |

## Componentes

### Tarjetas

- Fondo: `var(--bg-card)`
- Borde: `1px solid var(--border)`
- Border-radius: `6px`
- Padding: `1rem`–`1.5rem`

### Barras de navegación

- Fondo: `var(--bg-secondary)` o `var(--bg-card)`
- Borde inferior: `1px solid var(--border)`
- Altura mínima: `48px`–`64px`

### Badges / Metadatos

- Fondo: `var(--bg-card)`
- Color: `var(--accent)`
- Font: JetBrains Mono
- Padding: `0.35rem 0.85rem`
- Border-radius: `6px`

### Estados (success, warning, critical)

- Usar variables `--success`, `--warning`, `--critical` para iconos y texto
- Mantener contraste suficiente con el fondo

## Referencias

- `reporte-ejecutivo-valor-proyecto.html` — implementa este sistema de diseño
- `miniverse/` — dashboard de agentes IA ([Miniverse upstream](https://github.com/ianscott313/miniverse)); estilo pixel art del renderer `@miniverse/core`; alinear tonos con este documento solo si se personaliza la UI
