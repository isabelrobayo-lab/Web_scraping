#!/usr/bin/env node
/**
 * Análisis de tiempo por fase del ciclo de desarrollo
 * Procesa HUs cerradas de Jira con campos de tiempo custom
 *
 * Campos (horas):
 * - customfield_24748: Tiempo de Por hacer a Producción (ciclo total)
 * - customfield_24759: Tiempo en Por Hacer (Backlog)
 * - customfield_24764: Tiempo en Progreso (Desarrollo)
 * - customfield_24765: Tiempo en Pruebas QA
 * - customfield_24767: Tiempo en Pruebas UAT
 * - customfield_24757: Tiempo en Pendiente PAP (esperando deploy)
 * - customfield_24762: Tiempo en Producción
 */

const fs = require('fs');
const path = require('path');
const { getWorkspaceRoot } = require('../../scripts/workspace-root.js');

const FIELDS = {
  customfield_24748: 'Ciclo total (Por hacer → Producción)',
  customfield_24759: 'Por Hacer (Backlog)',
  customfield_24764: 'En Progreso (Desarrollo)',
  customfield_24765: 'Pruebas QA',
  customfield_24767: 'Pruebas UAT',
  customfield_24757: 'Pendiente PAP (esperando deploy)',
  customfield_24762: 'Producción',
};

function analyzeFromData(data) {
  if (!data.issues || !Array.isArray(data.issues)) {
    throw new Error('Formato inválido: se esperaba { issues: [...] }');
  }

  const issues = data.issues;
  const stats = {};
  const byProject = {};

  for (const fieldId of Object.keys(FIELDS)) {
    stats[fieldId] = { values: [], sum: 0, count: 0 };
  }

  for (const issue of issues) {
    const f = issue.fields || {};
    const projectKey = f.project?.key || 'N/A';

    if (!byProject[projectKey]) {
      byProject[projectKey] = {};
      for (const fieldId of Object.keys(FIELDS)) {
        byProject[projectKey][fieldId] = { values: [], sum: 0, count: 0 };
      }
    }

    for (const fieldId of Object.keys(FIELDS)) {
      const val = f[fieldId];
      if (val != null && typeof val === 'number' && !Number.isNaN(val) && val >= 0) {
        stats[fieldId].values.push(val);
        stats[fieldId].sum += val;
        stats[fieldId].count += 1;

        byProject[projectKey][fieldId].values.push(val);
        byProject[projectKey][fieldId].sum += val;
        byProject[projectKey][fieldId].count += 1;
      }
    }
  }

  return { stats, byProject, totalIssues: issues.length };
}

function analyze(dataPath) {
  const raw = fs.readFileSync(dataPath, 'utf8');
  const data = JSON.parse(raw);
  return analyzeFromData(data);
}

function formatHours(h) {
  if (h == null || (typeof h === 'number' && isNaN(h))) return '—';
  const n = Number(h);
  if (n === 0) return '0h';
  if (n >= 24) {
    const days = Math.floor(n / 24);
    const remainderHours = n - days * 24;
    const restRounded = Math.round(remainderHours * 10) / 10;
    if (restRounded <= 0) return `${days}d`;
    return `${days}d ${restRounded.toFixed(1)}h`;
  }
  return `${Math.round(n * 10) / 10}h`;
}

