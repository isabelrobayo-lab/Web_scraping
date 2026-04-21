#!/usr/bin/env node
/**
 * Abre el navegador en Microsoft Clarity → Configuración → Exportar datos
 * (pantalla para generar el token JWT de Data Export / MCP).
 *
 * Uso:
 *   node scripts/playwright-open-clarity-token.js
 *   CLARITY_PROJECT_ID=otroid node scripts/playwright-open-clarity-token.js
 *
 * Sesión ya iniciada en tu Chrome (macOS): cierra Chrome por completo y:
 *   PW_CHROME_USER_DATA="$HOME/Library/Application Support/Google/Chrome" \
 *     node scripts/playwright-open-clarity-token.js
 *
 * Si aparece login (Google/Microsoft), el script espera a volver al proyecto (por defecto 300 s):
 *   CLARITY_LOGIN_WAIT_MS=600000 node scripts/playwright-open-clarity-token.js
 *
 * @see https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-data-export-api
 */

const readline = require('readline');
const { chromium } = require('playwright');

const PROJECT_ID = process.env.CLARITY_PROJECT_ID || 'h4i8y1mwao';
const USER_DATA = process.env.PW_CHROME_USER_DATA || '';
const LOGIN_WAIT_MS = parseInt(process.env.CLARITY_LOGIN_WAIT_MS || '300000', 10);

function waitEnter(message) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(message, () => {
      rl.close();
      resolve();
    });
  });
}

function isAuthRedirectUrl(url) {
  return /signin|accounts\.google|login\.microsoftonline|live\.com\/oauth/i.test(url);
}

async function waitUntilClarityProject(page) {
  if (!isAuthRedirectUrl(page.url())) return;
  console.log(
    'Redirección a inicio de sesión detectada. Completa el login en el navegador.\n' +
      `Esperando hasta ${Math.round(LOGIN_WAIT_MS / 1000)} s a volver al proyecto en Clarity…\n`,
  );
  await page.waitForURL(
    (u) =>
      u.hostname.includes('clarity.microsoft.com') &&
      u.pathname.includes(`/projects/view/${PROJECT_ID}`),
    { timeout: LOGIN_WAIT_MS },
  );
}

/**
 * A veces la URL ya es /projects/view/.../settings pero el body muestra «sesión expirada»
 * (mismo dominio que con sesión). Esperamos a que el usuario inicie sesión en la ventana.
 */
async function waitUntilClaritySessionActive(page) {
  const needsLogin = await page
    .evaluate(() => {
      const t = (document.body && document.body.innerText) || '';
      return (
        /sesión ha expirado|session has expired|sign in to continue|inicia sesión en microsoft/i.test(
          t,
        ) && !/exportar datos|data export/i.test(t)
      );
    })
    .catch(() => false);

  if (!needsLogin) return;

  console.log(
    'Sesión de Clarity no activa (expirada o sin login). Inicia sesión en el navegador.\n' +
      `Esperando hasta ${Math.round(LOGIN_WAIT_MS / 1000)} s a que cargue la configuración del proyecto…\n`,
  );

  await page.waitForFunction(
    () => {
      const t = (document.body && document.body.innerText) || '';
      const expired = /sesión ha expirado|session has expired/i.test(t);
      const hasExport = /exportar datos|data export|export data/i.test(t);
      const looksLikeApp =
        /paneles|dashboards|grabaciones|recordings|mapas térmicos|heatmaps|configuración/i.test(t);
      return hasExport || (looksLikeApp && !expired);
    },
    { timeout: LOGIN_WAIT_MS },
  );
}

/**
 * Clic por texto visible en el DOM (main + iframes). Útil si la UI no expone roles ARIA estándar.
 */
async function clickExportarDatosViaEvaluate(frame) {
  return frame.evaluate(() => {
    const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
    const exact = [
      /^exportar datos$/i,
      /^data export$/i,
      /^export data$/i,
      /^exportación de datos$/i,
    ];
    const selectors = 'a[href], button, [role="menuitem"], [role="treeitem"], [role="link"], [role="tab"]';
    const nodes = /** @type {NodeListOf<HTMLElement>} */ (document.querySelectorAll(selectors));
    for (const el of nodes) {
      const t = norm(el.innerText || el.textContent || '');
      if (!t) continue;
      if (exact.some((re) => re.test(t))) {
        el.click();
        return { ok: true, text: t };
      }
    }
    return { ok: false, text: null };
  });
}

