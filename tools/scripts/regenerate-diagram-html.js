#!/usr/bin/env node
/**
 * Regenera los archivos .html de docs/diagrams/ desde los .mmd
 * Usa formato sin comprimir para compatibilidad con diagrams.net
 * Uso: node tools/scripts/regenerate-diagram-html.js
 */

const fs = require('fs');
const path = require('path');

const DIAGRAMS_DIR = path.join(__dirname, '../../docs/diagrams');
const BASE_URL = 'https://app.diagrams.net/?grid=0&pv=0&border=10&edit=_blank#create=';
const DIAGRAMS_NET_URL = 'https://app.diagrams.net/';

function createDiagramUrl(mermaidText) {
  const payload = JSON.stringify({ type: 'mermaid', data: mermaidText });
  return BASE_URL + encodeURIComponent(payload);
}

function generateHtml(mmdPath, title, mmdFile) {
  const mermaid = fs.readFileSync(mmdPath, 'utf8');
  const url = createDiagramUrl(mermaid);
  const mmdPathForUser = `docs/diagrams/${mmdFile}`;
  return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0;url=${url}">
  <title>${title} - Draw.io</title>
  <script>window.location.replace("${url.replace(/"/g, '\\"')}");</script>
</head>
<body>
  <p>Redirigiendo a <a href="${url}">Draw.io - ${title}</a>…</p>
  <p><strong>Si la redirección falla:</strong> Abre <a href="${DIAGRAMS_NET_URL}">diagrams.net</a>, crea un diagrama nuevo y pega el contenido del archivo <code>${mmdPathForUser}</code> en <em>Arrange → Insert → Advanced → Mermaid</em>.</p>
</body>
</html>
`;
}

const PAIRS = [
  ['equipo-agentes.mmd', 'Equipo de Agentes'],
  ['flujo-estructura.mmd', 'Flujo estructura'],
  ['esquema-proyecto-completo.mmd', 'Esquema proyecto completo'],
  ['esquema-funcionamiento-agnostico.mmd', 'Esquema funcionamiento agnóstico'],
  ['esquema-acciones-particulares.mmd', 'Esquema acciones particulares'],
  ['codigo-vs-artefactos.mmd', 'Código vs artefactos'],
  ['flujo-automation-datadog-alert.mmd', 'Flujo automation Datadog alert'],
  ['4-fases-protocolo.mmd', '4 fases protocolo'],
  ['flujo-github-pages.mmd', 'Flujo GitHub Pages'],
  ['flujo-workspace.mmd', 'Flujo workspace'],
  ['flujo-onboarding.mmd', 'Flujo onboarding'],
];

function main() {
  let count = 0;
  for (const [mmdFile, title] of PAIRS) {
    const mmdPath = path.join(DIAGRAMS_DIR, mmdFile);
    const htmlFile = mmdFile.replace('.mmd', '.html');
    const htmlPath = path.join(DIAGRAMS_DIR, htmlFile);

    if (!fs.existsSync(mmdPath)) {
      console.warn(`Saltando ${mmdFile}: no existe`);
      continue;
    }

    const html = generateHtml(mmdPath, title, mmdFile);
    fs.writeFileSync(htmlPath, html, 'utf8');
    console.log(`Generado: ${htmlFile}`);
    count++;
  }
  console.log(`\n${count} archivos HTML regenerados.`);
}

main();
