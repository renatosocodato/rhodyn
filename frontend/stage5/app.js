const CONTRACT_URL = "../../api/stage4/frontend_contract.json";
const OPENAPI_URL = "../../api/stage4/openapi.json";
const SCHEMA_FIXTURE_URL = "../../api/stage4/fixtures/schemas.response.json";

const state = {
  contract: null,
  openapi: null,
  schemas: {},
  rows: [],
  csvText: "",
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

function renderTrajectory(rows) {
  const svg = $("trajectoryPlot");
  svg.innerHTML = "";
  if (!rows.length || !("time" in rows[0]) || !("signal" in rows[0])) {
    $("trajectoryState").textContent = rows.length ? "CSV loaded; no time/signal columns" : "waiting for CSV";
    return;
  }
  const grouped = new Map();
  for (const row of rows) {
    const id = row.cell_id || row.sample_id || row.condition || "series";
    if (!grouped.has(id)) grouped.set(id, []);
    grouped.get(id).push({ time: Number(row.time), signal: Number(row.signal) });
  }
  const series = Array.from(grouped.values()).slice(0, 12).map((items) => items.filter((item) => Number.isFinite(item.time) && Number.isFinite(item.signal)).sort((a, b) => a.time - b.time));
  const all = series.flat();
  if (!all.length) return;
  const minT = Math.min(...all.map((item) => item.time));
  const maxT = Math.max(...all.map((item) => item.time));
  const minY = Math.min(...all.map((item) => item.signal));
  const maxY = Math.max(...all.map((item) => item.signal));
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
  $("trajectoryState").textContent = `${rows.length} rows, ${series.length} displayed traces`;
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

function assignResult(payload) {
  state.lastResult = payload;
  const text = JSON.stringify(payload, null, 2);
  $("resultPanel").textContent = text;
  $("residenceSummary").textContent = operationById("score_residence") === state.operation ? text : $("residenceSummary").textContent;
  $("couplingSummary").textContent = operationById("decide_coupling") === state.operation ? text : $("couplingSummary").textContent;
  $("reserveSummary").textContent = operationById("summarize_reserve") === state.operation ? text : $("reserveSummary").textContent;
  $("modelSummary").textContent = operationById("compare_models") === state.operation ? text : $("modelSummary").textContent;
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
  const response = await fetch(`../../${state.operation.example_csv}`);
  if (!response.ok) throw new Error(`Could not load ${state.operation.example_csv}`);
  state.csvText = await response.text();
  state.rows = parseCsv(state.csvText);
  $("rowCount").value = state.rows.length;
  $("csvFile").value = "";
  renderTable(state.rows);
  renderTrajectory(state.rows);
  updateValidationState();
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

$("operationSelect").addEventListener("change", (event) => renderParameters(operationById(event.target.value)));
$("parameterPanel").addEventListener("input", () => { renderParameterPayload(); renderTrajectory(state.rows); });
$("parameterPanel").addEventListener("change", () => { renderParameterPayload(); renderTrajectory(state.rows); });
$("csvFile").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  state.csvText = file ? await file.text() : "";
  state.rows = state.csvText ? parseCsv(state.csvText) : [];
  $("rowCount").value = state.rows.length;
  renderTable(state.rows);
  renderTrajectory(state.rows);
  updateValidationState();
});
$("healthButton").addEventListener("click", () => checkHealth().catch((error) => { $("healthState").textContent = error.message; }));
$("sampleButton").addEventListener("click", () => loadExampleCsv().catch((error) => { $("validationState").textContent = error.message; }));
$("runButton").addEventListener("click", () => runOperation(state.operation.endpoint).catch((error) => { $("resultPanel").textContent = error.message; }));
$("submitButton").addEventListener("click", () => runOperation(state.operation.submit_endpoint).catch((error) => { $("resultPanel").textContent = error.message; }));
$("bundleButton").addEventListener("click", () => runOperation(state.operation.bundle_endpoint).catch((error) => { $("resultPanel").textContent = error.message; }));

loadContract().catch((error) => {
  $("contractBadge").textContent = "contract unavailable";
  $("resultPanel").textContent = error.message;
});
