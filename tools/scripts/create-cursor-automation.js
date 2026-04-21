#!/usr/bin/env node
/**
 * Script Playwright para automatizar la creación de la automatización
 * "Datadog Alert → Plan + HU" en cursor.com/automations.
 *
 * Requisitos:
 * - Sesión iniciada en Cursor (el script usa contexto persistente)
 * - Ejecutar: npx node tools/scripts/create-cursor-automation.js
 *
 * La primera vez puede pedir login manual. El estado se guarda en
 * Workspace/playwright/cursor-browser-state para reutilizar la sesión.
 */

const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');
const { getWorkspaceRoot } = require('../../scripts/workspace-root.js');

const CURSOR_AUTOMATIONS_URL = 'https://cursor.com/automations';
const PROMPT_FILE = path.join(__dirname, '../../docs/templates/automation-datadog-alert-prompt.md');
const USER_DATA_DIR = path.join(getWorkspaceRoot(), 'playwright', 'cursor-browser-state');

// Contenido del prompt sin el encabezado (líneas 1-5)
function getPromptContent() {
  const full = fs.readFileSync(PROMPT_FILE, 'utf-8');
  const lines = full.split('\n');
  const startIdx = lines.findIndex((l) => l.includes('Instrucciones para el agente'));
  if (startIdx === -1) return full;
  return lines.slice(startIdx).join('\n').trim();
}

async function main() {
  console.log('🚀 Iniciando script de creación de automatización en Cursor...\n');

  const promptContent = getPromptContent();
  if (!promptContent) {
    console.error('❌ No se pudo leer el prompt desde:', PROMPT_FILE);
    process.exit(1);
  }
  console.log('✅ Prompt cargado (' + promptContent.length + ' caracteres)\n');

  // Crear directorio para estado del navegador
  const userDataDir = path.resolve(USER_DATA_DIR);
  fs.mkdirSync(userDataDir, { recursive: true });

  const browser = await chromium.launch({
    headless: false,
    slowMo: 100,
    args: ['--disable-blink-features=AutomationControlled'],
  });

  const storagePath = path.join(userDataDir, 'storage.json');
  const context = await browser.newContext({
    userAgent:
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 },
    storageState: fs.existsSync(storagePath) ? storagePath : undefined,
  });

  const page = await context.newPage();

  try {
    console.log('📄 Navegando a', CURSOR_AUTOMATIONS_URL);
    await page.goto(CURSOR_AUTOMATIONS_URL, { waitUntil: 'networkidle', timeout: 30000 });

    // Si hay redirección a login, pausar para que el usuario inicie sesión
    const url = page.url();
    if (url.includes('login') || url.includes('auth') || url.includes('signin')) {
      console.log('\n⚠️  Detectada página de login. Inicia sesión manualmente.');
      console.log('   Cuando llegues al dashboard de automations, el script continuará.\n');
      await page.waitForURL(/cursor\.com\/automations/, { timeout: 120000 });
    }

    // Guardar estado de sesión para futuras ejecuciones
    await context.storageState({ path: storagePath });

    console.log('🔍 Buscando botón "Create" o "New automation"...');
    const createSelectors = [
      'button:has-text("Create")',
      'button:has-text("New")',
      'a:has-text("Create")',
      '[data-testid*="create"]',
      'button:has-text("New automation")',
    ];

    let createClicked = false;
    for (const sel of createSelectors) {
      try {
        const btn = page.locator(sel).first();
        if ((await btn.count()) > 0 && (await btn.isVisible())) {
          await btn.click({ timeout: 5000 });
          createClicked = true;
          console.log('✅ Clic en crear automatización');
          break;
        }
      } catch {
        // Continuar con el siguiente selector
      }
    }

    if (!createClicked) {
      console.log('\n⚠️  No se encontró el botón de crear. Abriendo pausa para inspección manual.');
      await page.pause();
    }

    // Esperar a que aparezca el formulario o modal
    await page.waitForTimeout(2000);

    // Buscar trigger "Scheduled" (las alertas se obtienen vía MCP Datadog, no webhook)
    console.log('🔍 Buscando opción Scheduled como trigger...');
    const triggerSelectors = [
      'text=Scheduled',
      'button:has-text("Scheduled")',
      'text=Schedule',
      '[data-testid*="schedule"]',
      'text=Webhook',
      'button:has-text("Webhook")',
    ];
    for (const sel of triggerSelectors) {
      try {
        const el = page.locator(sel).first();
        if ((await el.count()) > 0 && (await el.isVisible())) {
          await el.click({ timeout: 3000 });
          console.log('✅ Trigger seleccionado (Scheduled preferido)');
          break;
        }
      } catch {
        // Continuar
      }
    }

    await page.waitForTimeout(1000);

    // Buscar textarea o campo de prompt
    console.log('🔍 Buscando campo de prompt...');
    const promptSelectors = [
      'textarea',
      '[contenteditable="true"]',
      '[role="textbox"]',
      '[data-testid*="prompt"]',
      '[placeholder*="prompt"]',
      '[placeholder*="instruction"]',
    ];

    let promptFilled = false;
    for (const sel of promptSelectors) {
      try {
        const el = page.locator(sel).first();
        if ((await el.count()) > 0 && (await el.isVisible())) {
          await el.click();
          await el.fill('');
          await el.fill(promptContent);
          promptFilled = true;
          console.log('✅ Prompt pegado en el campo');
          break;
        }
      } catch {
        // Continuar
      }
    }

    if (!promptFilled) {
      console.log('\n⚠️  No se encontró el campo de prompt. Usando portapapeles (Ctrl+V)...');
      await context.grantPermissions(['clipboard-read', 'clipboard-write']);
      await page.evaluate((text) => navigator.clipboard.writeText(text), promptContent);
      const mod = process.platform === 'darwin' ? 'Meta' : 'Control';
      await page.keyboard.press(`${mod}+v`);
    }

    await page.waitForTimeout(1500);

    // Buscar botón Save
    console.log('🔍 Buscando botón Save...');
    const saveSelectors = [
      'button:has-text("Save")',
      'button:has-text("Create")',
      'button:has-text("Guardar")',
      '[data-testid*="save"]',
    ];
    for (const sel of saveSelectors) {
      try {
        const btn = page.locator(sel).first();
        if ((await btn.count()) > 0 && (await btn.isVisible())) {
          await btn.click({ timeout: 3000 });
          console.log('✅ Guardado (o creación) solicitado');
          break;
        }
      } catch {
        // Continuar
      }
    }

    console.log('\n✅ Script completado. Revisa la página para confirmar que la automatización se creó.');
    console.log('   Usa trigger Scheduled (no Webhook). Las alertas se obtienen vía MCP Datadog.');
    console.log('   Ver: docs/runbook/automation-datadog-alert.md\n');

    // Mantener abierto 10 segundos para que el usuario vea el resultado
    await page.waitForTimeout(10000);
  } catch (err) {
    console.error('\n❌ Error:', err.message);
    console.log('\n💡 El script puede haber fallado por cambios en la UI de Cursor.');
    console.log('   Ejecuta con pausa para inspeccionar: añade page.pause() donde necesites.\n');
    await page.pause();
  } finally {
    await browser.close();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
