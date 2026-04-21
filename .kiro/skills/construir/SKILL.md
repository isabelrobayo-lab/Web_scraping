---
name: construir-deploy
description: "Sube el proyecto a producción siguiendo los pasos ordenados: 1) Ejecutar build, 2) Revisar errores, 3) Hacer commit, 4) Ejecutar push."
---

# Skill de Construcción y Deploy

## Objetivo

Preparar y subir el proyecto a producción (o a la rama remota) de forma ordenada.

## Instrucciones

### Paso 1: Ejecutar build

```bash
npm run build
```

Para proyectos sin script de build en `package.json`, omitir este paso e indicarlo al usuario.

- Frontend: `npm run build` o `npm run build:prod`
- Backend TypeScript: `npm run build` o `tsc`

### Paso 2: Revisar que no haya errores

- La salida del build no debe tener errores ni warnings críticos.
- Opcional: `npm test` para validar tests.
- Opcional: `npm run lint` para verificar estilo.

Si hay errores, **detenerse** y corregir antes de continuar.

### Paso 3: Hacer commit

```bash
git add .
git status
git commit -m "mensaje descriptivo del cambio"
```

Convenciones de mensaje: `feat: ...`, `fix: ...`, `chore: ...`, `docs: ...`.

### Paso 4: Ejecutar push

```bash
git push origin <rama>
```

Ejemplo: `git push origin main` o `git push origin develop`.

## Checklist

- [ ] Build ejecutado sin errores
- [ ] Tests pasan (opcional pero recomendado)
- [ ] Commit realizado con mensaje descriptivo
- [ ] Push ejecutado a la rama correcta

## Restricciones

- No ejecutar build en cada cambio durante desarrollo. Este skill es para el flujo de deploy explícito.
- Si el usuario no quiere commit/push automático, detenerse tras el build y preguntar.
