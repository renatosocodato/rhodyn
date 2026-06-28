const CONTRACT_URL = "../../api/stage4/frontend_contract.json";
const OPENAPI_URL = "../../api/stage4/openapi.json";

const state = {
  contract: null,
  openapi: null,
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
    $("trajectoryState").textContent = "CSV loaded; no time/signal columns";
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
  if (op && op.parameters && "low" in op.parameters && "high" in op.parameters) {
    const yHigh = y(Number(op.parameters.high));
    const yLow = y(Number(op.parameters.low));
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
  const fields = Object.entries(operation.parameters || {});
  $("parameterPanel").innerHTML = fields.map(([key, value]) => `<label>${key}<input data-param="${key}" value="${value}"></label>`).join("");
  renderTrajectory(state.rows);
}

function currentParameters() {
  const params = {};
  document.querySelectorAll("[data-param]").forEach((input) => {
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
  const [contractResponse, openapiResponse] = await Promise.all([fetch(CONTRACT_URL), fetch(OPENAPI_URL)]);
  state.contract = await contractResponse.json();
  state.openapi = await openapiResponse.json();
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

async function runOperation(endpoint) {
  if (!state.csvText) throw new Error("Load a CSV table before running an operation.");
  const response = await fetch(routeUrl(endpoint, state.operation, currentParameters()), { method: "POST", headers: { ...headers(), "content-type": "text/csv" }, body: state.csvText });
  if (response.headers.get("content-type")?.includes("application/zip")) {
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `rhodyn_${state.operation.operation_id}_bundle.zip`;
    link.click();
    URL.revokeObjectURL(url);
    $("jobState").textContent = "bundle downloaded";
    return;
  }
  const payload = await response.json();
  if (payload.stored_job) state.lastJob = payload.stored_job;
  $("jobState").textContent = payload.stored_job ? `stored ${payload.stored_job.job_id}` : payload.status;
  assignResult(payload);
}

$("operationSelect").addEventListener("change", (event) => renderParameters(operationById(event.target.value)));
$("csvFile").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  state.csvText = file ? await file.text() : "";
  state.rows = state.csvText ? parseCsv(state.csvText) : [];
  $("rowCount").value = state.rows.length;
  renderTable(state.rows);
  renderTrajectory(state.rows);
});
$("healthButton").addEventListener("click", () => checkHealth().catch((error) => { $("healthState").textContent = error.message; }));
$("runButton").addEventListener("click", () => runOperation(state.operation.endpoint).catch((error) => { $("resultPanel").textContent = error.message; }));
$("submitButton").addEventListener("click", () => runOperation(state.operation.submit_endpoint).catch((error) => { $("resultPanel").textContent = error.message; }));
$("bundleButton").addEventListener("click", () => runOperation(state.operation.bundle_endpoint).catch((error) => { $("resultPanel").textContent = error.message; }));

loadContract().catch((error) => {
  $("contractBadge").textContent = "contract unavailable";
  $("resultPanel").textContent = error.message;
});
