// @ts-check
/**
 * Smoke tests E2E para Miniverse (upstream @miniverse/core + Vite).
 * Ejecutar con: npx playwright test tests/miniverse.spec.js --project=miniverse
 * Requiere `npm run dev` en miniverse/ (Vite :5173 + API :4321).
 */
const { test, expect } = require('@playwright/test');

const MINIVERSE_API = process.env.MINIVERSE_API_URL || 'http://localhost:4321';

/** Los 8 agentes de docs/architecture/6-inventario-agentes.md (ids estables para E2E). */
const INVENTORY_AGENTS = [
  { agent: 'inv-orquestador', name: 'Orquestador', state: 'working' },
  { agent: 'inv-scout', name: 'Scout', state: 'idle' },
  { agent: 'inv-historian', name: 'Historian', state: 'thinking' },
  { agent: 'inv-guardian', name: 'Guardian', state: 'working' },
  { agent: 'inv-github-repos', name: 'GitHub Repos', state: 'idle' },
  { agent: 'inv-po-agile', name: 'PO-Agile', state: 'idle' },
  { agent: 'inv-doc-updater', name: 'Doc Updater', state: 'idle' },
  { agent: 'inv-cloud-datadog', name: 'Cloud Agent Datadog', state: 'sleeping' },
];

test.describe('Miniverse', () => {
  test('carga el mundo y muestra el canvas', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('Miniverse');
    await expect(page.locator('#miniverse-container canvas')).toBeVisible({ timeout: 20000 });
  });

  test('API heartbeat responde correctamente', async ({ request }) => {
    const res = await request.post(`${MINIVERSE_API}/api/heartbeat`, {
      data: { agent: 'e2e-test', name: 'E2E', state: 'idle' },
    });
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    expect(body.ok).toBe(true);
    expect(body.agent.agent).toBe('e2e-test');
  });

  test('los 8 agentes del inventario aparecen en la API y en el mundo', async ({ page, request }) => {
    await request
      .post(`${MINIVERSE_API}/api/agents/remove`, { data: { agent: 'e2e-test' } })
      .catch(() => {});

    for (const a of INVENTORY_AGENTS) {
      const res = await request.post(`${MINIVERSE_API}/api/heartbeat`, {
        data: { agent: a.agent, name: a.name, state: a.state, task: `E2E · ${a.name}` },
      });
      expect(res.ok()).toBeTruthy();
    }

    const listRes = await request.get(`${MINIVERSE_API}/api/agents`);
    expect(listRes.ok()).toBeTruthy();
    const { agents } = await listRes.json();
    const ids = new Set((agents ?? []).map((x) => x.agent));
    for (const a of INVENTORY_AGENTS) {
      expect(ids.has(a.agent), `debe existir ${a.agent} en /api/agents`).toBeTruthy();
    }

    // El cliente solo descubre ciudadanos en el arranque: cargar tras los heartbeats
    await page.goto('/');
    await expect(page.locator('#miniverse-container canvas')).toBeVisible({ timeout: 20000 });

    await expect
      .poll(
        async () =>
          page.evaluate(() => globalThis.__E2E_MINIVERSE_CITIZENS__ ?? -1),
        { timeout: 15000 },
      )
      .toBe(8);
  });

  test('nueva verificación: inventario completo (8 agentes, API exacta + mundo)', async ({
    page,
    request,
  }) => {
    const cleanupIds = [...INVENTORY_AGENTS.map((x) => x.agent), 'e2e-test'];
    for (const agent of cleanupIds) {
      await request.post(`${MINIVERSE_API}/api/agents/remove`, { data: { agent } }).catch(() => {});
    }

    for (const a of INVENTORY_AGENTS) {
      const res = await request.post(`${MINIVERSE_API}/api/heartbeat`, {
        data: { agent: a.agent, name: a.name, state: a.state, task: `Equipo completo · ${a.name}` },
      });
      expect(res.ok()).toBeTruthy();
    }

    const listRes = await request.get(`${MINIVERSE_API}/api/agents`);
    expect(listRes.ok()).toBeTruthy();
    const { agents } = await listRes.json();
    const list = agents ?? [];
    expect(list.length, '/api/agents debe listar exactamente 8 agentes').toBe(8);

    const byId = Object.fromEntries(list.map((x) => [x.agent, x]));
    for (const a of INVENTORY_AGENTS) {
      const row = byId[a.agent];
      expect(row, `fila ${a.agent}`).toBeTruthy();
      expect(row.name).toBe(a.name);
      expect(row.state).toBe(a.state);
      expect(String(row.task ?? '')).toContain('Equipo completo');
    }

    await page.goto('/');
    await expect(page.locator('#miniverse-container canvas')).toBeVisible({ timeout: 20000 });
    await expect
      .poll(
        async () =>
          page.evaluate(() => globalThis.__E2E_MINIVERSE_CITIZENS__ ?? -1),
        { timeout: 15000 },
      )
      .toBe(8);
  });
});
