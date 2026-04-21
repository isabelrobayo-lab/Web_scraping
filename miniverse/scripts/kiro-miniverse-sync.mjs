#!/usr/bin/env node
/**
 * Adaptador Kiro → Miniverse.
 * Los hooks de Kiro invocan: node kiro-miniverse-sync.mjs <agentKey> <state> ["<task>"]
 * Este script traduce esos args a POST /api/heartbeat compatible con Miniverse.
 *
 * Uso:
 *   node kiro-miniverse-sync.mjs guardian working "Ejecutando tests E2E"
 *   node kiro-miniverse-sync.mjs guardian idle
 *
 * Requiere: Miniverse API en marcha (npm run dev en miniverse/ → :4321).
 * Override: MINIVERSE_URL=http://localhost:4322 node ...
 */

const BASE = (process.env.MINIVERSE_URL || 'http://localhost:4321').replace(/\/$/, '');

const INVENTORY = {
  orquestador: { agent: 'inv-orquestador', name: 'Orquestador' },
  scout:       { agent: 'inv-scout',       name: 'Scout' },
  historian:   { agent: 'inv-historian',    name: 'Historian' },
  guardian:    { agent: 'inv-guardian',      name: 'Guardian' },
  'github-repos': { agent: 'inv-github-repos', name: 'GitHub Repos' },
  'po-agile':  { agent: 'inv-po-agile',    name: 'PO-Agile' },
  'doc-updater': { agent: 'inv-doc-updater', name: 'Doc Updater' },
  'cloud-datadog': { agent: 'inv-cloud-datadog', name: 'Cloud Agent Datadog' },
  'clarity-behavior': { agent: 'inv-clarity-behavior', name: 'Clarity Behavior' },
};

// Aliases para flexibilidad en los hooks
const ALIASES = {
  scout: 'scout',
  historian: 'historian',
  guardian: 'guardian',
  github: 'github-repos',
  'github-repos': 'github-repos',
  po: 'po-agile',
  'po-agile': 'po-agile',
  doc: 'doc-updater',
  'doc-updater': 'doc-updater',
  datadog: 'cloud-datadog',
  'cloud-datadog': 'cloud-datadog',
  clarity: 'clarity-behavior',
  'clarity-behavior': 'clarity-behavior',
};

async function heartbeat(body) {
  try {
    const res = await fetch(`${BASE}/api/heartbeat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const t = await res.text().catch(() => '');
      console.error(`[kiro-miniverse-sync] ${res.status} ${t}`);
    }
  } catch {
    // Miniverse no levantado — fallo silencioso
  }
}

async function main() {
  const [,, rawKey, state, ...taskParts] = process.argv;
  const task = taskParts.join(' ') || null;

  if (!rawKey || !state) {
    console.error('Uso: node kiro-miniverse-sync.mjs <agentKey> working|idle ["<task>"]');
    process.exit(1);
  }

  const normalizedKey = ALIASES[rawKey.toLowerCase()] ?? rawKey.toLowerCase();
  const entry = INVENTORY[normalizedKey];

  if (!entry) {
    console.error(`[kiro-miniverse-sync] Agente desconocido: "${rawKey}". Claves válidas: ${Object.keys(ALIASES).join(', ')}`);
    process.exit(1);
  }

  if (state === 'working') {
    // Orquestador → working (activando especialista)
    await heartbeat({
      agent: INVENTORY.orquestador.agent,
      name: INVENTORY.orquestador.name,
      state: 'working',
      task: `Activando → ${entry.name}`,
    });
    // Especialista → working
    await heartbeat({
      agent: entry.agent,
      name: entry.name,
      state: 'working',
      task: task || 'Task',
    });
  } else if (state === 'idle') {
    // Especialista → idle
    await heartbeat({
      agent: entry.agent,
      name: entry.name,
      state: 'idle',
      task: null,
    });
    // Orquestador → idle
    await heartbeat({
      agent: INVENTORY.orquestador.agent,
      name: INVENTORY.orquestador.name,
      state: 'idle',
      task: null,
    });
  } else {
    console.error(`[kiro-miniverse-sync] Estado inválido: "${state}". Usar "working" o "idle".`);
    process.exit(1);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
