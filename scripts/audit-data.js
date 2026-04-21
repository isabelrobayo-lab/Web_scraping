/**
 * Datos y helpers para auditoría de consola.
 * Zonas por defecto cuando no hay config/platforms.json en el workspace activo.
 * Para plataformas específicas, definir auditZones en platforms.json.
 */

const ZONES = [{ name: "Home", url: "/" }];

function createEmptyReport() {
  return {
    timestamp: new Date().toISOString(),
    zones: [],
    allConsoleMessages: [],
    summary: { errors: 0, warnings: 0, logs: 0 },
  };
}

function categorizeMessage(type, summary) {
  if (type === "error") summary.errors++;
  else if (type === "warning") summary.warnings++;
  else summary.logs++;
}

module.exports = { ZONES, createEmptyReport, categorizeMessage };
