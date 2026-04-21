// @ts-check
const path = require('path');
const { defineConfig, devices } = require('@playwright/test');
const { getBaseUrl } = require('./scripts/get-platform-config.js');
const { getWorkspaceRoot } = require('./scripts/workspace-root.js');

const baseURL = getBaseUrl() || process.env.BASE_URL || 'https://example.com';
const playwrightDir = path.join(getWorkspaceRoot(), 'playwright');
const outputDir = path.relative(__dirname, path.join(playwrightDir, 'test-results')) || '.';
const reportFolder =
  path.relative(__dirname, path.join(playwrightDir, 'playwright-report')) || '.';

module.exports = defineConfig({
  testDir: './tests',
  testIgnore: ['**/unit/**'],
  timeout: 30000,
  retries: process.env.CI ? 1 : 0,
  outputDir,
  reporter:
    process.env.CI
      ? 'github'
      : [['list'], ['html', { outputFolder: reportFolder }]],
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      // Debe incluir **/unit/**: si solo se ignora miniverse, se pierde el ignore raíz y Vitest (*.test.js) choca con expect de Playwright.
      testIgnore: ['**/miniverse.spec.js', '**/unit/**'],
    },
    {
      name: 'miniverse',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: process.env.MINIVERSE_BASE_URL || 'http://localhost:5173',
      },
      testMatch: '**/miniverse.spec.js',
    },
  ],
});
