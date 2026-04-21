#!/usr/bin/env node
/**
 * Genera reporte HTML gerencial de análisis de ciclo de desarrollo
 * Lee JSON de Jira y produce reports/analisis-ciclo-desarrollo.html bajo WORKSPACE_ROOT (ver scripts/workspace-root.js)
 */

const fs = require('fs');
const path = require('path');
const { getWorkspaceRoot } = require('../../scripts/workspace-root.js');
const { getPlatformConfig } = require('../../scripts/get-platform-config.js');

/**
 * Obtiene la URL base de Jira desde platforms.json → jira.projectUrl.
 * Fallback a variable de entorno JIRA_BASE_URL o placeholder genérico.
 */
function getJiraBase() {
  const platform = getPlatformConfig();
  const projectUrl = platform?.jira?.projectUrl;
  if (projectUrl) {
    const match = projectUrl.match(/^(https?:\/\/[^/]+\/browse)/);
    if (match) return match[1];
  }
  return process.env.JIRA_BASE_URL || 'https://jira.example.com/browse';
}

const JIRA_BASE = getJiraBase();

const PHASES = [
  { id: 'customfield_24759', label: 'Por Hacer (Backlog)' },
  { id: 'customfield_24764', label: 'En Progreso (Desarrollo)' },
  { id: 'customfield_24765', label: 'Pruebas QA' },
  { id: 'customfield_24767', label: 'Pruebas UAT' },
  { id: 'customfield_24757', label: 'Pendiente PAP (esperando deploy)' },
  { id: 'customfield_24762', label: 'Producción' },
  { id: 'customfield_24748', label: 'Ciclo total (Por hacer → Producción)' },
];

/**
 * Formatea horas a "Xd Yh" o "Yh". Evita errores de punto flotante en módulo.
 * Los valores de Jira vienen en horas decimales (ej. 48.5 = 2d 0.5h).
 */
function formatHours(h) {
  if (h == null || (typeof h === 'number' && isNaN(h))) return '—';
  const n = Number(h);
  if (n === 0) return '0 h';
  if (n >= 24) {
    const days = Math.floor(n / 24);
    const remainderHours = n - days * 24;
    const restRounded = Math.round(remainderHours * 10) / 10;
    if (restRounded <= 0) return `${days}d`;
    return `${days}d ${restRounded.toFixed(1)}h`;
  }
  return `${(Math.round(n * 10) / 10).toFixed(1)} h`;
}

function analyze(data) {
  const issues = data.issues || [];
  const stats = {};
  for (const p of PHASES) {
    const vals = issues
      .map((i) => i.fields?.[p.id])
      .filter((v) => v != null && typeof v === 'number' && !isNaN(v) && v >= 0);
    const sum = vals.reduce((a, b) => a + b, 0);
    stats[p.id] = {
      avg: vals.length ? sum / vals.length : 0,
      count: vals.length,
    };
  }
  return { issues, stats };
}

