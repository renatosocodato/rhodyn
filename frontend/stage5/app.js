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
  lastJob: null,
  lastSimulation: null
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

function statusChip(label, passed = true) {
  return `<span class="status-chip ${passed ? "pass" : "warn"}">${escapeHtml(label)}</span>`;
}

function metricCard(label, value, detail = "") {
  return `<div class="metric-card"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong>${detail ? `<p>${escapeHtml(detail)}</p>` : ""}</div>`;
}

function resultTable(rows, columns) {
  if (!rows.length) return "";
  return `
    <div class="comparison-table">
      <table>
        <thead><tr>${columns.map((column) => `<th>${escapeHtml(column.label)}</th>`).join("")}</tr></thead>
        <tbody>${rows.map((row) => `<tr>${columns.map((column) => `<td>${escapeHtml(column.format ? column.format(row) : row[column.key] ?? "")}</td>`).join("")}</tr>`).join("")}</tbody>
      </table>
    </div>
  `;
}

function comparisonSuite({ title, subtitle, cards, plot = "", table = "", note = "" }) {
  return `
    <div class="comparison-suite">
      <div class="comparison-head">
        <div>
          <h3>${escapeHtml(title)}</h3>
          <p>${escapeHtml(subtitle)}</p>
        </div>
      </div>
      <div class="metric-strip">${cards.join("")}</div>
      ${plot ? `<div class="comparison-plot">${plot}</div>` : ""}
      ${table}
      ${note ? `<p class="comparison-note">${escapeHtml(note)}</p>` : ""}
    </div>
  `;
}

function rankedBarRows(rows, valueField, labelField, { maxRows = 12, scale = "absolute", formatter = fmt } = {}) {
  const visible = rows.slice(0, maxRows);
  const values = visible.map((row) => Number(row[valueField])).filter(Number.isFinite);
  if (!values.length) return "";
  const maxAbs = Math.max(...values.map(Math.abs), 1e-9);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = Math.max(max - min, 1e-9);
  return `<div class="ranked-bars">${visible.map((row, index) => {
    const value = Number(row[valueField]);
    const width = scale === "inverse" ? ((max - value) / span) * 100 : (Math.abs(value) / maxAbs) * 100;
    return `
      <div class="ranked-row">
        <span class="rank">${index + 1}</span>
        <span class="label">${escapeHtml(row[labelField] ?? "")}</span>
        <div class="track"><i style="width:${Math.max(3, Math.min(100, width)).toFixed(1)}%"></i></div>
        <strong>${escapeHtml(formatter(value, row))}</strong>
      </div>
    `;
  }).join("")}</div>`;
}

function couplingIntervalPlot(records, decisions) {
  if (!records.length || !decisions.length) return "";
  const rows = records.map((record, index) => ({ ...record, ...(decisions[index] || {}) }));
  return `
    <div class="margin-axis"><span>-margin</span><span>0</span><span>+margin</span></div>
    <div class="interval-list">${rows.map((row) => {
      const margin = Math.max(Math.abs(Number(row.margin)), 1e-9);
      const toPct = (value) => Math.max(0, Math.min(100, ((Number(value) + margin) / (2 * margin)) * 100));
      const left = toPct(row.ci_low);
      const right = toPct(row.ci_high);
      const estimate = toPct(row.estimate);
      return `
        <div class="interval-row ${row.passes ? "pass" : "warn"}">
          <span class="label">${escapeHtml(row.contrast || "")}</span>
          <div class="interval-track">
            <em class="zero"></em>
            <b style="left:${left.toFixed(1)}%;width:${Math.max(1, right - left).toFixed(1)}%"></b>
            <i style="left:${estimate.toFixed(1)}%"></i>
          </div>
          ${statusChip(row.passes ? "inside" : "outside", row.passes)}
        </div>
      `;
    }).join("")}</div>
  `;
}

