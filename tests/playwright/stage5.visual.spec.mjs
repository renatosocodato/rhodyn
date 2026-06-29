import { expect, test } from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const FIXTURE_DIR = path.join(ROOT, 'api/stage4/fixtures');
const COMPARISON_SCREENSHOT_OPTIONS = { maxDiffPixelRatio: 0.05 };

const RUN_FIXTURES = {
  validate: 'validate_trajectory_upload_run.response.json',
  score_residence: 'score_residence_upload_run.response.json',
  decide_coupling: 'decide_coupling_upload_run.response.json',
  summarize_reserve: 'summarize_reserve_upload_run.response.json',
  compare_models: 'compare_models_upload_run.response.json',
  export_markdown: 'export_markdown_upload_run.response.json',
};

async function fixtureBody(name) {
  const payload = JSON.parse(await fs.readFile(path.join(FIXTURE_DIR, name), 'utf8'));
  return { body: payload.body ?? payload, status: payload.status_code ?? 200 };
}

function jsonResponse(body, status = 200) {
  return { status, contentType: 'application/json', body: JSON.stringify(body) };
}

async function mockStage4Api(page, overrides = {}) {
  await page.route('http://127.0.0.1:8000/health', async (route) => {
    const payload = await fixtureBody('health.response.json');
    await route.fulfill(jsonResponse(payload.body, payload.status));
  });

  await page.route(/http:\/\/127\.0\.0\.1:8000\/jobs\/upload\/run.*/, async (route) => {
    const url = new URL(route.request().url());
    const operation = url.searchParams.get('operation') || '';
    const override = overrides[operation];
    if (override) {
      await route.fulfill(jsonResponse(override));
      return;
    }
    const fixture = RUN_FIXTURES[operation];
    if (!fixture) {
      await route.fulfill(jsonResponse({ status: 'error', error: `unhandled operation ${operation}` }, 404));
      return;
    }
    const payload = await fixtureBody(fixture);
    await route.fulfill(jsonResponse(payload.body, payload.status));
  });

  await page.route(/http:\/\/127\.0\.0\.1:8000\/jobs\/upload\/submit.*/, async (route) => {
    const url = new URL(route.request().url());
    const operation = url.searchParams.get('operation') || 'unknown';
    await route.fulfill(jsonResponse({ status: 'pass', stored_job: { job_id: `mock-${operation}`, operation } }));
  });

  await page.route(/http:\/\/127\.0\.0\.1:8000\/jobs\/upload\/bundle.*/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/zip',
      headers: { 'x-rhodyn-bundle-sha256': 'mocked-stage5-browser-regression' },
      body: 'stage5 mocked bundle',
    });
  });
}

async function openWorkbench(page, overrides) {
  await mockStage4Api(page, overrides);
  await page.goto('/frontend/stage5/');
  await expect(page.locator('#contractBadge')).toHaveText('Stage 4 contract loaded');
}

async function runOperation(page, operationId) {
  await page.locator('#operationSelect').selectOption(operationId);
  await page.getByRole('button', { name: 'Load example' }).click();
  await expect(page.locator('#validationState')).toContainText('passed');
  await expect(page.locator('#rowCount')).not.toHaveValue('');
  await page.locator('#runButton').click();
  const suite = page.locator('#resultVisual .comparison-suite');
  await expect(suite).toBeVisible();
  await expect(page.locator('#resultPanel')).toContainText('"status": "pass"');
  return suite;
}

async function expectNoUnsafeText(locator) {
  const text = await locator.innerText();
  expect(text).not.toMatch(/undefined|NaN|Infinity/);
  expect(text).not.toContain('no effect');
  expect(text).not.toContain('proves zero coupling');
}

async function expectNoDocumentOverflow(page) {
  const overflow = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth + 2);
}

const comparisonCases = [
  {
    operationId: 'score_residence',
    title: 'Residence-window comparison',
    text: ['Mean residence', 'Residence time', 'Residence summaries are derived'],
    snapshot: 'stage5-residence-comparison.png',
  },
  {
    operationId: 'decide_coupling',
    title: 'Bounded-coupling comparison',
    text: ['Inside margin', 'Zero coupling', 'not absence of all coupling'],
    snapshot: 'stage5-coupling-comparison.png',
  },
  {
    operationId: 'summarize_reserve',
    title: 'Reserve-buffering comparison',
    text: ['Mean reserve', 'Peak', 'not a direct measurement'],
    snapshot: 'stage5-reserve-comparison.png',
  },
  {
    operationId: 'compare_models',
    title: 'Reduced-architecture ranking',
    text: ['Delta BIC', 'Best model', 'does not identify every molecular edge'],
    snapshot: 'stage5-model-comparison.png',
  },
];

test.describe('Stage 5 comparison-suite screenshots', () => {
  for (const item of comparisonCases) {
    test(`${item.operationId} renders a stable comparison panel`, async ({ page }) => {
      await openWorkbench(page);
      const suite = await runOperation(page, item.operationId);
      await expect(suite.locator('h3')).toHaveText(item.title);
      for (const token of item.text) await expect(suite).toContainText(token);
      await expectNoUnsafeText(suite);
      await expectNoDocumentOverflow(page);
      await expect(suite).toHaveScreenshot(item.snapshot, COMPARISON_SCREENSHOT_OPTIONS);
    });
  }
});