function escapeHtml(s) {
  if (s == null) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function generateHtml(dataPath, outPath) {
  const raw = fs.readFileSync(dataPath, 'utf8');
  const data = JSON.parse(raw);
  const { issues, stats } = analyze(data);

  const phaseCards = PHASES.map(
    (p) => `
    <div class="phase-card">
      <div class="phase-label">${escapeHtml(p.label)}</div>
      <div class="phase-value">${formatHours(stats[p.id].avg)}</div>
      <div class="phase-meta">promedio · ${stats[p.id].count} HUs</div>
    </div>`
  ).join('');

  const tableRows = issues
    .map((issue) => {
      const f = issue.fields || {};
      const key = issue.key;
      const summary = (f.summary || '').toLowerCase();
      const project = f.project?.key || '';
      const issuetype = (f.issuetype?.name || '').toLowerCase();
      const link = `${JIRA_BASE}/${key}`;
      const cells = PHASES.map((p, i) => {
        const val = f[p.id];
        const sortVal =
          val != null && typeof val === 'number' && !isNaN(val) ? val : -1;
        return `<td class="num" data-col="${4 + i}" data-sort="${sortVal}">${formatHours(val)}</td>`;
      }).join('');
      return `
      <tr>
        <td data-col="0" data-sort="${escapeHtml(key)}"><a href="${link}" target="_blank" rel="noopener">${escapeHtml(key)}</a></td>
        <td data-col="1" data-sort="${escapeHtml(summary)}">${escapeHtml(f.summary || '')}</td>
        <td data-col="2" data-sort="${escapeHtml(issuetype)}"><span class="badge">${escapeHtml(f.issuetype?.name || '—')}</span></td>
        <td data-col="3" data-sort="${escapeHtml(project)}">${escapeHtml(project || '—')}</td>
        ${cells}
      </tr>`;
    })
    .join('');

  const phaseHeaders = PHASES.map(
    (p, i) =>
      `<th class="sortable" data-col="${4 + i}" data-type="num" title="Clic para ordenar">${escapeHtml(p.label)}</th>`
  ).join('');

  const textHeaders = [
    '<th class="sortable" data-col="0" data-type="text" title="Clic para ordenar">Incidencia</th>',
    '<th class="sortable" data-col="1" data-type="text" title="Clic para ordenar">Resumen</th>',
    '<th class="sortable" data-col="2" data-type="text" title="Clic para ordenar">Tipo</th>',
    '<th class="sortable" data-col="3" data-type="text" title="Clic para ordenar">Proyecto</th>',
  ].join('');

  const html = `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Análisis Ciclo de Desarrollo | Reporte Gerencial | SQUAD-AGENTES-IA</title>
  <meta name="description" content="Análisis de tiempo por fase del ciclo de desarrollo. 100 HUs cerradas (1 ene - 30 mar 2025). Seguros Bolívar.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="Asset/report-base.css">
  <link rel="stylesheet" href="Asset/report-components.css">
</head>
<body>
  <div class="container container--wide">
    <a href="reportes.html" class="nav-link">← Ver todos los reportes</a>
    <a href="index.html" class="nav-link" style="margin-left: 1rem;">Inicio →</a>

    <header>
      <h1 class="report-title">Análisis de Tiempo por Fase del Ciclo de Desarrollo</h1>
      <p class="report-subtitle">Reporte gerencial · 100 Historias de Usuario cerradas · 7 proyectos</p>
      <span class="report-meta">1 enero – 30 marzo 2025 · Jira Seguros Bolívar</span>
    </header>

    <section class="section">
      <div class="summary-box">
        <h3>Resumen ejecutivo</h3>
        <p>
          Análisis de <strong>100 HUs cerradas</strong> en el rango 1 de enero a 30 de marzo de 2025,
          de <strong>7 proyectos distintos</strong>. Los datos provienen de los campos de tiempo del workflow de Jira.
          El <strong>ciclo total promedio</strong> (Por hacer → Producción) es de <strong>${formatHours(stats.customfield_24748.avg)}</strong>.
          La fase con mayor tiempo promedio es <strong>En Progreso (Desarrollo)</strong> con ${formatHours(stats.customfield_24764.avg)}.
        </p>
      </div>
      <div class="info-note">
        <strong>Importante:</strong> Los tiempos de cada fase y el ciclo total no se pueden sumar porque usan <strong>unidades distintas</strong> en Jira.
        • <em>Tiempo en X</em> (por fase): suele estar en horas de calendario (24/7).
        • <em>Ciclo total</em>: suele estar en horas de trabajo u otra métrica end-to-end.
        El Ciclo total es una métrica independiente, no la suma de las fases.
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">Promedio de horas por fase</h2>
      <div class="phases-grid">
        ${phaseCards}
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">Detalle por incidencia</h2>
      <p style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1rem;">
        Haz clic en la clave de la incidencia para abrirla en Jira.
      </p>
      <div class="table-wrapper table-wrapper--wide">
        <table id="issues-table">
          <thead>
            <tr>
              ${textHeaders}
              ${phaseHeaders}
            </tr>
          </thead>
          <tbody>
            ${tableRows}
          </tbody>
        </table>
      </div>
    </section>

    <footer class="footer">
      <p>Reporte generado el ${new Date().toLocaleDateString('es-CO', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
      <p style="margin-top: 0.5rem;">Proyecto SQUAD-AGENTES-IA</p>
      <p style="margin-top: 1rem;"><a href="reportes.html">Ver todos los reportes</a></p>
    </footer>
  </div>
  <script>
    (function() {
      var table = document.getElementById('issues-table');
      if (!table) return;
      var tbody = table.querySelector('tbody');
      var headers = table.querySelectorAll('th.sortable');
      var currentCol = -1;
      var currentDir = 1;

      function sort(colIndex, dir) {
        var rows = Array.from(tbody.querySelectorAll('tr'));
        var isNum = headers[colIndex] && headers[colIndex].dataset.type === 'num';
        rows.sort(function(a, b) {
          var cellA = a.querySelector('td[data-col="' + colIndex + '"]');
          var cellB = b.querySelector('td[data-col="' + colIndex + '"]');
          if (!cellA || !cellB) return 0;
          var valA = cellA.dataset.sort;
          var valB = cellB.dataset.sort;
          if (isNum) {
            valA = parseFloat(valA);
            valB = parseFloat(valB);
            return dir * (valA - valB);
          }
          valA = (valA || '').toLowerCase();
          valB = (valB || '').toLowerCase();
          return dir * valA.localeCompare(valB);
        });
        rows.forEach(function(r) { tbody.appendChild(r); });
      }

      headers.forEach(function(th, i) {
        th.addEventListener('click', function() {
          var colIndex = parseInt(th.dataset.col, 10);
          if (currentCol === colIndex) currentDir = -currentDir;
          else { currentCol = colIndex; currentDir = 1; }
          headers.forEach(function(h) { h.classList.remove('sorted-asc', 'sorted-desc'); });
          th.classList.add(currentDir === 1 ? 'sorted-asc' : 'sorted-desc');
          sort(colIndex, currentDir);
        });
      });
    })();
  </script>
</body>
</html>`;

  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, html, 'utf8');
  console.log('Reporte generado:', outPath);
}

const dataPath =
  process.argv[2] || path.join(__dirname, '../../docs/data/jira-cycle-2025.json');
const outPath = path.join(getWorkspaceRoot(), 'reports', 'analisis-ciclo-desarrollo.html');

if (!fs.existsSync(dataPath)) {
  console.error('No se encontró el archivo de datos. Uso: node generate-cycle-report-html.js <ruta-json>');
  process.exit(1);
}

generateHtml(dataPath, outPath);
