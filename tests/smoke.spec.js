const { test, expect } = require('@playwright/test');
const { getSmokePaths } = require('../scripts/get-platform-config.js');

test.describe('Smoke tests E2E', () => {
  const paths = getSmokePaths();

  for (const path of paths) {
    const route = path || '/';
    test(`Ruta ${route} carga correctamente`, async ({ page }) => {
      const response = await page.goto(route);
      expect(response?.status()).toBeLessThan(500);
      await expect(page.locator('body')).toBeVisible();
    });
  }
});