function renderResidenceComparison(payload) {
  const summaries = [...(payload.summaries || [])].sort((a, b) => Number(b.residence_fraction || 0) - Number(a.residence_fraction || 0));
  const meanResidence = summaries.length ? summaries.reduce((total, row) => total + Number(row.residence_fraction || 0), 0) / summaries.length : NaN;
  const meanMax = summaries.length ? summaries.reduce((total, row) => total + Number(row.max_signal || 0), 0) / summaries.length : NaN;
  const plot = rankedBarRows(summaries, "residence_fraction", "cell_id", { formatter: (value) => fmt(value) });
  const table = resultTable(summaries.slice(0, 12), [
    { label: "Trace", key: "cell_id" },
    { label: "Condition", key: "condition" },
    { label: "Residence", format: (row) => fmt(Number(row.residence_fraction)) },
    { label: "Residence time", format: (row) => fmt(Number(row.residence_time)) },
    { label: "Max signal", format: (row) => fmt(Number(row.max_signal)) },
    { label: "Segments", format: (row) => String((row.segments || []).length) }
  ]);
  return comparisonSuite({
    title: "Residence-window comparison",
    subtitle: "Traces are ranked by fraction of observed time inside the declared signal window.",
    cards: [
      metricCard("Traces", String(summaries.length)),
      metricCard("Mean residence", fmt(meanResidence)),
      metricCard("Mean max signal", fmt(meanMax)),
      metricCard("Window", `${fmt(Number(payload.window?.low))} to ${fmt(Number(payload.window?.high))}`)
    ],
    plot,
    table,
    note: "Residence summaries are derived from submitted trajectories and the visible window parameters."
  });
}

function renderCouplingComparison(payload) {
  const records = payload.records || [];
  const decisions = payload.decisions || [];
  const passing = decisions.filter((row) => row.passes).length;
  const rows = records.map((record, index) => ({ ...record, ...(decisions[index] || {}) }));
  const table = resultTable(rows, [
    { label: "Contrast", key: "contrast" },
    { label: "Estimate", format: (row) => fmt(Number(row.estimate)) },
    { label: "90% CI low", format: (row) => fmt(Number(row.ci_low)) },
    { label: "90% CI high", format: (row) => fmt(Number(row.ci_high)) },
    { label: "Margin", format: (row) => fmt(Number(row.margin)) },
    { label: "Decision", format: (row) => row.passes ? "inside margin" : "outside margin" }
  ]);
  return comparisonSuite({
    title: "Bounded-coupling comparison",
    subtitle: "Intervals are placed against each contrast's declared equivalence or coupling margin.",
    cards: [
      metricCard("Contrasts", String(decisions.length)),
      metricCard("Inside margin", `${passing}/${decisions.length}`),
      metricCard("Rule", "interval + ROPE"),
      metricCard("Zero coupling", "not claimed")
    ],
    plot: couplingIntervalPlot(records, decisions),
    table,
    note: "A passing interval supports bounded coupling within the declared margin, not absence of all coupling."
  });
}

function renderReserveComparison(payload) {
  const summaries = [...(payload.summaries || [])].sort((a, b) => Number(b.reserve || 0) - Number(a.reserve || 0));
  const meanReserve = summaries.length ? summaries.reduce((total, row) => total + Number(row.reserve || 0), 0) / summaries.length : NaN;
  const meanPeak = summaries.length ? summaries.reduce((total, row) => total + Number(row.peak_response || 0), 0) / summaries.length : NaN;
  const table = resultTable(summaries.slice(0, 12), [
    { label: "Sample", key: "sample_id" },
    { label: "Condition", key: "condition" },
    { label: "Replicate", key: "replicate" },
    { label: "Reserve", format: (row) => fmt(Number(row.reserve)) },
    { label: "Peak", format: (row) => fmt(Number(row.peak_response)) },
    { label: "Points", key: "n_points" }
  ]);
  return comparisonSuite({
    title: "Reserve-buffering comparison",
    subtitle: "Samples are ranked by reserve coordinate under the declared floor, ceiling, and normalization choices.",
    cards: [
      metricCard("Samples", String(summaries.length)),
      metricCard("Mean reserve", fmt(meanReserve)),
      metricCard("Mean peak", fmt(meanPeak)),
      metricCard("Scale", "derived")
    ],
    plot: rankedBarRows(summaries, "reserve", "sample_id"),
    table,
    note: "Reserve is a derived response summary, not a direct measurement of inflammatory injury."
  });
}

