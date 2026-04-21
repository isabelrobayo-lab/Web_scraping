#!/usr/bin/env node
/**
 * Demostración en consola: simula el flujo Orquestador → Scout → Historian → Plan → Guardian.
 * No ejecuta MCPs ni tests; solo imprime líneas con timestamps ficticios.
 *
 * Uso: npm run demo:agentes
 *      node scripts/demo-agentes-run.js --fast
 */

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function formatClock(totalMs) {
  const s = Math.floor(totalMs / 1000);
  const ms = totalMs % 1000;
  const h = Math.floor(s / 3600) % 24;
  const m = Math.floor(s / 60) % 60;
  const sec = s % 60;
  const pad = (n, w = 2) => String(n).padStart(w, '0');
  return `${pad(h)}:${pad(m)}:${pad(sec)}.${String(ms).padStart(3, '0')}`;
}

const STEPS = [
  { t: 0, line: '[Orquestador] INICIADO (The Architect)' },
  { t: 100, line: '  └─ Scout … RUNNING → MCP atlassian: leer ticket' },
  { t: 7800, line: '  └─ Scout … OK → requisitos extraídos' },
  { t: 9000, line: '  └─ Historian … RUNNING → @Codebase, gh pr list' },
  { t: 45000, line: '  └─ Historian … OK → impacto resumido' },
  { t: 46000, line: '  └─ Planificación … RUNNING → Workspace/plans/plan-demo.md' },
  { t: 62000, line: '  └─ Planificación … OK' },
  { t: 63000, line: '  └─ Guardian … RUNNING → npx playwright test (simulado)' },
  { t: 95000, line: '  └─ Guardian … OK → tarea cerrada (demo)' },
  { t: 96000, line: '[Orquestador] FIN (solo demostración)' },
];

async function main() {
  const fast = process.argv.includes('--fast');
  const delay = fast ? 0 : 400;

  console.log('');
  console.log('═══ Demo: agentes en ejecución (timestamps simulados, sin red ni tests) ═══');
  console.log('');

  let prevT = 0;
  for (const step of STEPS) {
    if (!fast && delay > 0) {
      await sleep(Math.min(1200, step.t - prevT) || delay);
    }
    prevT = step.t;
    console.log(`[${formatClock(step.t)}] ${step.line}`);
  }

  console.log('');
  console.log('En Cursor, los especialistas se activan con la herramienta Task (subagentes); este script solo simula tiempos en consola.');
  console.log('');
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
