/**
 * Registra en el servidor Miniverse los 8 agentes de docs/architecture/6-inventario-agentes.md
 * vía POST /api/heartbeat. La UI (Vite) solo lee /api/agents al cargar: tras ejecutar esto,
 * recarga http://localhost:5173/
 *
 * Uso:
 *   npm run seed:agents
 *   MINIVERSE_API_URL=http://localhost:4322 npm run seed:agents
 *   npm run seed:agents:live   # heartbeats cada 20s hasta Ctrl+C
 */
const BASE = (process.env.MINIVERSE_API_URL || 'http://localhost:4321').replace(/\/$/, '');

/** Misma lista que tests/miniverse.spec.js (ids estables). */
const INVENTORY_AGENTS = [
  { agent: 'inv-orquestador', name: 'Orquestador', state: 'working' },
  { agent: 'inv-scout', name: 'Scout', state: 'idle' },
  { agent: 'inv-historian', name: 'Historian', state: 'thinking' },
  { agent: 'inv-guardian', name: 'Guardian', state: 'working' },
  { agent: 'inv-github-repos', name: 'GitHub Repos', state: 'idle' },
  { agent: 'inv-po-agile', name: 'PO-Agile', state: 'idle' },
  { agent: 'inv-doc-updater', name: 'Doc Updater', state: 'idle' },
  { agent: 'inv-cloud-datadog', name: 'Cloud Agent Datadog', state: 'sleeping' },
  { agent: 'inv-clarity-behavior', name: 'Clarity Behavior', state: 'idle' },
];

async function seed() {
  for (const a of INVENTORY_AGENTS) {
    const res = await fetch(`${BASE}/api/heartbeat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent: a.agent,
        name: a.name,
        state: a.state,
        task: `Local · ${a.name}`,
      }),
    });
    if (!res.ok) {
      const t = await res.text();
      throw new Error(`${res.status} ${t}`);
    }
  }
}

const live = process.argv.includes('--keep-alive');
const INTERVAL_MS = 20_000;

async function main() {
  await seed();
  console.log(
    `Listo: ${INVENTORY_AGENTS.length} agentes en ${BASE}. Recarga la pestaña de Miniverse (5173).`,
  );
  if (live) {
    console.log(`Heartbeats cada ${INTERVAL_MS / 1000}s (Ctrl+C para salir).`);
    setInterval(() => {
      seed().catch((e) => console.error('[seed-inventory-agents]', e.message));
    }, INTERVAL_MS);
  }
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