function renderModelComparison(payload) {
  const fits = [...(payload.fits || [])].sort((a, b) => Number(a.bic || 0) - Number(b.bic || 0));
  const best = fits[0] || {};
  const bestBic = Number(best.bic);
  const withDelta = fits.map((row) => ({ ...row, delta_bic: Number(row.bic) - bestBic }));
  const table = resultTable(withDelta, [
    { label: "Model", key: "model" },
    { label: "Delta BIC", format: (row) => fmt(Number(row.delta_bic)) },
    { label: "BIC", format: (row) => fmt(Number(row.bic)) },
    { label: "AIC", format: (row) => fmt(Number(row.aic)) },
    { label: "RMSE", format: (row) => fmt(Number(row.rmse)) },
    { label: "RSS", format: (row) => fmt(Number(row.rss)) }
  ]);
  return comparisonSuite({
    title: "Reduced-architecture ranking",
    subtitle: "Models are ordered by BIC, with delta BIC shown relative to the best retained fit.",
    cards: [
      metricCard("Models", String(fits.length)),
      metricCard("Best model", best.model || "-"),
      metricCard("Best BIC", fmt(bestBic)),
      metricCard("Metric", "lower BIC")
    ],
    plot: rankedBarRows(withDelta, "delta_bic", "model", { formatter: (value) => fmt(value) }),
    table,
    note: "Model comparison ranks submitted endpoint rows under declared assumptions; it does not identify every molecular edge."
  });
}

