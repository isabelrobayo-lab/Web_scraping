/**
 * Lee la configuración desde WORKSPACE_ROOT/config/platforms.json (o PLATFORMS_CONFIG_PATH).
 * Usado por Playwright, audit y otros scripts para mantener el proyecto agnóstico.
 *
 * @returns {object|null} Config de defecto, o null si no existe
 */
const path = require('path');
const fs = require('fs');
const { getWorkspaceRoot, REPO_ROOT } = require('./workspace-root.js');

function getConfigPath() {
  if (process.env.PLATFORMS_CONFIG_PATH) {
    const p = process.env.PLATFORMS_CONFIG_PATH.trim();
    return path.isAbsolute(p) ? p : path.join(REPO_ROOT, p);
  }
  return path.join(getWorkspaceRoot(), 'config', 'platforms.json');
}

function getPlatformsConfig() {
  const configPath = getConfigPath();
  if (!fs.existsSync(configPath)) return null;
  return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
}

/**
 * ID de plataforma activa: PLATFORM_ID (env) si existe y coincide con una entrada;
 * si no, defaultPlatformId del JSON.
 */
function resolveActivePlatformId(config) {
  const envId = process.env.PLATFORM_ID?.trim();
  if (envId && config.platforms?.some((p) => p.id === envId)) {
    return envId;
  }
  return config.defaultPlatformId;
}

function getPlatformConfig() {
  const config = getPlatformsConfig();
  if (!config) return null;

  const activeId = resolveActivePlatformId(config);
  const platform =
    config.platforms?.find((p) => p.id === activeId) ||
    config.platforms?.find((p) => p.id === config.defaultPlatformId) ||
    config.platforms?.[0];
  return platform || null;
}

/**
 * Obtiene todas las plataformas configuradas (para filtros, índices, etc.)
 */
function getAllPlatforms() {
  const config = getPlatformsConfig();
  return config?.platforms || [];
}

/**
 * Obtiene la URL base de la app (desde config o env)
 */
function getBaseUrl() {
  const platform = getPlatformConfig();
  return platform?.urls?.app || process.env.BASE_URL || null;
}

/**
 * Obtiene los paths para smoke tests (desde config o default)
 */
function getSmokePaths() {
  const platform = getPlatformConfig();
  return platform?.smokePaths || ['/'];
}

/**
 * Obtiene las zonas para auditoría (desde config o default)
 */
function getAuditZones() {
  const platform = getPlatformConfig();
  if (platform?.auditZones?.length) return platform.auditZones;
  return [{ name: 'Home', url: '/' }];
}

module.exports = {
  getPlatformConfig,
  getBaseUrl,
  getSmokePaths,
  getAuditZones,
  getAllPlatforms,
  getPlatformsConfig,
};
