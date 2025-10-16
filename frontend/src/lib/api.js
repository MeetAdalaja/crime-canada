// frontend/src/lib/api.js
const BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function getViolations() {
  const r = await fetch(`${BASE}/api/v1/violations`);
  if (!r.ok) throw new Error(`Violations failed: ${r.status}`);
  return r.json();
}

export async function getHistorical(violation) {
  const url = new URL(`${BASE}/api/v1/historical`);
  url.searchParams.set("violation", violation);
  const r = await fetch(url);
  if (!r.ok) throw new Error(`Historical failed: ${r.status}`);
  return r.json();
}

export async function getForecast(violation, horizon) {
  const url = new URL(`${BASE}/api/v1/forecast`);
  url.searchParams.set("violation", violation);
  url.searchParams.set("horizon", horizon.toString());
  const r = await fetch(url);
  if (!r.ok) throw new Error(`Forecast failed: ${r.status}`);
  return r.json();
}

export async function getPredictYear(violation, year) {
  const url = new URL(`${BASE}/api/v1/predict_year`);
  url.searchParams.set("violation", violation);
  url.searchParams.set("year", year.toString());
  const r = await fetch(url);
  if (!r.ok) throw new Error(`PredictYear failed: ${r.status}`);
  return r.json();
}
