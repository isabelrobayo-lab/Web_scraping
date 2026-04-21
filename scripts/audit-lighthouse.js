/**
 * Auditoría de rendimiento con Lighthouse.
 * Usa PageSpeed Insights API (si hay API key) o Lighthouse CLI local.
 *
 * Uso:
 *   node scripts/audit-lighthouse.js [url1] [url2] ...
 *   GOOGLE_PAGESPEED_API_KEY=tu_key node scripts/audit-lighthouse.js [urls]
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const API_BASE = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed';
const { getWorkspaceRoot } = require('./workspace-root.js');

const OUTPUT_DIR = path.join(getWorkspaceRoot(), 'audit', 'lighthouse');
const STRATEGIES = ['mobile', 'desktop'];

const METRIC_IDS = [
  'first-contentful-paint',
  'largest-contentful-paint',
  'total-blocking-time',
  'cumulative-layout-shift',
  'speed-index',
  'interactive',
];

function parseArgs() {
  const args = process.argv.slice(2);
  let urls = [];
  let apiKey = process.env.GOOGLE_PAGESPEED_API_KEY;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--urls' && args[i + 1]) {
      urls = args[i + 1].split(',').map((u) => u.trim());
      i++;
    } else if (args[i] === '--key' && args[i + 1]) {
      apiKey = args[i + 1];
      i++;
    } else if (!args[i].startsWith('--') && args[i].startsWith('http')) {
      urls.push(args[i]);
    }
  }

  return { urls, apiKey };
}

async function runPageSpeed(url, strategy, apiKey) {
  const params = new URLSearchParams({
    url,
    strategy,
    category: 'PERFORMANCE',
  });
  if (apiKey) params.set('key', apiKey);

  const res = await fetch(`${API_BASE}?${params}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`PageSpeed API error ${res.status}: ${text.slice(0, 300)}`);
  }
  return res.json();
}

function runLighthouseCLI(url, strategy) {
  const tmpDir = path.join(OUTPUT_DIR, 'tmp');
  if (!fs.existsSync(tmpDir)) fs.mkdirSync(tmpDir, { recursive: true });
  const outPath = path.join(tmpDir, `lh-${Date.now()}-${strategy}.json`);

  const formFactor = strategy === 'mobile' ? 'mobile' : 'desktop';
  const screenEmulation = strategy === 'desktop' ? ' --screenEmulation.mobile=false' : '';
  const cmd = `npx lighthouse "${url}" --output=json --output-path="${outPath}" --only-categories=performance --form-factor=${formFactor}${screenEmulation} --chrome-flags="--headless --no-sandbox" --quiet`;
  execSync(cmd, { stdio: 'pipe', timeout: 120000 });

  const data = JSON.parse(fs.readFileSync(outPath, 'utf8'));
  try {
    fs.unlinkSync(outPath);
  } catch (_) {}

  return { lighthouseResult: data };
}

function extractMetrics(lighthouseResult) {
  const audits = lighthouseResult?.audits || {};
  const metrics = {};
  for (const id of METRIC_IDS) {
    const a = audits[id];
    if (a) {
      metrics[id] = {
        title: a.title,
        displayValue: a.displayValue,
        score: a.score,
        numericValue: a.numericValue,
      };
    }
  }
  return metrics;
}

function extractOpportunities(lighthouseResult) {
  const audits = lighthouseResult?.audits || {};
  const opportunities = [];

  for (const [id, audit] of Object.entries(audits)) {
    if (!audit || audit.score === null) continue;
    if (audit.score >= 1) continue;
    if (!audit.displayValue && !audit.description) continue;

    const item = {
      id,
      title: audit.title,
      description: audit.description,
      score: audit.score,
      displayValue: audit.displayValue,
    };

    if (audit.details?.overallSavingsMs) {
      item.savingsMs = audit.details.overallSavingsMs;
    }
    if (audit.details?.overallSavingsBytes) {
      item.savingsBytes = audit.details.overallSavingsBytes;
    }
    if (audit.details?.items?.length) {
      item.items = audit.details.items.slice(0, 5);
    }

    opportunities.push(item);
  }

  return opportunities.sort((a, b) => (a.score || 0) - (b.score || 0));
}

function scoreToPercent(score) {
  if (score === null || score === undefined) return 'N/A';
  return Math.round((score || 0) * 100);
}

async function auditUrl(url, apiKey) {
  const results = { url, strategies: {} };
  const useApi = !!apiKey;

  for (const strategy of STRATEGIES) {
    process.stdout.write(`  Analizando ${strategy}... `);
    try {
      const data = useApi
        ? await runPageSpeed(url, strategy, apiKey)
        : runLighthouseCLI(url, strategy);
      const lh = data.lighthouseResult;
      const perfCategory = lh?.categories?.performance;

      results.strategies[strategy] = {
        performanceScore: scoreToPercent(perfCategory?.score),
        metrics: extractMetrics(lh),
        opportunities: extractOpportunities(lh),
      };
      console.log(`Score: ${results.strategies[strategy].performanceScore}%`);
    } catch (err) {
      console.log(`Error: ${err.message}`);
      results.strategies[strategy] = { error: err.message };
    }
  }

  return results;
}

function generateMarkdownReport(report) {
  const lines = [
    '# Reporte Lighthouse - Mejoras de rendimiento',
    '',
    `**Fecha:** ${new Date().toISOString()}`,
    '',
    '## URLs analizadas',
    '',
  ];

  for (const result of report.results) {
    lines.push(`### ${result.url}`);
    lines.push('');

    for (const [strategy, data] of Object.entries(result.strategies)) {
      if (data.error) {
        lines.push(`- **${strategy}**: Error - ${data.error}`);
        continue;
      }

      lines.push(`#### ${strategy.toUpperCase()}`);
      lines.push(`- **Performance Score:** ${data.performanceScore}%`);
      lines.push('');

      lines.push('**Métricas principales:**');
      for (const [id, m] of Object.entries(data.metrics || {})) {
        lines.push(`- ${m.title}: ${m.displayValue || 'N/A'}`);
      }
      lines.push('');

      if (data.opportunities?.length) {
        lines.push('**Oportunidades de mejora:**');
        for (const opp of data.opportunities) {
          lines.push(`- **${opp.title}** (score: ${scoreToPercent(opp.score)}%)`);
          if (opp.displayValue) lines.push(`  - ${opp.displayValue}`);
          if (opp.savingsMs) lines.push(`  - Ahorro estimado: ${Math.round(opp.savingsMs)} ms`);
          if (opp.description) {
            const shortDesc = opp.description.replace(/\[.*?\]\(.*?\)/g, '').slice(0, 200);
            lines.push(`  - ${shortDesc}`);
          }
          lines.push('');
        }
      }
      lines.push('---');
      lines.push('');
    }
  }

  return lines.join('\n');
}

async function main() {
  const { urls, apiKey } = parseArgs();

  const targetUrls =
    urls.length > 0
      ? urls
      : [];

  if (targetUrls.length === 0) {
    console.error('No se proporcionaron URLs. Usa --url=<URL> o configura auditZones en platforms.json.');
    process.exit(1);
  }

  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const useApi = !!apiKey;
  console.log(useApi ? 'Auditoría Lighthouse - PageSpeed Insights API\n' : 'Auditoría Lighthouse - CLI local\n');
  console.log(`URLs a analizar: ${targetUrls.length}`);

  const report = {
    timestamp: new Date().toISOString(),
    results: [],
  };

  for (const url of targetUrls) {
    console.log(`\n${url}`);
    const result = await auditUrl(url, apiKey);
    report.results.push(result);
  }

  const jsonPath = path.join(OUTPUT_DIR, `lighthouse-${Date.now()}.json`);
  const mdPath = path.join(OUTPUT_DIR, `lighthouse-${Date.now()}.md`);

  fs.writeFileSync(jsonPath, JSON.stringify(report, null, 2), 'utf8');
  fs.writeFileSync(mdPath, generateMarkdownReport(report), 'utf8');

  console.log(`\nReportes guardados en:`);
  console.log(`  - ${jsonPath}`);
  console.log(`  - ${mdPath}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
