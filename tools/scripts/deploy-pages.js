#!/usr/bin/env node
/**
 * Regenera reportes y los copia a docs/ para publicación en GitHub Pages.
 * Ejecutar antes de push cuando se quieran publicar reportes actualizados.
 *
 * Uso: npm run deploy:pages
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = path.join(__dirname, '../..');
const { getWorkspaceRoot } = require('../../scripts/workspace-root.js');
const WS = getWorkspaceRoot();
const WORKSPACE_REPORTS = path.join(WS, 'reports');
const WORKSPACE_AUDIT = path.join(WS, 'audit');
const WORKSPACE_CONFIG = path.join(WS, 'config', 'platforms.json');
const DOCS = path.join(ROOT, 'docs');
const DOCS_DATA = path.join(DOCS, 'data');

function main() {
  console.log('Regenerando reportes...');
  execSync('npm run report:cycle', {
    cwd: ROOT,
    stdio: 'inherit',
  });

  if (!fs.existsSync(WORKSPACE_REPORTS)) {
    console.error(`No se encontró reports/ en el workspace (${WORKSPACE_REPORTS}). Ejecuta npm run report:cycle primero.`);
    process.exit(1);
  }

  const files = fs.readdirSync(WORKSPACE_REPORTS).filter((f) => f.endsWith('.html'));
  if (files.length === 0) {
    console.log(`No hay archivos HTML en reports/ del workspace (${WORKSPACE_REPORTS}).`);
  } else {
    console.log(`Copiando ${files.length} reporte(s) a docs/...`);
    for (const file of files) {
      const src = path.join(WORKSPACE_REPORTS, file);
      const dest = path.join(DOCS, file);
      fs.copyFileSync(src, dest);
      console.log(`  ${file} -> docs/${file}`);
    }
  }

  // Copiar platforms.json para filtros en reportes (GitHub Pages)
  if (fs.existsSync(WORKSPACE_CONFIG)) {
    if (!fs.existsSync(DOCS_DATA)) fs.mkdirSync(DOCS_DATA, { recursive: true });
    const dest = path.join(DOCS_DATA, 'platforms.json');
    fs.copyFileSync(WORKSPACE_CONFIG, dest);
    console.log('  platforms.json -> docs/data/platforms.json');
  } else {
    console.log(`  (${WORKSPACE_CONFIG} no existe; filtros por plataforma deshabilitados)`);
  }

  // Copiar screenshots de auditoría si existen (para auditoria-errores-consola.html)
  const auditScreenshots = path.join(WORKSPACE_AUDIT, 'screenshots');
  const docsScreenshots = path.join(DOCS, 'screenshots-auditoria');
  if (fs.existsSync(auditScreenshots)) {
    if (!fs.existsSync(docsScreenshots)) fs.mkdirSync(docsScreenshots, { recursive: true });
    const screens = fs.readdirSync(auditScreenshots).filter((f) => /\.(png|jpg|jpeg|webp)$/i.test(f));
    for (const f of screens) {
      fs.copyFileSync(path.join(auditScreenshots, f), path.join(docsScreenshots, f));
    }
    console.log(`  screenshots-auditoria/ (${screens.length} archivos)`);
  }

  console.log('Listo. Haz commit y push para publicar en GitHub Pages.');
}

main();
