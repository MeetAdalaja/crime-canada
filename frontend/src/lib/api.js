// const BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

// export async function getPlaces() {
//   const r = await fetch(`${BASE}/api/v1/places`);
//   if (!r.ok) throw new Error(`Places failed: ${r.status}`);
//   return r.json();
// }

// export async function getViolations() {
//   const r = await fetch(`${BASE}/api/v1/violations`);
//   if (!r.ok) throw new Error(`Violations failed: ${r.status}`);
//   return r.json();
// }

// export async function getHistoricalMulti(place, violations) {
//   const url = new URL(`${BASE}/api/v1/historical_multi`);
//   url.searchParams.set("place", place);
//   if (violations && violations.length) {
//     for (const v of violations) url.searchParams.append("violations", v);
//   }
//   const r = await fetch(url);
//   if (!r.ok) throw new Error(`HistoricalMulti failed: ${r.status}`);
//   return r.json();
// }

// export async function getForecastMulti(place, violations, horizon) {
//   const url = new URL(`${BASE}/api/v1/forecast_multi`);
//   url.searchParams.set("place", place);
//   if (violations && violations.length) {
//     for (const v of violations) url.searchParams.append("violations", v);
//   }
//   url.searchParams.set("horizon", String(horizon));
//   const r = await fetch(url);
//   if (!r.ok) throw new Error(`ForecastMulti failed: ${r.status}`);
//   return r.json();
// }

// export async function getPredictYearMulti(place, violations, year) {
//   const url = new URL(`${BASE}/api/v1/predict_year_multi`);
//   url.searchParams.set("place", place);
//   if (violations && violations.length) {
//     for (const v of violations) url.searchParams.append("violations", v);
//   }
//   url.searchParams.set("year", String(year));
//   const r = await fetch(url);
//   if (!r.ok) throw new Error(`PredictYearMulti failed: ${r.status}`);
//   return r.json();
// }




const BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function getPlaces() {
  const r = await fetch(`${BASE}/api/v1/places`);
  if (!r.ok) throw new Error(`Places failed: ${r.status}`);
  return r.json();
}

export async function getViolations() {
  const r = await fetch(`${BASE}/api/v1/violations`);
  if (!r.ok) throw new Error(`Violations failed: ${r.status}`);
  return r.json();
}

function appendPlaces(url, places) {
  if (places && places.length) {
    if (places.length === 1) {
      url.searchParams.set("place", places[0]);
    } else {
      for (const p of places) url.searchParams.append("places", p);
    }
  }
}

export async function getHistoricalMulti(places, violations) {
  const url = new URL(`${BASE}/api/v1/historical_multi`);
  appendPlaces(url, places);
  if (violations && violations.length) {
    for (const v of violations) url.searchParams.append("violations", v);
  }
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HistoricalMulti failed: ${r.status}`);
  return r.json();
}

export async function getForecastMulti(places, violations, horizon) {
  const url = new URL(`${BASE}/api/v1/forecast_multi`);
  appendPlaces(url, places);
  if (violations && violations.length) {
    for (const v of violations) url.searchParams.append("violations", v);
  }
  url.searchParams.set("horizon", String(horizon));
  const r = await fetch(url);
  if (!r.ok) throw new Error(`ForecastMulti failed: ${r.status}`);
  return r.json();
}

export async function getPredictYearMulti(places, violations, year) {
  const url = new URL(`${BASE}/api/v1/predict_year_multi`);
  appendPlaces(url, places);
  if (violations && violations.length) {
    for (const v of violations) url.searchParams.append("violations", v);
  }
  url.searchParams.set("year", String(year));
  const r = await fetch(url);
  if (!r.ok) throw new Error(`PredictYearMulti failed: ${r.status}`);
  return r.json();
}