function renderResultVisual(payload) {
  if (!payload) {
    $("resultVisual").innerHTML = "";
    return;
  }
  const operation = resultOperation(payload);
  const job = payload.job || {};
  const rows = resultRows(payload);
  const shellCards = [
    metricCard("Operation", operation || "-"),
    metricCard("Status", payload.status || "-"),
    metricCard("Rows", String(job.input_rows ?? rows.length)),
    metricCard("Job", job.job_id || "not stored")
  ];
  let detail = comparisonSuite({
    title: "Result overview",
    subtitle: "The raw JSON result is retained below for exact reproducibility.",
    cards: shellCards,
    table: resultTable(rows.slice(0, 12), Object.keys(rows[0] || {}).slice(0, 8).map((key) => ({ label: key, key })))
  });
  if (operation === "score_residence") {
    detail = renderResidenceComparison(payload);
  } else if (operation === "decide_coupling") {
    detail = renderCouplingComparison(payload);
  } else if (operation === "summarize_reserve") {
    detail = renderReserveComparison(payload);
  } else if (operation === "compare_models") {
    detail = renderModelComparison(payload);
  } else if (operation === "validate") {
    const issues = payload.issues || [];
    detail = comparisonSuite({
      title: "Schema validation",
      subtitle: "The submitted rows are checked against the selected table schema.",
      cards: [...shellCards, metricCard("Schema", payload.kind || "-"), metricCard("Issues", String(issues.length))],
      plot: issues.length ? `<pre class="markdown-preview">${escapeHtml(rowsToMarkdown("Validation issues", issues))}</pre>` : "<p class=\"result-note\">Schema validation passed for the submitted rows.</p>"
    });
  } else if (operation === "export_markdown") {
    detail = comparisonSuite({
      title: "Markdown report",
      subtitle: "This export summarizes submitted rows and does not add inference.",
      cards: shellCards,
      plot: `<pre class="markdown-preview">${escapeHtml(payload.markdown || "")}</pre>`
    });
  }
  $("resultVisual").innerHTML = detail;
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


const SIMULATION_DEFAULTS = {
  duration: 20,
  dt: 0.5,
  burden_threshold: 0.5,
  initial_rhoa: 0.45,
  initial_src: 0.20,
  initial_reserve: 0.80,
  rhoa_input: 0.08,
  rhoa_decay: 0.04,
  window_low: 0.35,
  window_high: 0.75,
  window_slope: 0.05,
  src_drive: 0.15,
  src_decay: 0.08,
  reserve_decay: 0.06,
  reserve_recovery: 0.02,
  myh9_gain: 0.20,
  myh10_gain: 0.25
};

const SIMULATION_PARAMETER_FIELDS = [
  ["initial_rhoa", "Initial RhoA"],
  ["initial_src", "Initial Src"],
  ["initial_reserve", "Initial reserve"],
  ["rhoa_input", "RhoA input"],
  ["rhoa_decay", "RhoA decay"],
  ["window_low", "Window low"],
  ["window_high", "Window high"],
  ["window_slope", "Window slope"],
  ["src_drive", "Src drive"],
  ["src_decay", "Src decay"],
  ["reserve_decay", "Reserve decay"],
  ["reserve_recovery", "Reserve recovery"],
  ["myh9_gain", "Myh9 gain"],
  ["myh10_gain", "Myh10 gain"]
];

const SIMULATION_PRESETS = {
  default: {
    label: "Default controller",
    description: "Mirrors rhodyn simulate defaults.",
    values: SIMULATION_DEFAULTS
  },
  buffered_window: {
    label: "Buffered window",
    description: "Starts in the permissive RhoA window with stronger reserve recovery.",
    values: { ...SIMULATION_DEFAULTS, initial_rhoa: 0.52, initial_reserve: 0.9, rhoa_input: 0.035, src_drive: 0.10, reserve_recovery: 0.045 }
  },
  low_residence: {
    label: "Low residence pressure",
    description: "Starts below the RhoA window and allows Src-linked burden to rise.",
    values: { ...SIMULATION_DEFAULTS, initial_rhoa: 0.22, rhoa_input: 0.035, initial_src: 0.28, reserve_decay: 0.075 }
  },
  excessive_engagement: {
    label: "Excessive engagement",
    description: "Keeps RhoA high enough that window residence collapses late.",
    values: { ...SIMULATION_DEFAULTS, initial_rhoa: 0.82, rhoa_input: 0.11, rhoa_decay: 0.025, src_drive: 0.12 }
  }
};

function sigmoid(value) {
  return 1 / (1 + Math.exp(-value));
}

function windowGateLocal(rhoa, params) {
  const lower = sigmoid((rhoa - params.window_low) / params.window_slope);
  const upper = sigmoid((params.window_high - rhoa) / params.window_slope);
  return lower * upper;
}

function simulateControllerLocal(params) {
  if (!(params.dt > 0) || params.duration < 0) throw new Error("duration must be non-negative and dt must be positive");
  let rhoa = params.initial_rhoa;
  let src = params.initial_src;
  let reserve = params.initial_reserve;
  const rows = [];
  const steps = Math.trunc(params.duration / params.dt) + 1;
  for (let step = 0; step < steps; step += 1) {
    const time = step * params.dt;
    const gate = windowGateLocal(rhoa, params);
    const myh9 = params.myh9_gain * rhoa;
    const myh10 = params.myh10_gain * src * (1 - reserve);
    const burden = src * (1 - reserve);
    rows.push({
      time,
      rhoa,
      window_gate: gate,
      src,
      reserve,
      myh9_route: myh9,
      myh10_route: myh10,
      burden
    });
    rhoa += params.dt * (params.rhoa_input - params.rhoa_decay * rhoa);
    src += params.dt * (params.src_drive * (1 - gate) - params.src_decay * src);
    reserve += params.dt * (params.reserve_recovery * gate - params.reserve_decay * src * reserve);
    reserve = Math.max(0, Math.min(1, reserve));
  }
  return rows;
}

function firstPassage(rows, field, threshold, direction = "above") {
  for (const row of rows) {
    const value = Number(row[field]);
    if (direction === "above" && value >= threshold) return row.time;
    if (direction === "below" && value <= threshold) return row.time;
  }
  return null;
}

function simulationResidence(rows, params) {
  const points = rows.map((row) => ({ time: row.time, signal: row.rhoa }));
  return residenceForPoints(points, params.window_low, params.window_high);
}

function simulationParameters() {
  const params = { ...SIMULATION_DEFAULTS };
  params.duration = Number($("simulationDuration").value);
  params.dt = Number($("simulationDt").value);
  params.burden_threshold = Number($("simulationBurdenThreshold").value);
  document.querySelectorAll("[data-sim-param]").forEach((input) => {
    params[input.dataset.simParam] = Number(input.value);
  });
  for (const [key, value] of Object.entries(params)) {
    if (!Number.isFinite(value)) throw new Error(`Simulation parameter ${key} is not numeric.`);
  }
  return params;
}

function setSimulationParameters(values) {
  $("simulationDuration").value = values.duration;
  $("simulationDt").value = values.dt;
  $("simulationBurdenThreshold").value = values.burden_threshold;
  for (const [key] of SIMULATION_PARAMETER_FIELDS) {
    const input = document.querySelector(`[data-sim-param="${key}"]`);
    if (input) input.value = values[key];
  }
}

function renderSimulationControls() {
  $("simulationPreset").innerHTML = Object.entries(SIMULATION_PRESETS)
    .map(([key, preset]) => `<option value="${key}">${escapeHtml(preset.label)}</option>`)
    .join("");
  $("simulationParameterPanel").innerHTML = SIMULATION_PARAMETER_FIELDS.map(([key, label]) => `
    <label>${escapeHtml(label)}<input data-sim-param="${key}" type="number" step="0.005"><small>${escapeHtml(key)}</small></label>
  `).join("");
  setSimulationParameters(SIMULATION_DEFAULTS);
}

function simulationSummary(rows, params) {
  const final = rows[rows.length - 1] || {};
  const residence = simulationResidence(rows, params);
  const peakBurden = Math.max(...rows.map((row) => row.burden));
  const minReserve = Math.min(...rows.map((row) => row.reserve));
  const peakSrc = Math.max(...rows.map((row) => row.src));
  const peakMyh9 = Math.max(...rows.map((row) => row.myh9_route));
  const peakMyh10 = Math.max(...rows.map((row) => row.myh10_route));
  return {
    rows: rows.length,
    residence_fraction: residence.residenceFraction,
    residence_time: residence.residenceTime,
    residence_segments: residence.segmentCount,
    peak_src: peakSrc,
    min_reserve: minReserve,
    peak_burden: peakBurden,
    final_reserve: final.reserve,
    final_burden: final.burden,
    peak_myh9_route: peakMyh9,
    peak_myh10_route: peakMyh10,
    burden_first_passage: firstPassage(rows, "burden", params.burden_threshold)
  };
}

function simulationPayload(rows, params, presetKey) {
  const preset = SIMULATION_PRESETS[presetKey] || SIMULATION_PRESETS.default;
  return {
    status: "pass",
    operation: "simulate_controller_local",
    source: "frontend Stage 5.1 Simulation Workbench; mirrors rhodyn.models.simulate_controller",
    preset: preset.label,
    preset_description: preset.description,
    parameters: params,
    summary: simulationSummary(rows, params),
    rows,
    interpretation_boundary: "This is a deterministic controller simulation for parameter exploration. It does not add a backend route, fit data, or establish a biological claim."
  };
}

function simulationCommand(params) {
  return [
    "CLI parity",
    `rhodyn simulate --duration ${fmt(params.duration, 2)} --dt ${fmt(params.dt, 2)}`,
    "Python API",
    "from rhodyn.models import ControllerParams, simulate_controller"
  ].join("\n");
}

function renderSimulationPlot(rows, params) {
  const svg = $("simulationPlot");
  svg.innerHTML = "";
  if (!rows.length) return;
  const series = [
    { key: "rhoa", label: "RhoA", cls: "sim-rhoa" },
    { key: "window_gate", label: "Window gate", cls: "sim-gate" },
    { key: "src", label: "Src", cls: "sim-src" },
    { key: "reserve", label: "Reserve", cls: "sim-reserve" },
    { key: "burden", label: "Burden", cls: "sim-burden" }
  ];
  const minT = Math.min(...rows.map((row) => row.time));
  const maxT = Math.max(...rows.map((row) => row.time));
  const values = rows.flatMap((row) => series.map((item) => row[item.key])).concat([params.burden_threshold]);
  const minY = Math.min(0, ...values);
  const maxY = Math.max(1, ...values);
  const x = (value) => 58 + ((value - minT) / Math.max(maxT - minT, 1)) * 790;
  const y = (value) => 292 - ((value - minY) / Math.max(maxY - minY, 1e-9)) * 244;
  svg.insertAdjacentHTML("beforeend", `<line class="axis" x1="58" y1="292" x2="848" y2="292"></line><line class="axis" x1="58" y1="48" x2="58" y2="292"></line>`);
  const thresholdY = y(params.burden_threshold);
  svg.insertAdjacentHTML("beforeend", `<line class="sim-threshold" x1="58" y1="${thresholdY.toFixed(1)}" x2="848" y2="${thresholdY.toFixed(1)}"></line><text class="sim-legend" x="854" y="${thresholdY.toFixed(1)}">burden threshold</text>`);
  series.forEach((item, index) => {
    const points = rows.map((row) => `${x(row.time).toFixed(1)},${y(row[item.key]).toFixed(1)}`).join(" ");
    const legendY = 58 + index * 20;
    svg.insertAdjacentHTML("beforeend", `<polyline class="sim-trace ${item.cls}" points="${points}"></polyline><line class="sim-legend-swatch ${item.cls}" x1="854" y1="${legendY}" x2="876" y2="${legendY}"></line><text class="sim-legend" x="882" y="${legendY + 4}">${item.label}</text>`);
  });
}

function renderSimulationTable(rows) {
  const indices = new Set([0, rows.length - 1]);
  const stride = Math.max(1, Math.floor(rows.length / 8));
  for (let index = 0; index < rows.length; index += stride) indices.add(index);
  const visible = Array.from(indices).sort((a, b) => a - b).map((index) => rows[index]).filter(Boolean);
  const columns = ["time", "rhoa", "window_gate", "src", "reserve", "burden", "myh9_route", "myh10_route"];
  $("simulationTable").innerHTML = `
    <table>
      <thead><tr>${columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("")}</tr></thead>
      <tbody>${visible.map((row) => `<tr>${columns.map((column) => `<td>${fmt(Number(row[column]))}</td>`).join("")}</tr>`).join("")}</tbody>
    </table>
  `;
}

function renderSimulationWorkbench(payload) {
  const summary = payload.summary;
  const firstPassageText = summary.burden_first_passage === null ? "not reached" : `${fmt(summary.burden_first_passage)} time units`;
  $("simulationState").textContent = `${payload.rows.length} simulated points; ${payload.preset}`;
  $("simulationMetrics").innerHTML = [
    metricCard("Residence fraction", fmt(summary.residence_fraction), `${fmt(summary.residence_time)} time units inside the RhoA window`),
    metricCard("Peak burden", fmt(summary.peak_burden), `threshold ${fmt(payload.parameters.burden_threshold)}`),
    metricCard("First passage", firstPassageText, "burden threshold crossing"),
    metricCard("Final reserve", fmt(summary.final_reserve), `minimum ${fmt(summary.min_reserve)}`),
    metricCard("Peak Src", fmt(summary.peak_src), "deterministic trajectory"),
    metricCard("Route split", `${fmt(summary.peak_myh9_route)} / ${fmt(summary.peak_myh10_route)}`, "peak Myh9 / peak Myh10")
  ].join("");
  renderSimulationPlot(payload.rows, payload.parameters);
  renderSimulationTable(payload.rows);
  $("simulationCommand").textContent = simulationCommand(payload.parameters);
}

function runSimulationWorkbench() {
  const params = simulationParameters();
  const rows = simulateControllerLocal(params);
  const payload = simulationPayload(rows, params, $("simulationPreset").value);
  state.lastSimulation = payload;
  renderSimulationWorkbench(payload);
  $("resultPanel").textContent = compactJson(payload);
  $("jobState").textContent = "local deterministic simulation preview";
  return payload;
}

function simulationMarkdown() {
  if (!state.lastSimulation) runSimulationWorkbench();
  const payload = state.lastSimulation;
  return [
    `# RhoDyn simulation workbench`,
    "",
    `Preset: ${payload.preset}`,
    `Rows: ${payload.rows.length}`,
    `Residence fraction: ${fmt(payload.summary.residence_fraction)}`,
    `Peak burden: ${fmt(payload.summary.peak_burden)}`,
    `Final reserve: ${fmt(payload.summary.final_reserve)}`,
    "",
    "The simulation is deterministic and parameter-declared. It mirrors the minimal controller API and does not fit data or add a biological claim."
  ].join("\n") + "\n";
}

function exportSimulationJson() {
  if (!state.lastSimulation) runSimulationWorkbench();
  downloadText("rhodyn_simulation_workbench.json", compactJson(state.lastSimulation) + "\n", "application/json");
}

function exportSimulationCsv() {
  if (!state.lastSimulation) runSimulationWorkbench();
  downloadText("rhodyn_simulation_workbench.csv", rowsToCsv(state.lastSimulation.rows), "text/csv");
}

function exportSimulationMarkdown() {
  downloadText("rhodyn_simulation_workbench.md", simulationMarkdown(), "text/markdown");
}

window.__RHODYN_STAGE5_SIM__ = { simulateControllerLocal, windowGateLocal, SIMULATION_DEFAULTS };

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

$("simulationPreset").addEventListener("change", () => { setSimulationParameters(SIMULATION_PRESETS[$("simulationPreset").value].values); runSimulationWorkbench(); });
$("simulationRunButton").addEventListener("click", () => { try { runSimulationWorkbench(); } catch (error) { $("simulationState").textContent = error.message; } });
$("simulationResetButton").addEventListener("click", () => { setSimulationParameters(SIMULATION_PRESETS[$("simulationPreset").value].values); runSimulationWorkbench(); });
$("simulationParameterPanel").addEventListener("input", () => { try { runSimulationWorkbench(); } catch (error) { $("simulationState").textContent = error.message; } });
$("simulationDuration").addEventListener("input", () => { try { runSimulationWorkbench(); } catch (error) { $("simulationState").textContent = error.message; } });
$("simulationDt").addEventListener("input", () => { try { runSimulationWorkbench(); } catch (error) { $("simulationState").textContent = error.message; } });
$("simulationBurdenThreshold").addEventListener("input", () => { try { runSimulationWorkbench(); } catch (error) { $("simulationState").textContent = error.message; } });
$("simulationExportJsonButton").addEventListener("click", () => { try { exportSimulationJson(); } catch (error) { $("simulationState").textContent = error.message; } });
$("simulationExportCsvButton").addEventListener("click", () => { try { exportSimulationCsv(); } catch (error) { $("simulationState").textContent = error.message; } });
$("simulationExportMarkdownButton").addEventListener("click", () => { try { exportSimulationMarkdown(); } catch (error) { $("simulationState").textContent = error.message; } });

renderSimulationControls();
runSimulationWorkbench();

loadContract().catch((error) => {
  $("contractBadge").textContent = "contract unavailable";
  $("resultPanel").textContent = error.message;
});
