/**
 * Raíz del workspace de artefactos (planes, reportes, audit, playwright).
 * WORKSPACE_ROOT (env): ruta absoluta o relativa al repo (ej. Workspace/mi-plataforma).
 * Si no está definida, se requiere configurarla o se usa un directorio genérico.
 */
const path = require('path');

const REPO_ROOT = path.join(__dirname, '..');

function getWorkspaceRoot() {
  const w = process.env.WORKSPACE_ROOT?.trim();
  if (!w) {
    console.warn('[workspace-root] WORKSPACE_ROOT no definida. Usa: export WORKSPACE_ROOT=Workspace/<tu-plataforma>');
    return path.join(REPO_ROOT, 'Workspace');
  }
  return path.isAbsolute(w) ? w : path.join(REPO_ROOT, w);
}

module.exports = { getWorkspaceRoot, REPO_ROOT };
