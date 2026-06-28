const CONTRACT_URL = "../../api/stage4/frontend_contract.json";
const OPENAPI_URL = "../../api/stage4/openapi.json";
const SCHEMA_FIXTURE_URL = "../../api/stage4/fixtures/schemas.response.json";
const PUBLIC_WORKFLOW = {
  operation_id: "score_residence",
  csv: "../../examples/mlci_public_intensity_trajectory.csv",
  label: "MLCI public intensity trajectory",
  source: "Zenodo 7260137-derived MLCI tracking subset",
  parameters: { low: 13.0, high: 14.5, signal_column: "signal" }
};

const state = {
  contract: null,
  openapi: null,
  schemas: {},
  rows: [],
  csvText: "",
  loadedSource: "",
  operation: null,
  lastResult: null,
  lastJob: null
};

const $ = (id) => document.getElementById(id);

function headers() {
  const key = $("apiKey").value.trim();
  return key ? { "x-rhodyn-api-key": key } : {};
}

function apiBase() {
  return $("apiBase").value.replace(/\/$/, "");
}

function operationById(id) {
  return state.contract.operations.find((item) => item.operation_id === id);
}

function schemaForOperation(operation) {
  return state.schemas[operation.table_kind] || null;
}

function inferParameterType(value) {
  if (typeof value === "boolean") return "boolean";
  if (typeof value === "number") return "number";
  return "text";
}