function report({ stats, byProject, totalIssues }) {
  const lines = [];

  lines.push('# Análisis de tiempo por fase del ciclo de desarrollo');
  lines.push('');
  lines.push(`**Muestra:** ${totalIssues} Historias de Usuario cerradas`);
  lines.push(`**Rango:** 1 enero - 30 marzo 2025`);
  lines.push(`**Proyectos:** ${Object.keys(byProject).length} distintos`);
  lines.push('');
  lines.push('---');
  lines.push('');
  lines.push('## Promedio de horas por fase (todas las HUs)');
  lines.push('');
  lines.push('> **Nota:** Los campos de tiempo pueden usar unidades distintas según el workflow (horas de trabajo vs. horas de calendario). El ciclo total refleja el tiempo end-to-end.');
  lines.push('');
  lines.push('| Fase del ciclo | Promedio (horas) | Promedio (días) | HUs con dato |');
  lines.push('|----------------|------------------|-----------------|--------------|');

  const totalCycle = stats.customfield_24748;
  const totalCycleFiltered = totalCycle.values.filter((v) => v > 0);
  const totalAvg =
    totalCycleFiltered.length > 0
      ? totalCycleFiltered.reduce((a, b) => a + b, 0) / totalCycleFiltered.length
      : 0;

  for (const [fieldId, label] of Object.entries(FIELDS)) {
    const s = stats[fieldId];
    const vals = s.values.filter((v) => v > 0);
    const avg = vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
    const avgDays = (avg / 24).toFixed(1);
    lines.push(`| ${label} | ${avg.toFixed(1)} | ${avgDays} | ${s.count} |`);
  }

  lines.push('');
  lines.push('---');
  lines.push('');
  lines.push('## Resumen ejecutivo');
  lines.push('');
  lines.push(`- **Ciclo total promedio (Por hacer → Producción):** ${formatHours(totalAvg)} (${(totalAvg / 24).toFixed(1)} días)`);
  lines.push(`- **HUs con ciclo total > 0:** ${totalCycleFiltered.length} de ${totalCycle.count}`);
  lines.push('');

  const phases = [
    ['customfield_24759', 'Backlog'],
    ['customfield_24764', 'Desarrollo'],
    ['customfield_24765', 'QA'],
    ['customfield_24767', 'UAT'],
    ['customfield_24757', 'Pendiente PAP'],
    ['customfield_24762', 'Producción'],
  ];

  const phaseAvgs = phases
    .map(([id, name]) => {
      const s = stats[id];
      const vals = s.values.filter((v) => v > 0);
      return { name, avg: vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : 0 };
    })
    .filter((p) => p.avg > 0)
    .sort((a, b) => b.avg - a.avg);

  if (phaseAvgs.length > 0) {
    lines.push('**Fases con mayor tiempo promedio (horas registradas):**');
    phaseAvgs.slice(0, 5).forEach((p, i) => {
      lines.push(`${i + 1}. **${p.name}**: ${formatHours(p.avg)}`);
    });
  }

  lines.push('');
  lines.push('---');
  lines.push('');
  lines.push('## Por proyecto (top 10 por volumen)');
  lines.push('');

  const projectCounts = {};
  for (const [proj, data] of Object.entries(byProject)) {
    projectCounts[proj] = data.customfield_24748?.count || 0;
  }
  const topProjects = Object.entries(projectCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([p]) => p);

  for (const proj of topProjects) {
    const d = byProject[proj];
    const cycle = d.customfield_24748;
    const vals = cycle?.values?.filter((v) => v > 0) || [];
    const avgCycle = vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
    lines.push(`### ${proj} (${cycle?.count || 0} HUs)`);
    lines.push(`- Ciclo total promedio: ${formatHours(avgCycle)}${vals.length === 0 ? ' (sin datos)' : ''}`);
    lines.push('');
  }

  return lines.join('\n');
}

function main() {
  const dataPath =
    process.argv[2] ||
    path.join(__dirname, '../../docs/data/jira-cycle-2025.json');

  if (!fs.existsSync(dataPath)) {
    console.error('No se encontró el archivo de datos. Uso: node analyze-cycle-time.js <ruta-json>');
    process.exit(1);
  }

  const result = analyze(dataPath);
  const reportMd = report(result);
  console.log(reportMd);

  const outPath = path.join(getWorkspaceRoot(), 'reports', 'analisis-ciclo-desarrollo.md');
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, reportMd, 'utf8');
  console.log('\n---\nReporte guardado en:', outPath);
}

// Exportadas para tests unitarios
module.exports = { analyze, analyzeFromData, formatHours, report };

// Solo ejecutar main cuando se invoca directamente (node analyze-cycle-time.js)
if (require.main === module) main();
