/**
 * Script de auditoría: navega por la URL configurada y captura errores de consola.
 * Genera reporte con capturas de pantalla y lista de errores priorizados.
 * URL y zonas desde config/platforms.json del workspace activo (workspace-root.js).
 */

const { firefox } = require('playwright');
const path = require('path');
const fs = require('fs');
const { getBaseUrl, getAuditZones } = require('./get-platform-config.js');
const { getWorkspaceRoot } = require('./workspace-root.js');

const BASE_URL = getBaseUrl() || process.env.BASE_URL || 'https://example.com';
const ZONES = getAuditZones();
const OUTPUT_DIR = path.join(getWorkspaceRoot(), 'audit');
const SCREENSHOTS_DIR = path.join(OUTPUT_DIR, 'screenshots');

/** URL final de zona: absoluta si zone.url ya es http(s), si no se concatena con BASE_URL */
function resolveZoneUrl(baseUrl, zoneUrl) {
  if (/^https?:\/\//i.test(zoneUrl)) return zoneUrl;
  return `${baseUrl}${zoneUrl}`;
}

async function runAudit() {
  if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  if (!fs.existsSync(SCREENSHOTS_DIR)) fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });

  const report = {
    timestamp: new Date().toISOString(),
    zones: [],
    allConsoleMessages: [],
    summary: { errors: 0, warnings: 0, logs: 0 },
  };

  const browser = await firefox.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
  });

  for (const zone of ZONES) {
    const page = await context.newPage();
    const zoneMessages = [];

    page.on('console', (msg) => {
      const type = msg.type();
      const text = msg.text();
      const location = msg.location();
      const entry = {
        type,
        text,
        url: location?.url || '',
        timestamp: new Date().toISOString(),
      };
      zoneMessages.push(entry);
      report.allConsoleMessages.push({ ...entry, zone: zone.name });
      if (type === 'error') report.summary.errors++;
      else if (type === 'warning') report.summary.warnings++;
      else report.summary.logs++;
    });

    try {
      const fullUrl = resolveZoneUrl(BASE_URL, zone.url);
      console.log(`Navegando a ${zone.name}: ${fullUrl}`);
      await page.goto(fullUrl, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(3000);

      const errors = zoneMessages.filter((m) => m.type === 'error' || m.type === 'warning');
      const zoneResult = {
        name: zone.name,
        url: fullUrl,
        status: 'ok',
        errorCount: zoneMessages.filter((m) => m.type === 'error').length,
        warningCount: zoneMessages.filter((m) => m.type === 'warning').length,
        messages: zoneMessages,
        errorsOnly: errors,
      };

      if (errors.length > 0) {
        const safeName = zone.name.replace(/\s+/g, '-').toLowerCase();
        const screenshotPath = path.join(SCREENSHOTS_DIR, `${safeName}-${Date.now()}.png`);
        await page.screenshot({ path: screenshotPath, fullPage: false });
        zoneResult.screenshot = path.relative(OUTPUT_DIR, screenshotPath);
      }

      report.zones.push(zoneResult);
    } catch (err) {
      report.zones.push({
        name: zone.name,
        url: resolveZoneUrl(BASE_URL, zone.url),
        status: 'error',
        error: err.message,
        messages: zoneMessages,
      });
      console.error(`Error en ${zone.name}:`, err.message);
    } finally {
      await page.close();
    }
  }

  await browser.close();

  const reportPath = path.join(OUTPUT_DIR, 'console-audit-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2), 'utf-8');
  console.log(`\nReporte guardado en: ${reportPath}`);
  console.log(`Resumen: ${report.summary.errors} errores, ${report.summary.warnings} warnings`);

  return report;
}

runAudit().catch(console.error);
