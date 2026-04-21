/**
 * Tests E2E para la página de reportes (reportes.html)
 * URL: https://carlospatinovelez19.github.io/prueba-agente-po/reportes.html
 */
const { test, expect } = require('@playwright/test');

const REPORTES_URL =
  process.env.REPORTES_BASE_URL ||
  'https://carlospatinovelez19.github.io/prueba-agente-po/reportes.html';

test.describe('Página de Reportes (reportes.html)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(REPORTES_URL);
  });

  test('carga correctamente con status 200', async ({ page }) => {
    const response = await page.goto(REPORTES_URL);
    expect(response?.status()).toBe(200);
  });

  test('muestra el título principal "Reportes del Proyecto"', async ({ page }) => {
    await expect(page.locator('h1')).toHaveText('Reportes del Proyecto');
  });

  test('muestra el enlace de navegación a Inicio', async ({ page }) => {
    const navLink = page.locator('a.nav-link, a[href*="index.html"]').first();
    await expect(navLink).toBeVisible();
    await expect(navLink).toContainText('Inicio');
  });

  test('muestra las tres tarjetas de reportes', async ({ page }) => {
    const cards = page.locator('.card');
    await expect(cards).toHaveCount(3);
  });

  test('la primera tarjeta enlaza al Reporte Ejecutivo principal', async ({ page }) => {
    const primaryCard = page.locator('.card.primary');
    await expect(primaryCard).toBeVisible();
    await expect(primaryCard).toHaveAttribute('href', /index\.html/);
    await expect(primaryCard.locator('h2')).toContainText('Reporte Ejecutivo');
  });

  test('la segunda tarjeta enlaza al reporte standalone', async ({ page }) => {
    const card = page.locator('.card').nth(1);
    await expect(card).toHaveAttribute('href', /reporte-ejecutivo-valor-proyecto\.html/);
  });

  test('la tercera tarjeta enlaza al análisis de ciclo', async ({ page }) => {
    const card = page.locator('.card').nth(2);
    await expect(card).toHaveAttribute('href', /analisis-ciclo-desarrollo\.html/);
    await expect(card.locator('h2')).toContainText('Análisis Ciclo de Desarrollo');
  });

  test('los estilos CSS cargan correctamente (body visible con layout)', async ({ page }) => {
    const body = page.locator('body');
    await expect(body).toBeVisible();
    const container = page.locator('.container');
    await expect(container).toBeVisible();
  });

  test('el enlace Inicio navega correctamente', async ({ page }) => {
    const navLink = page.locator('a[href*="index.html"]').first();
    await navLink.click();
    await expect(page).toHaveURL(/index\.html/);
  });

  test('tarjeta 1: navega a index.html y carga correctamente', async ({ page }) => {
    const card = page.locator('.card.primary');
    const [response] = await Promise.all([
      page.waitForNavigation(),
      card.click(),
    ]);
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/index\.html/);
    await expect(page.locator('body')).toBeVisible();
  });

  test('tarjeta 2: navega a reporte-ejecutivo-valor-proyecto.html y carga correctamente', async ({ page }) => {
    const card = page.locator('.card').nth(1);
    const [response] = await Promise.all([
      page.waitForNavigation(),
      card.click(),
    ]);
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/reporte-ejecutivo-valor-proyecto\.html/);
    await expect(page.locator('h1, .report-title')).toBeVisible();
  });

  test('tarjeta 3: navega a analisis-ciclo-desarrollo.html y carga correctamente', async ({ page }) => {
    const card = page.locator('.card').nth(2);
    const [response] = await Promise.all([
      page.waitForNavigation(),
      card.click(),
    ]);
    expect(response?.status()).toBeLessThan(400);
    await expect(page).toHaveURL(/analisis-ciclo-desarrollo\.html/);
    await expect(page.locator('h1, .report-title')).toBeVisible();
  });

  test('incluye selector de plataforma en el DOM', async ({ page }) => {
    await expect(page.locator('#platform-select')).toBeAttached();
  });
});