test('navigation and action states stay coherent after polish', async ({ page }) => {
  await openWorkbench(page);
  await expect(page.getByRole('link', { name: 'Dashboard' })).toHaveAttribute('aria-current', 'page');
  await expect(page.locator('#runButton')).toBeDisabled();
  await expect(page.locator('#jobState')).toHaveText('no job submitted');
  await expect(page.locator('#resultPanel')).not.toContainText('simulate_controller_local');

  await page.getByRole('link', { name: 'Simulation' }).click();
  await expect(page.getByRole('link', { name: 'Simulation' })).toHaveAttribute('aria-current', 'page');
  await page.locator('#simulationPinButton').click();
  await expect(page.locator('#jobState')).toContainText('simulation pinned');
  await expect(page.locator('#resultVisual')).toContainText('Simulation preview');
  await expect(page.locator('#resultPanel')).toContainText('simulate_controller_local');
  await expectNoUnsafeText(page.locator('#simulation'));
  await expectNoDocumentOverflow(page);
});

test('operation-specific panels accept polished results', async ({ page }) => {
  await openWorkbench(page);
  await page.getByRole('link', { name: 'Residence' }).click();
  await expect(page.locator('#residenceVisual')).toContainText('Residence output waiting');
  await page.locator('[data-operation-jump="score_residence"]').click();
  await expect(page.locator('#operationSelect')).toHaveValue('score_residence');
  await expect(page.locator('#runButton')).toBeDisabled();
  await page.getByRole('button', { name: 'Load example' }).click();
  await expect(page.locator('#runButton')).toBeEnabled();
  await page.locator('#runButton').click();
  await expect(page.locator('#residenceVisual .comparison-suite')).toBeVisible();
  await expect(page.locator('#residenceVisual')).toContainText('Residence-window comparison');
  await expect(page.locator('#residenceSummary')).toContainText('"status": "pass"');
  await expectNoUnsafeText(page.locator('#residenceVisual'));
  await expectNoDocumentOverflow(page);
});

test('simulation workbench mirrors the deterministic controller and stays readable', async ({ page }) => {
  await openWorkbench(page);
  await page.getByRole('link', { name: 'Simulation' }).click();
  const section = page.locator('#simulation');
  await expect(section).toContainText('Simulation workbench');
  await expect(section).toContainText('Residence fraction');
  await expect(section).toContainText('Peak burden');
  await expect(section).toContainText('First passage');
  await expect(section).toContainText('rhodyn simulate');
  const reference = await page.evaluate(() => {
    const api = window.__RHODYN_STAGE5_SIM__;
    const rows = api.simulateControllerLocal({ ...api.SIMULATION_DEFAULTS });
    return { length: rows.length, first: rows[0], middle: rows[20], final: rows[40] };
  });
  expect(reference.length).toBe(41);
  expect(reference.first.window_gate).toBeCloseTo(0.8786191987, 9);
  expect(reference.middle.src).toBeCloseTo(0.6484494667, 9);
  expect(reference.final.burden).toBeCloseTo(0.7990020641, 9);
  await page.locator('#simulationPreset').selectOption('buffered_window');
  await expect(page.locator('#simulationState')).toContainText('Buffered window');
  await expectNoUnsafeText(section);
  await expectNoDocumentOverflow(page);
  if (process.platform === 'darwin') {
    await expect(section).toHaveScreenshot('stage5-simulation-workbench.png');
  }
});

test('public trajectory workflow remains visually usable', async ({ page }) => {
  await openWorkbench(page);
  await page.getByRole('button', { name: 'Load MLCI workflow' }).click();
  await expect(page.locator('#trajectoryState')).toContainText('rows');
  await expect(page.locator('#trajectoryStats')).toContainText('Traces');
  await expect(page.locator('#trajectoryStats')).toContainText('Window');
  await expect(page.locator('#traceSummaryTable')).toContainText('Residence fraction');
  await expectNoDocumentOverflow(page);
  await expect(page.locator('#trajectory')).toHaveScreenshot('stage5-public-trajectory-workflow.png');
});

test('adversarial coupling labels remain bounded and do not inflate the biology', async ({ page }) => {
  const longContrast = 'very_long_public_ligand_batch_with_extreme_replicate_label_and_margin_boundary_check';
  await openWorkbench(page, {
    decide_coupling: {
      status: 'pass',
      job: {
        input_rows: 2,
        job_id: 'mock-adversarial-coupling',
        kind: 'coupling',
        operation: 'decide_coupling',
        parameters: { rope_threshold: 0.95 },
        software_version: '0.1.0',
      },
      records: [
        { contrast: longContrast, estimate: 0.0004, ci_low: -0.1995, ci_high: 0.1994, margin: 0.2, rope_mass: 0.951 },
        { contrast: `${longContrast}_outside`, estimate: 0.16, ci_low: -0.03, ci_high: 0.245, margin: 0.2, rope_mass: 0.8 },
      ],
      decisions: [
        { estimate: 0.0004, ci_low: -0.1995, ci_high: 0.1994, margin: 0.2, passes: true, rope_mass: 0.951, rope_threshold: 0.95, interval_inside_margin: true },
        { estimate: 0.16, ci_low: -0.03, ci_high: 0.245, margin: 0.2, passes: false, rope_mass: 0.8, rope_threshold: 0.95, interval_inside_margin: false },
      ],
      typed_results: [],
    },
  });
  const suite = await runOperation(page, 'decide_coupling');
  await expect(suite).toContainText('inside');
  await expect(suite).toContainText('outside');
  await expect(suite).toContainText('Zero coupling');
  await expect(suite).toContainText('not claimed');
  await expectNoUnsafeText(suite);
  await expectNoDocumentOverflow(page);
  await expect(suite).toHaveScreenshot('stage5-adversarial-coupling.png', COMPARISON_SCREENSHOT_OPTIONS);
});
