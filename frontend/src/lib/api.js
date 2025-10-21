// // frontend/src/lib/api.js
// const BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

// export async function getViolations() {
//   const r = await fetch(`${BASE}/api/v1/violations`);
//   if (!r.ok) throw new Error(`Violations failed: ${r.status}`);
//   return r.json();
// }

// export async function getHistorical(violation) {
//   const url = new URL(`${BASE}/api/v1/historical`);
//   url.searchParams.set("violation", violation);
//   const r = await fetch(url);
//   if (!r.ok) throw new Error(`Historical failed: ${r.status}`);
//   return r.json();
// }

// export async function getForecast(violation, horizon) {
//   const url = new URL(`${BASE}/api/v1/forecast`);
//   url.searchParams.set("violation", violation);
//   url.searchParams.set("horizon", horizon.toString());
//   const r = await fetch(url);
//   if (!r.ok) throw new Error(`Forecast failed: ${r.status}`);
//   return r.json();
// }

// export async function getPredictYear(violation, year) {
//   const url = new URL(`${BASE}/api/v1/predict_year`);
//   url.searchParams.set("violation", violation);
//   url.searchParams.set("year", year.toString());
//   const r = await fetch(url);
//   if (!r.ok) throw new Error(`PredictYear failed: ${r.status}`);
//   return r.json();
// }




const BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

// single (kept, used for initial list)
export async function getViolations() {
  const r = await fetch(`${BASE}/api/v1/violations`);
  if (!r.ok) throw new Error(`Violations failed: ${r.status}`);
  return r.json();
}

// multi variants (new)
export async function getHistoricalMulti(violations) {
  const url = new URL(`${BASE}/api/v1/historical_multi`);
  if (violations && violations.length) {
    for (const v of violations) url.searchParams.append("violations", v);
  } // else: server returns all
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HistoricalMulti failed: ${r.status}`);
  return r.json();
}

export async function getForecastMulti(violations, horizon) {
  const url = new URL(`${BASE}/api/v1/forecast_multi`);
  if (violations && violations.length) {
    for (const v of violations) url.searchParams.append("violations", v);
  }
  url.searchParams.set("horizon", String(horizon));
  const r = await fetch(url);
  if (!r.ok) throw new Error(`ForecastMulti failed: ${r.status}`);
  return r.json();
}

export async function getPredictYearMulti(violations, year) {
  const url = new URL(`${BASE}/api/v1/predict_year_multi`);
  if (violations && violations.length) {
    for (const v of violations) url.searchParams.append("violations", v);
  }
  url.searchParams.set("year", String(year));
  const r = await fetch(url);
  if (!r.ok) throw new Error(`PredictYearMulti failed: ${r.status}`);
  return r.json();
}