/**
 * El lateral de Configuración en Clarity cambia según idioma y versión de la UI;
 * probamos varios roles, todos los frames y evaluate como último recurso.
 */
async function clickExportarDatos(page) {
  const label = /Exportar datos|Data export|Export data|Exportación de datos/i;

  /** @type {Array<(ctx: import('playwright').Page | import('playwright').Frame) => import('playwright').Locator>} */
  const candidates = [
    (ctx) => ctx.getByRole('link', { name: label }),
    (ctx) => ctx.getByRole('treeitem', { name: label }),
    (ctx) => ctx.getByRole('menuitem', { name: label }),
    (ctx) => ctx.getByRole('button', { name: label }),
    (ctx) => ctx.getByRole('tab', { name: label }),
    (ctx) => ctx.locator('a').filter({ hasText: label }),
    (ctx) => ctx.locator('a:has-text("Exportar datos")'),
    (ctx) => ctx.locator('a:has-text("Data export")'),
    (ctx) =>
      ctx.locator('[role="listitem"], [role="option"], li').filter({ hasText: label }).locator('a').first(),
    (ctx) => ctx.locator('button').filter({ hasText: label }),
  ];

  const deadline = Date.now() + 90_000;
  let lastErr;
  while (Date.now() < deadline) {
    for (const frame of page.frames()) {
      for (const make of candidates) {
        const loc = make(frame).first();
        try {
          if (await loc.isVisible({ timeout: 800 }).catch(() => false)) {
            await loc.scrollIntoViewIfNeeded();
            await loc.click({ timeout: 15_000 });
            return;
          }
        } catch (e) {
          lastErr = e;
        }
      }
      try {
        const ev = await clickExportarDatosViaEvaluate(frame);
        if (ev.ok) {
          await page.waitForTimeout(1500);
          return;
        }
      } catch (e) {
        lastErr = e;
      }
    }
    await page.waitForTimeout(800);
  }

  console.error('URL actual:', page.url());
  const main = await page
    .evaluate(() => (document.body ? document.body.innerText.slice(0, 2500) : ''))
    .catch(() => '');
  if (main) console.error('Fragmento del texto visible (main frame):\n', main.slice(0, 1200));
  throw lastErr || new Error('No se encontró el enlace «Exportar datos» / Data export en 90 s.');
}

async function openDataExport(page) {
  const settingsUrl = `https://clarity.microsoft.com/projects/view/${PROJECT_ID}/settings`;
  await page.goto(settingsUrl, { waitUntil: 'domcontentloaded', timeout: 90_000 });

  await waitUntilClarityProject(page);
  await waitUntilClaritySessionActive(page);

  // SPA: hidrato del menú lateral
  await page.waitForTimeout(4500);

  const configTop = page.getByRole('tab', { name: /Configuración|Settings/i }).first();
  if (await configTop.isVisible().catch(() => false)) {
    await configTop.click();
    await page.waitForTimeout(2000);
  }

  await clickExportarDatos(page);
}

async function main() {
  /** @type {import('playwright').Browser | null} */
  let browser = null;
  /** @type {import('playwright').BrowserContext | null} */
  let context = null;

  const common = {
    headless: false,
    channel: 'chrome',
    args: ['--disable-blink-features=AutomationControlled'],
  };

  if (USER_DATA) {
    context = await chromium.launchPersistentContext(USER_DATA, {
      ...common,
      viewport: { width: 1280, height: 800 },
    });
  } else {
    browser = await chromium.launch(common);
    context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  }

  const page = context.pages()[0] || (await context.newPage());

  try {
    console.log(
      `Proyecto Clarity: ${PROJECT_ID}\n` +
        'Si no ves tu sesión, inicia sesión en la ventana del navegador.\n' +
        'Luego usa **Generar nuevo token de API** en Exportar datos.\n',
    );
    await openDataExport(page);
    console.log('Listo: deberías estar en Exportar datos. Cierra con Enter aquí.\n');
    await waitEnter('Pulsa Enter para cerrar el navegador… ');
  } finally {
    await context.close();
    if (browser) await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
