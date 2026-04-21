#!/usr/bin/env node
/**
 * Sincroniza activación de subagentes (Task) de Cursor con Miniverse vía POST /api/heartbeat.
 * Prioridad: primera línea del prompt `[miniverse:CLAVE]` (obligatoria según Orquestador).
 * Invocado desde legacy .cursor/hooks.json → subagentStart / subagentStop.
 *
 * Requiere: Miniverse API en marcha (npm run dev en miniverse/ → :4321).
 * Override: MINIVERSE_URL=http://localhost:4322 node ...
 */
import { readFileSync } from 'node:fs';
import { mkdir, readFile, unlink, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const BASE = (process.env.MINIVERSE_URL || 'http://localhost:4321').replace(/\/$/, '');
const TASK_MAX = 220;

/** Estado local: Cursor a veces envía `subagentStop` sin prompt; reutilizamos el último Start del mismo cwd (repo). */
const LAST_SUBAGENT_FILE = join(process.cwd(), '.cursor', '.miniverse-last-subagent.json');

/** Primera línea del prompt: [miniverse:scout] etc. (case-insensitive, tolera espacios previos). */
const MINIVERSE_TAG = /^\s*\[miniverse:([a-z0-9-]+)\]\s*/i;

/** Alineado con miniverse/scripts/seed-inventory-agents.mjs (ids inv-*). */
const INVENTORY = {
  orquestador: { agent: 'inv-orquestador', name: 'Orquestador' },
  scout: { agent: 'inv-scout', name: 'Scout' },
  historian: { agent: 'inv-historian', name: 'Historian' },
  guardian: { agent: 'inv-guardian', name: 'Guardian' },
  githubRepos: { agent: 'inv-github-repos', name: 'GitHub Repos' },
  poAgile: { agent: 'inv-po-agile', name: 'PO-Agile' },
  docUpdater: { agent: 'inv-doc-updater', name: 'Doc Updater' },
  datadog: { agent: 'inv-cloud-datadog', name: 'Cloud Agent Datadog' },
  clarity: { agent: 'inv-clarity-behavior', name: 'Clarity Behavior' },
};

/** CLAVES del Orquestador → ciudadano. Alias aceptados. */
const KEY_TO_ENTRY = {
  scout: INVENTORY.scout,
  historian: INVENTORY.historian,
  guardian: INVENTORY.guardian,
  'github-repos': INVENTORY.githubRepos,
  github: INVENTORY.githubRepos,
  'po-agile': INVENTORY.poAgile,
  po: INVENTORY.poAgile,
  'doc-updater': INVENTORY.docUpdater,
  doc: INVENTORY.docUpdater,
  'cloud-datadog': INVENTORY.datadog,
  datadog: INVENTORY.datadog,
  clarity: INVENTORY.clarity,
  'clarity-behavior': INVENTORY.clarity,
};

function stripMiniverseTag(taskText) {
  const t = String(taskText ?? '');
  const m = t.match(MINIVERSE_TAG);
  if (!m) return { key: null, displayTask: t.trim() };
  const key = m[1].toLowerCase();
  const displayTask = t.slice(m[0].length).trim().replace(/^\n+/, '');
  return { key, displayTask };
}

/** Campos donde Cursor puede mandar el prompt del Task (orden: más específico primero). */
const TASK_TEXT_KEYS = ['task', 'description', 'summary', 'prompt', 'message', 'body', 'title'];

function collectTaskTextBlocks(input) {
  if (!input || typeof input !== 'object') return [];
  return TASK_TEXT_KEYS.map((k) => input[k]).filter((v) => v != null && String(v).trim());
}

function taskBlob(input) {
  if (!input || typeof input !== 'object') return '';
  const fromKeys = collectTaskTextBlocks(input).join(' ');
  const rest = Object.entries(input)
    .filter(([k, v]) => typeof v === 'string' && v.trim() && !TASK_TEXT_KEYS.includes(k))
    .map(([, v]) => v)
    .join(' ');
  return `${fromKeys} ${rest}`.toLowerCase();
}

function resolveByTag(taskText) {
  const { key } = stripMiniverseTag(taskText);
  if (!key) return null;
  return KEY_TO_ENTRY[key] ?? null;
}

/** Busca [miniverse:…] en el primer bloque que lo tenga o al inicio del texto combinado. */
function resolveTagFromInput(input) {
  for (const block of collectTaskTextBlocks(input)) {
    const tagged = resolveByTag(String(block).trim());
    if (tagged) return tagged;
  }
  const combined = collectTaskTextBlocks(input).join('\n').trim();
  if (combined) {
    const tagged = resolveByTag(combined);
    if (tagged) return tagged;
  }
  return null;
}

/** Texto del prompt para quitar la etiqueta en la UI (mismo criterio que el tag). */
function primaryPromptText(input) {
  const blocks = collectTaskTextBlocks(input);
  for (const block of blocks) {
    const trimmed = String(block).trim();
    const { key } = stripMiniverseTag(trimmed);
    if (key && KEY_TO_ENTRY[key]) return trimmed;
  }
  if (blocks.length) return String(blocks[0]).trim();
  return String(input?.task ?? input?.description ?? '').trim();
}

function normalizeSubagentType(raw) {
  let s = String(raw ?? '')
    .trim()
    .toLowerCase()
    .replace(/_/g, '-')
    .replace(/\s+/g, '-');
  while (s.includes('--')) s = s.replace(/--+/g, '-');
  if (s === 'general-purpose') s = 'generalpurpose';
  return s;
}

function rawSubagentType(input) {
  return input?.subagent_type ?? input?.subagentType ?? '';
}

/**
 * Mapea subagent_type + texto del task al ciudadano del inventario.
 * Si hay `[miniverse:…]` en cualquier campo de texto del hook, prioridad absoluta (Orquestador).
 */
function resolveInventoryAgent(input) {
  const tagged = resolveTagFromInput(input);
  if (tagged) return tagged;

  const typeNorm = normalizeSubagentType(rawSubagentType(input));
  const blob = taskBlob(input);

  if (typeNorm === 'explore') return INVENTORY.historian;
  if (typeNorm === 'shell') return INVENTORY.guardian;
  if (typeNorm === 'best-of-n-runner' || typeNorm === 'bestofnrunner') return INVENTORY.guardian;

  if (
    typeNorm === 'api-readiness-analyzer' ||
    /api readiness|openapi|swagger|postman|agent-ready/i.test(blob)
  ) {
    return INVENTORY.scout;
  }

  // No forzar Scout por un subagent_type desconocido: Cursor puede enviar valores internos;
  // dejar pasar a heurísticas por texto y recién al final usar Scout como fallback.

  if (/datadog|observabilidad|monitor\b|apm\b|slo\b|bits_ai|mcp.*datadog/i.test(blob)) return INVENTORY.datadog;
  if (/clarity|comportamiento.*usuario|sesiones.*producción|ux.*real|mcp.*clarity|microsoft.*clarity/i.test(blob)) return INVENTORY.clarity;
  if (/repos extern|platforms\.json.*github|user-github|\bgh\s|pull request|list_commits|repositorios de plataforma/i.test(blob)) {
    return INVENTORY.githubRepos;
  }
  if (/jira|confluence|atlassian|ticket\b|backlog|mcp.*atlassian|scout\b|especificación/i.test(blob)) {
    return INVENTORY.scout;
  }
  if (/invest|gherkin|po-agile|historia de usuario|product owner|agile master|user stor/i.test(blob)) {
    return INVENTORY.poAgile;
  }
  if (/doc-updater|documentación viva|actualizar docs|runbook|docs\/architecture/i.test(blob)) {
    return INVENTORY.docUpdater;
  }
  if (/playwright|e2e|npm test|guardian|shell.*test/i.test(blob)) return INVENTORY.guardian;
  if (/explore|codebase|código|repo|historian/i.test(blob)) return INVENTORY.historian;

  return INVENTORY.scout;
}

/** Hay datos en el hook suficientes para resolver el agente sin leer el archivo de último Start. */
function stopPayloadHasResolutionSignal(input) {
  if (collectTaskTextBlocks(input).length > 0) return true;
  const t = normalizeSubagentType(rawSubagentType(input));
  if (
    t === 'explore' ||
    t === 'shell' ||
    t === 'best-of-n-runner' ||
    t === 'bestofnrunner' ||
    t === 'api-readiness-analyzer'
  ) {
    return true;
  }
  return false;
}

const KNOWN_AGENT_IDS = new Set(Object.values(INVENTORY).map((x) => x.agent));

async function writeLastSubagent(entry) {
  try {
    await mkdir(join(process.cwd(), '.cursor'), { recursive: true });
    await writeFile(LAST_SUBAGENT_FILE, JSON.stringify(entry, null, 0), 'utf8');
  } catch (e) {
    console.error('[cursor-miniverse-sync] writeLastSubagent:', e?.message || e);
  }
}

async function readLastSubagent() {
  try {
    const raw = await readFile(LAST_SUBAGENT_FILE, 'utf8');
    const o = JSON.parse(raw);
    if (o?.agent && o?.name && KNOWN_AGENT_IDS.has(o.agent)) {
      return { agent: o.agent, name: o.name };
    }
  } catch {
    /* sin archivo o JSON inválido */
  }
  return null;
}

async function clearLastSubagent() {
  try {
    await unlink(LAST_SUBAGENT_FILE);
  } catch {
    /* ya no existe */
  }
}

async function readStdin() {
  if (process.stdin.isTTY) return '{}';
  try {
    // Node 25+: fs.promises.readFile(0) rechaza el fd numérico; readFileSync(0) sigue siendo válido.
    return readFileSync(0, 'utf8');
  } catch {
    return '{}';
  }
}

async function heartbeat(body) {
  try {
    const res = await fetch(`${BASE}/api/heartbeat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const t = await res.text().catch(() => '');
      console.error(`[cursor-miniverse-sync] ${res.status} ${t}`);
    }
  } catch (e) {
    console.error('[cursor-miniverse-sync]', e?.message || e);
  }
}

async function main() {
  const mode = process.argv[2];
  const raw = await readStdin();
  let input = {};
  try {
    input = JSON.parse(raw || '{}');
  } catch {
    input = {};
  }

  const taskRaw = primaryPromptText(input);
  const { displayTask } = stripMiniverseTag(taskRaw);
  const taskLabel = (displayTask || 'Task').slice(0, TASK_MAX);

  const { agent, name } = resolveInventoryAgent(input);

  if (mode === 'subagentStart') {
    await heartbeat({
      agent: INVENTORY.orquestador.agent,
      name: INVENTORY.orquestador.name,
      state: 'working',
      task: `Activando → ${name}`,
    });
    await heartbeat({
      agent,
      name,
      state: 'working',
      task: taskLabel || 'Task',
    });
    await writeLastSubagent({ agent, name });
    console.log(JSON.stringify({ permission: 'allow' }));
    return;
  }

  if (mode === 'subagentStop') {
    let specialist = { agent, name };
    if (!stopPayloadHasResolutionSignal(input)) {
      const last = await readLastSubagent();
      if (last) specialist = last;
    }

    await heartbeat({
      agent: specialist.agent,
      name: specialist.name,
      state: 'idle',
      task: null,
    });
    await heartbeat({
      agent: INVENTORY.orquestador.agent,
      name: INVENTORY.orquestador.name,
      state: 'idle',
      task: null,
    });
    await clearLastSubagent();
    console.log(JSON.stringify({}));
    return;
  }

  console.error('Uso: node cursor-miniverse-sync.mjs subagentStart|subagentStop < stdin.json');
  process.exit(1);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