function fmt(value, digits = 3) {
  return Number.isFinite(value) ? value.toFixed(digits) : "-";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function compactJson(value) {
  return JSON.stringify(value, null, 2);
}

function flattenValue(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function resultOperation(payload = state.lastResult) {
  return payload?.job?.operation || state.operation?.upload_operation || "";
}

function resultRows(payload = state.lastResult) {
  if (!payload) return [];
  for (const key of ["summaries", "fits", "decisions", "records", "typed_results"]) {
    if (Array.isArray(payload[key])) return payload[key];
  }
  if (payload.typed_result && typeof payload.typed_result === "object") return [payload.typed_result];
  if (payload.markdown) return [{ markdown: payload.markdown }];
  return [{ status: payload.status || "", operation: resultOperation(payload) }];
}

function rowsToCsv(rows) {
  if (!rows.length) return "";
  const fields = [];
  rows.forEach((row) => Object.keys(row).forEach((key) => { if (!fields.includes(key)) fields.push(key); }));
  const quote = (value) => {
    const text = flattenValue(value);
    return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
  };
  return [fields.join(","), ...rows.map((row) => fields.map((field) => quote(row[field])).join(","))].join("\n") + "\n";
}

function rowsToMarkdown(title, rows) {
  if (!rows.length) return `# ${title}\n\nNo rows.\n`;
  const fields = [];
  rows.forEach((row) => Object.keys(row).forEach((key) => { if (!fields.includes(key)) fields.push(key); }));
  const header = `| ${fields.join(" | ")} |`;
  const sep = `| ${fields.map(() => "---").join(" | ")} |`;
  const body = rows.map((row) => `| ${fields.map((field) => flattenValue(row[field]).replaceAll("|", "\\|")).join(" | ")} |`);
  return [`# ${title}`, "", header, sep, ...body, ""].join("\n");
}

function downloadText(filename, text, mimeType) {
  const blob = new Blob([text], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function resultFilename(extension) {
  const operation = resultOperation() || "result";
  const job = state.lastResult?.job?.job_id || "preview";
  return `rhodyn_${operation}_${job}.${extension}`;
}

function resultMarkdown() {
  if (!state.lastResult) return "# RhoDyn result\n\nNo result is loaded.\n";
  if (state.lastResult.markdown) return state.lastResult.markdown;
  const operation = resultOperation();
  const job = state.lastResult.job || {};
  const rows = resultRows();
  const table = rowsToMarkdown(`RhoDyn ${operation} result`, rows);
  return [
    table.trimEnd(),
    "",
    "## Parameter provenance",
    "",
    `Operation: \`${operation}\``,
    `Job ID: \`${job.job_id || ""}\``,
    `Software version: \`${job.software_version || ""}\``,
    "",
    "```json",
    compactJson(job.parameters || currentParameters()),
    "```",
    "",
    "Results are scoped to the submitted rows and declared parameters."
  ].join("\n") + "\n";
}

function renderOperationMeta(operation) {
  $("operationMeta").innerHTML = `
    <div><span>Operation</span><strong>${operation.upload_operation}</strong></div>
    <div><span>Table kind</span><strong>${operation.table_kind}</strong></div>
    <div><span>Run route</span><code>${operation.endpoint}</code></div>
    <div><span>Submit route</span><code>${operation.submit_endpoint}</code></div>
    <div><span>Bundle route</span><code>${operation.bundle_endpoint}</code></div>
    <div class="wide"><span>Boundary</span><p>${operation.biological_boundary}</p></div>
  `;
}

function renderSchemaInspection(operation) {
  const schema = schemaForOperation(operation);
  if (!schema) {
    $("schemaPanel").innerHTML = "<strong>Accepted table</strong><p>Any CSV with a header row can be summarized for this report operation.</p>";
    return;
  }
  $("schemaPanel").innerHTML = `
    <strong>${schema.name} schema</strong>
    <div><span>Required</span>${schema.required.map((field) => `<code>${field}</code>`).join(" ")}</div>
    <div><span>Optional</span>${schema.optional.length ? schema.optional.map((field) => `<code>${field}</code>`).join(" ") : "none"}</div>
  `;
}

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  if (!lines.length) return [];
  const fields = lines[0].split(",").map((item) => item.trim());
  return lines.slice(1).filter(Boolean).map((line) => {
    const values = line.split(",");
    const row = {};
    fields.forEach((field, index) => { row[field] = values[index] ?? ""; });
    return row;
  });
}

function renderTable(rows) {
  if (!rows.length) {
    $("tablePreview").innerHTML = "";
    return;
  }
  const fields = Object.keys(rows[0]);
  const visible = rows.slice(0, 80);
  $("tablePreview").innerHTML = `<table><thead><tr>${fields.map((field) => `<th>${field}</th>`).join("")}</tr></thead><tbody>${visible.map((row) => `<tr>${fields.map((field) => `<td>${row[field] ?? ""}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}

function currentSignalColumn() {
  const params = currentParameters();
  return params.signal_column || "signal";
}

function groupTrajectoryRows(rows, signalColumn) {
  const grouped = new Map();
  for (const row of rows) {
    const time = Number(row.time);
    const signal = Number(row[signalColumn]);
    if (!Number.isFinite(time) || !Number.isFinite(signal)) continue;
    const id = row.cell_id || row.sample_id || row.condition || "series";
    if (!grouped.has(id)) grouped.set(id, { id, condition: row.condition || "", replicate: row.replicate || "", points: [] });
    grouped.get(id).points.push({ time, signal });
  }
  for (const group of grouped.values()) {
    group.points.sort((a, b) => a.time - b.time);
  }
  return Array.from(grouped.values()).filter((group) => group.points.length);
}

function residenceForPoints(points, low, high) {
  if (!points.length) return { residenceFraction: 0, residenceTime: 0, totalTime: 0, segmentCount: 0 };
  const inside = (value) => Number.isFinite(low) && Number.isFinite(high) && low <= value && value <= high;
  if (points.length === 1) {
    const residenceFraction = inside(points[0].signal) ? 1 : 0;
    return { residenceFraction, residenceTime: residenceFraction, totalTime: 1, segmentCount: residenceFraction ? 1 : 0 };
  }
  let totalTime = 0;
  let residenceTime = 0;
  let segmentCount = 0;
  let wasInside = false;
  for (let index = 0; index < points.length - 1; index += 1) {
    const pointInside = inside(points[index].signal);
    const dt = Math.max(0, points[index + 1].time - points[index].time);
    totalTime += dt;
    if (pointInside) residenceTime += dt;
    if (pointInside && !wasInside) segmentCount += 1;
    wasInside = pointInside;
  }
  if (inside(points[points.length - 1].signal) && !wasInside) segmentCount += 1;
  const fallbackFraction = points.filter((point) => inside(point.signal)).length / points.length;
  return totalTime > 0
    ? { residenceFraction: residenceTime / totalTime, residenceTime, totalTime, segmentCount }
    : { residenceFraction: fallbackFraction, residenceTime: fallbackFraction, totalTime: 1, segmentCount };
}

function trajectoryInspection(rows) {
  const signalColumn = currentSignalColumn();
  const groups = groupTrajectoryRows(rows, signalColumn);
  const points = groups.flatMap((group) => group.points);
  const conditions = new Set(rows.map((row) => row.condition).filter(Boolean));
  const replicates = new Set(rows.map((row) => row.replicate).filter(Boolean));
  const params = currentParameters();
  const low = Number(params.low);
  const high = Number(params.high);
  const summaries = groups.map((group) => {
    const values = group.points.map((point) => point.signal);
    const residence = residenceForPoints(group.points, low, high);
    return {
      ...group,
      nPoints: group.points.length,
      minSignal: Math.min(...values),
      maxSignal: Math.max(...values),
      meanSignal: values.reduce((total, value) => total + value, 0) / values.length,
      ...residence
    };
  }).sort((a, b) => b.residenceFraction - a.residenceFraction || b.maxSignal - a.maxSignal);
  return {
    signalColumn,
    groups,
    summaries,
    conditions,
    replicates,
    points,
    minTime: points.length ? Math.min(...points.map((point) => point.time)) : NaN,
    maxTime: points.length ? Math.max(...points.map((point) => point.time)) : NaN,
    minSignal: points.length ? Math.min(...points.map((point) => point.signal)) : NaN,
    maxSignal: points.length ? Math.max(...points.map((point) => point.signal)) : NaN,
    low,
    high
  };
}

function renderTrajectoryStats(summary) {
  if (!summary.points.length) {
    $("trajectoryStats").innerHTML = "";
    $("traceSummaryTable").innerHTML = "";
    return;
  }
  const source = state.loadedSource ? `<div><span>Source</span><strong>${escapeHtml(state.loadedSource)}</strong></div>` : "";
  $("trajectoryStats").innerHTML = `
    ${source}
    <div><span>Signal</span><strong>${escapeHtml(summary.signalColumn)}</strong></div>
    <div><span>Rows</span><strong>${state.rows.length}</strong></div>
    <div><span>Traces</span><strong>${summary.groups.length}</strong></div>
    <div><span>Conditions</span><strong>${summary.conditions.size || "-"}</strong></div>
    <div><span>Replicates</span><strong>${summary.replicates.size || "-"}</strong></div>
    <div><span>Time range</span><strong>${fmt(summary.minTime)} to ${fmt(summary.maxTime)}</strong></div>
    <div><span>Signal range</span><strong>${fmt(summary.minSignal)} to ${fmt(summary.maxSignal)}</strong></div>
    <div><span>Window</span><strong>${fmt(summary.low)} to ${fmt(summary.high)}</strong></div>
  `;
  const visible = summary.summaries.slice(0, 10);
  $("traceSummaryTable").innerHTML = `
    <table>
      <thead><tr><th>Trace</th><th>Condition</th><th>Replicate</th><th>Points</th><th>Mean</th><th>Max</th><th>Residence fraction</th><th>Residence time</th><th>Segments</th></tr></thead>
      <tbody>${visible.map((row) => `<tr><td>${escapeHtml(row.id)}</td><td>${escapeHtml(row.condition)}</td><td>${escapeHtml(row.replicate)}</td><td>${row.nPoints}</td><td>${fmt(row.meanSignal)}</td><td>${fmt(row.maxSignal)}</td><td>${fmt(row.residenceFraction)}</td><td>${fmt(row.residenceTime)}</td><td>${row.segmentCount}</td></tr>`).join("")}</tbody>
    </table>
  `;
}

function renderTrajectory(rows) {
  const svg = $("trajectoryPlot");
  svg.innerHTML = "";
  const signalColumn = currentSignalColumn();
  if (!rows.length || !("time" in rows[0]) || !(signalColumn in rows[0])) {
    $("trajectoryState").textContent = rows.length ? `CSV loaded; no time/${signalColumn} columns` : "waiting for CSV";
    $("trajectoryStats").innerHTML = "";
    $("traceSummaryTable").innerHTML = "";
    return;
  }
  const inspection = trajectoryInspection(rows);
  renderTrajectoryStats(inspection);
  const series = inspection.groups.slice(0, 12).map((group) => group.points);
  const all = series.flat();
  if (!all.length) return;
  const minT = inspection.minTime;
  const maxT = inspection.maxTime;
  const minY = inspection.minSignal;
  const maxY = inspection.maxSignal;
  const x = (value) => 56 + ((value - minT) / Math.max(maxT - minT, 1)) * 790;
  const y = (value) => 276 - ((value - minY) / Math.max(maxY - minY, 1)) * 230;
  svg.insertAdjacentHTML("beforeend", `<line class="axis" x1="56" y1="276" x2="846" y2="276"></line><line class="axis" x1="56" y1="46" x2="56" y2="276"></line>`);
  const op = state.operation;
  const params = currentParameters();
  if (op && "low" in params && "high" in params) {
    const yHigh = y(Number(params.high));
    const yLow = y(Number(params.low));
    svg.insertAdjacentHTML("beforeend", `<rect class="window-band" x="56" y="${Math.min(yHigh, yLow)}" width="790" height="${Math.abs(yHigh - yLow)}"></rect>`);
  }
  series.forEach((items, index) => {
    const points = items.map((item) => `${x(item.time).toFixed(1)},${y(item.signal).toFixed(1)}`).join(" ");
    svg.insertAdjacentHTML("beforeend", `<polyline class="trace ${index % 2 ? "trace-b" : "trace-a"}" points="${points}"></polyline>`);
  });
  $("trajectoryState").textContent = `${rows.length} rows, ${inspection.groups.length} traces, ${series.length} displayed`;
}

function renderParameters(operation) {
  state.operation = operation;
  $("tableKind").value = operation.table_kind;
  renderOperationMeta(operation);
  renderSchemaInspection(operation);
  const fields = Object.entries(operation.parameters || {});
  $("parameterPanel").innerHTML = fields.map(([key, value]) => {
    const type = inferParameterType(value);
    if (type === "boolean") {
      return `<label>${key}<input data-param="${key}" type="checkbox" ${value ? "checked" : ""}><small>${type}</small></label>`;
    }
    return `<label>${key}<input data-param="${key}" type="${type === "number" ? "number" : "text"}" value="${value}"><small>${type}</small></label>`;
  }).join("");
  renderParameterPayload();
  renderTrajectory(state.rows);
  updateValidationState();
}

function currentParameters() {
  const params = {};
  document.querySelectorAll("[data-param]").forEach((input) => {
    if (input.type === "checkbox") {
      params[input.dataset.param] = input.checked;
      return;
    }
    const raw = input.value;
    const number = Number(raw);
    params[input.dataset.param] = raw === "true" ? true : raw === "false" ? false : Number.isFinite(number) && raw.trim() !== "" ? number : raw;
  });
  return params;
}

function routeUrl(endpoint, operation, params) {
  const query = new URLSearchParams({ operation: operation.upload_operation, parameters_json: JSON.stringify(params) });
  return `${apiBase()}${endpoint}?${query.toString()}`;
}

function renderParameterPayload() {
  if (!state.operation) return;
  const params = currentParameters();
  $("parameterPayload").textContent = JSON.stringify(params, null, 2);
  $("routePanel").textContent = routeUrl(state.operation.endpoint, state.operation, params);
}

function setParameterValues(values) {
  for (const [key, value] of Object.entries(values)) {
    const input = document.querySelector(`[data-param="${key}"]`);
    if (!input) continue;
    if (input.type === "checkbox") input.checked = Boolean(value);
    else input.value = value;
  }
  renderParameterPayload();
  renderTrajectory(state.rows);
  updateValidationState();
}

function localValidationIssues() {
  if (!state.operation) return ["No operation selected."];
  if (!state.csvText.trim()) return ["Load a CSV table before running an operation."];
  if (!state.rows.length) return ["CSV table has no data rows."];
  const schema = schemaForOperation(state.operation);
  if (!schema) return [];
  const fields = new Set(Object.keys(state.rows[0] || {}));
  return schema.required.filter((field) => !fields.has(field)).map((field) => `Missing required column: ${field}`);
}

function updateValidationState() {
  const issues = localValidationIssues();
  $("validationState").className = issues.length ? "status-bad" : "status-good";
  $("validationState").textContent = issues.length ? issues.join("; ") : "Local schema check passed for the selected operation.";
}

function card(label, value, detail = "") {
  return `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong>${detail ? `<p>${escapeHtml(detail)}</p>` : ""}</div>`;
}

function barRows(rows, valueField, labelField, { lowerIsBetter = false, maxRows = 12 } = {}) {
  const visible = rows.slice(0, maxRows);
  const values = visible.map((row) => Number(row[valueField])).filter(Number.isFinite);
  if (!values.length) return "";
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = Math.max(max - min, Math.abs(max), 1);
  return `<div class="bar-list">${visible.map((row) => {
    const value = Number(row[valueField]);
    const width = lowerIsBetter ? ((max - value) / span) * 100 : (Math.abs(value) / Math.max(...values.map(Math.abs), 1)) * 100;
    return `<div class="bar-row"><span>${escapeHtml(row[labelField] ?? "")}</span><div><i style="width:${Math.max(4, Math.min(100, width)).toFixed(1)}%"></i></div><strong>${fmt(value)}</strong></div>`;
  }).join("")}</div>`;
}

function intervalRows(records, decisions) {
  if (!records.length || !decisions.length) return "";
  const rows = records.map((record, index) => ({ ...record, ...(decisions[index] || {}) }));
  return `<div class="interval-list">${rows.map((row) => {
    const margin = Math.max(Math.abs(Number(row.margin)), 1e-9);
    const left = Math.max(0, Math.min(100, ((Number(row.ci_low) + margin) / (2 * margin)) * 100));
    const right = Math.max(0, Math.min(100, ((Number(row.ci_high) + margin) / (2 * margin)) * 100));
    const estimate = Math.max(0, Math.min(100, ((Number(row.estimate) + margin) / (2 * margin)) * 100));
    return `<div class="interval-row"><span>${escapeHtml(row.contrast || "")}</span><div><b style="left:${left.toFixed(1)}%;width:${Math.max(1, right - left).toFixed(1)}%"></b><i style="left:${estimate.toFixed(1)}%"></i></div><strong>${row.passes ? "inside" : "outside"}</strong></div>`;
  }).join("")}</div>`;
}

function renderResultVisual(payload) {
  if (!payload) {
    $("resultVisual").innerHTML = "";
    return;
  }
  const operation = resultOperation(payload);
  const job = payload.job || {};
  const rows = resultRows(payload);
  const cards = [
    card("Operation", operation || "-"),
    card("Status", payload.status || "-"),
    card("Rows", String(job.input_rows ?? rows.length)),
    card("Job", job.job_id || "not stored")
  ];
  let detail = "";
  if (operation === "score_residence") {
    const summaries = payload.summaries || [];
    const meanResidence = summaries.length ? summaries.reduce((total, row) => total + Number(row.residence_fraction || 0), 0) / summaries.length : NaN;
    cards.push(card("Traces", String(summaries.length)), card("Mean residence", fmt(meanResidence)));
    detail = barRows(summaries, "residence_fraction", "cell_id");
  } else if (operation === "decide_coupling") {
    const decisions = payload.decisions || [];
    const passing = decisions.filter((row) => row.passes).length;
    cards.push(card("Contrasts", String(decisions.length)), card("Inside margin", `${passing}/${decisions.length}`));
    detail = intervalRows(payload.records || [], decisions);
  } else if (operation === "summarize_reserve") {
    const summaries = payload.summaries || [];
    const meanReserve = summaries.length ? summaries.reduce((total, row) => total + Number(row.reserve || 0), 0) / summaries.length : NaN;
    cards.push(card("Samples", String(summaries.length)), card("Mean reserve", fmt(meanReserve)));
    detail = barRows(summaries, "reserve", "sample_id");
  } else if (operation === "compare_models") {
    const fits = payload.fits || [];
    const best = fits[0] || {};
    cards.push(card("Models", String(fits.length)), card("Best model", best.model || "-"), card("Best BIC", fmt(Number(best.bic))));
    detail = barRows(fits, "bic", "model", { lowerIsBetter: true });
  } else if (operation === "validate") {
    const issues = payload.issues || [];
    cards.push(card("Schema", payload.kind || "-"), card("Issues", String(issues.length)));
    detail = issues.length ? `<pre class="markdown-preview">${escapeHtml(rowsToMarkdown("Validation issues", issues))}</pre>` : "<p class=\"result-note\">Schema validation passed for the submitted rows.</p>";
  } else if (operation === "export_markdown") {
    detail = `<pre class="markdown-preview">${escapeHtml(payload.markdown || "")}</pre>`;
  }
  $("resultVisual").innerHTML = `
    <div class="result-cards">${cards.join("")}</div>
    ${detail ? `<div class="result-chart">${detail}</div>` : ""}
  `;
}

function assignResult(payload) {
  state.lastResult = payload;
  const text = compactJson(payload);
  $("resultPanel").textContent = text;
  renderResultVisual(payload);
  $("residenceSummary").textContent = operationById("score_residence") === state.operation ? text : $("residenceSummary").textContent;
  $("couplingSummary").textContent = operationById("decide_coupling") === state.operation ? text : $("couplingSummary").textContent;
  $("reserveSummary").textContent = operationById("summarize_reserve") === state.operation ? text : $("reserveSummary").textContent;
  $("modelSummary").textContent = operationById("compare_models") === state.operation ? text : $("modelSummary").textContent;
}

async function loadCsvFromPath(path, label) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Could not load ${path}`);
  state.csvText = await response.text();
  state.rows = parseCsv(state.csvText);
  state.loadedSource = label || path;
  $("rowCount").value = state.rows.length;
  $("csvFile").value = "";
  renderTable(state.rows);
  renderTrajectory(state.rows);
  updateValidationState();
}

async function loadContract() {
  const [contractResponse, openapiResponse, schemaResponse] = await Promise.all([fetch(CONTRACT_URL), fetch(OPENAPI_URL), fetch(SCHEMA_FIXTURE_URL)]);
  state.contract = await contractResponse.json();
  state.openapi = await openapiResponse.json();
  const schemaPayload = await schemaResponse.json();
  state.schemas = schemaPayload.body?.schemas || {};
  $("contractVersion").textContent = state.contract.contract_version;
  $("operationCount").textContent = state.contract.operations.length;
  $("screenCount").textContent = state.contract.screens.length;
  $("contractBadge").textContent = "Stage 4 contract loaded";
  $("operationSelect").innerHTML = state.contract.operations.map((operation) => `<option value="${operation.operation_id}">${operation.label}</option>`).join("");
  renderParameters(state.contract.operations[0]);
}

async function checkHealth() {
  const response = await fetch(`${apiBase()}/health`);
  const payload = await response.json();
  $("healthState").textContent = `${payload.status}; version ${payload.software_version}`;
}

async function loadExampleCsv() {
  if (!state.operation?.example_csv) throw new Error("No example CSV is declared for this operation.");
  await loadCsvFromPath(`../../${state.operation.example_csv}`, state.operation.example_csv);
}

async function loadPublicWorkflow() {
  renderParameters(operationById(PUBLIC_WORKFLOW.operation_id));
  setParameterValues(PUBLIC_WORKFLOW.parameters);
  await loadCsvFromPath(PUBLIC_WORKFLOW.csv, `${PUBLIC_WORKFLOW.label}; ${PUBLIC_WORKFLOW.source}`);
}

async function runOperation(endpoint) {
  renderParameterPayload();
  const issues = localValidationIssues();
  if (issues.length) throw new Error(issues.join("; "));
  const response = await fetch(routeUrl(endpoint, state.operation, currentParameters()), { method: "POST", headers: { ...headers(), "content-type": "text/csv" }, body: state.csvText });
  if (response.headers.get("content-type")?.includes("application/zip")) {
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `rhodyn_${state.operation.operation_id}_bundle.zip`;
    link.click();
    URL.revokeObjectURL(url);
    $("jobState").textContent = `bundle downloaded; ${response.headers.get("x-rhodyn-bundle-sha256") || "checksum not reported"}`;
    return;
  }
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || payload.detail || `HTTP ${response.status}`);
  if (payload.stored_job) state.lastJob = payload.stored_job;
  $("jobState").textContent = payload.stored_job ? `stored ${payload.stored_job.job_id}` : payload.status;
  assignResult(payload);
}

function requireResult() {
  if (!state.lastResult) throw new Error("Run an operation before exporting a result.");
  return state.lastResult;
}

function exportJson() {
  const payload = requireResult();
  downloadText(resultFilename("json"), compactJson(payload) + "\n", "application/json");
}

function exportCsv() {
  requireResult();
  downloadText(resultFilename("csv"), rowsToCsv(resultRows()), "text/csv");
}

function exportMarkdown() {
  requireResult();
  downloadText(resultFilename("md"), resultMarkdown(), "text/markdown");
}

async function copyJson() {
  const payload = requireResult();
  await navigator.clipboard.writeText(compactJson(payload));
  $("jobState").textContent = "result JSON copied";
}

$("operationSelect").addEventListener("change", (event) => renderParameters(operationById(event.target.value)));
$("parameterPanel").addEventListener("input", () => { renderParameterPayload(); renderTrajectory(state.rows); });
$("parameterPanel").addEventListener("change", () => { renderParameterPayload(); renderTrajectory(state.rows); });
$("csvFile").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  state.csvText = file ? await file.text() : "";
  state.loadedSource = file ? file.name : "";
  state.rows = state.csvText ? parseCsv(state.csvText) : [];
  $("rowCount").value = state.rows.length;
  renderTable(state.rows);
  renderTrajectory(state.rows);
  updateValidationState();
});
$("healthButton").addEventListener("click", () => checkHealth().catch((error) => { $("healthState").textContent = error.message; }));
$("sampleButton").addEventListener("click", () => loadExampleCsv().catch((error) => { $("validationState").textContent = error.message; }));
$("publicWorkflowButton").addEventListener("click", () => loadPublicWorkflow().catch((error) => { $("validationState").textContent = error.message; }));
$("runButton").addEventListener("click", () => runOperation(state.operation.endpoint).catch((error) => { $("resultPanel").textContent = error.message; }));
$("submitButton").addEventListener("click", () => runOperation(state.operation.submit_endpoint).catch((error) => { $("resultPanel").textContent = error.message; }));
$("bundleButton").addEventListener("click", () => runOperation(state.operation.bundle_endpoint).catch((error) => { $("resultPanel").textContent = error.message; }));
$("downloadJsonButton").addEventListener("click", () => { try { exportJson(); } catch (error) { $("jobState").textContent = error.message; } });
$("downloadCsvButton").addEventListener("click", () => { try { exportCsv(); } catch (error) { $("jobState").textContent = error.message; } });
$("downloadMarkdownButton").addEventListener("click", () => { try { exportMarkdown(); } catch (error) { $("jobState").textContent = error.message; } });
$("copyJsonButton").addEventListener("click", () => copyJson().catch((error) => { $("jobState").textContent = error.message; }));

loadContract().catch((error) => {
  $("contractBadge").textContent = "contract unavailable";
  $("resultPanel").textContent = error.message;
});
