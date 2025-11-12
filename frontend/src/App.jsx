// import { useEffect, useMemo, useState } from 'react';
// import CrimeChart from './components/CrimeChart.jsx';
// import DataTable from './components/DataTable.jsx';
// import {
//   getPlaces,
//   getViolations,
//   getHistoricalMulti,
//   getForecastMulti,
//   getPredictYearMulti
// } from './lib/api.js';

// const YEARS = Array.from({ length: 2030 - 2021 + 1 }, (_, i) => 2021 + i);
// const PALETTE = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22"];
// const slugify = (v) => v.replace(/\s+/g,"_").replace(/[\/\[\]]/g,"");

// export default function App() {
//   const [places, setPlaces] = useState([]);
//   const [place, setPlace] = useState("Ontario [35]");

//   const [allViolations, setAllViolations] = useState([]);
//   const [selectedViolations, setSelectedViolations] = useState([]);

//   const [year, setYear] = useState(2030);
//   const [loading, setLoading] = useState(false);
//   const [err, setErr] = useState("");

//   const [historical, setHistorical] = useState(null);
//   const [forecast, setForecast] = useState(null);
//   const [backtest, setBacktest] = useState(null);

//   // color per violation
//   const colorMap = useMemo(() => {
//     const m = new Map();
//     (selectedViolations.length ? selectedViolations : allViolations).forEach((v, i) => {
//       m.set(v, PALETTE[i % PALETTE.length]);
//     });
//     return m;
//   }, [selectedViolations, allViolations]);

//   // load places + violations
//   useEffect(() => {
//     (async () => {
//       try {
//         const pl = await getPlaces();
//         const vs = await getViolations();
//         setPlaces(pl.places || []);
//         setAllViolations(vs.violations || []);
//         if (vs.violations?.length) setSelectedViolations([vs.violations[0]]);
//         if (pl.places?.length && pl.places.includes("Ontario [35]")) {
//           setPlace("Ontario [35]");
//         } else if (pl.places?.length) {
//           setPlace(pl.places[0]);
//         }
//       } catch (e) { setErr(String(e)); }
//     })();
//   }, []);

//   // fetch historical for selected place + violations
//   useEffect(() => {
//     if (!place || !allViolations.length) return;
//     setErr(""); setLoading(true);
//     const vs = selectedViolations.length ? selectedViolations : allViolations;
//     getHistoricalMulti(place, vs)
//       .then(h => setHistorical(h))
//       .catch(e => setErr(String(e)))
//       .finally(() => setLoading(false));
//   }, [place, allViolations, selectedViolations]);

//   // fetch forecast/backtest for selected place
//   useEffect(() => {
//     if (!historical) return;
//     const lastObs = Math.max(...historical.items.map(it => it.last_observed_year || 0));
//     const vs = selectedViolations.length ? selectedViolations : allViolations;
//     setErr(""); setLoading(true);
//     if (year > lastObs) {
//       getForecastMulti(place, vs, year)
//         .then(f => { setForecast(f); setBacktest(null); })
//         .catch(e => setErr(String(e)))
//         .finally(() => setLoading(false));
//     } else {
//       getPredictYearMulti(place, vs, year)
//         .then(p => { setBacktest(p); setForecast(null); })
//         .catch(e => setErr(String(e)))
//         .finally(() => setLoading(false));
//     }
//   }, [historical, year, selectedViolations, allViolations, place]);

//   // unify dataset
//   const { rows, xMin, xMax, lastObservedYear, legend } = useMemo(() => {
//     if (!historical) return { rows: [], xMin: null, xMax: null, lastObservedYear: null, legend: [] };
//     const items = historical.items;
//     const vs = selectedViolations.length ? selectedViolations : allViolations;
//     const vsSet = new Set(vs);
//     const histMap = new Map();
//     for (const it of items) if (vsSet.has(it.violation)) histMap.set(it.violation, it);

//     const lastObs = Math.max(...[...histMap.values()].map(it => it.last_observed_year || 0));
//     const horizon = year;
//     const byYear = new Map();

//     // actuals
//     for (const v of vs) {
//       const it = histMap.get(v);
//       if (!it) continue;
//       const slug = slugify(v);
//       for (let i = 0; i < it.years.length; i++) {
//         const yr = it.years[i];
//         if (yr > horizon) continue;
//         const val = it.actual[i];
//         if (!byYear.has(yr)) byYear.set(yr, { year: yr });
//         byYear.get(yr)[`actual_${slug}`] = val ?? null;
//       }
//     }

//     // forecast + boundary connector
//     if (forecast?.items?.length) {
//       for (const fc of forecast.items) {
//         if (!vsSet.has(fc.violation)) continue;
//         const slug = slugify(fc.violation);
//         const hist = histMap.get(fc.violation);
//         const boundary = hist?.last_observed_year ?? lastObs;

//         if (boundary <= horizon) {
//           if (!byYear.has(boundary)) byYear.set(boundary, { year: boundary });
//           const rowB = byYear.get(boundary);
//           const av = rowB[`actual_${slug}`] ?? null;
//           rowB[`forecast_${slug}`] = av; // connector (hidden in tooltip)
//         }

//         for (const item of fc.forecast) {
//           const yr = item.year;
//           if (yr > horizon) continue;
//           if (!byYear.has(yr)) byYear.set(yr, { year: yr });
//           byYear.get(yr)[`forecast_${slug}`] = item.yhat;
//         }
//       }
//     }

//     // backtest predicted segment (selected year + connector at year-1)
//     if (backtest?.items?.length) {
//       for (const bt of backtest.items) {
//         if (!vsSet.has(bt.violation)) continue;
//         const slug = slugify(bt.violation);
//         const y = bt.year;
//         if (y <= horizon && bt.yhat != null) {
//           const prev = y - 1;
//           if (!byYear.has(prev)) byYear.set(prev, { year: prev });
//           const rowP = byYear.get(prev);
//           const av = rowP[`actual_${slug}`] ?? null;
//           rowP[`predicted_${slug}`] = av; // connector (hidden in tooltip)
//           if (!byYear.has(y)) byYear.set(y, { year: y });
//           byYear.get(y)[`predicted_${slug}`] = bt.yhat;
//         }
//       }
//     }

//     const rows = Array.from(byYear.values()).sort((a, b) => a.year - b.year);
//     const xMin = rows[0]?.year ?? null;
//     const xMax = rows[rows.length - 1]?.year ?? null;
//     const legend = vs.map(v => ({ v, color: colorMap.get(v) || "#666", slug: slugify(v) }));
//     return { rows, xMin, xMax, lastObservedYear: lastObs, legend };
//   }, [historical, forecast, backtest, selectedViolations, allViolations, year, colorMap]);

//   const onSelectAll = () => setSelectedViolations(allViolations);
//   const onClear = () => setSelectedViolations([]);

//   return (
//     <div className="container">
//       <div className="header">
//         <h1>Crime Prediction — {place}</h1>
//         <span className="help">Multi-select crimes; backtest (2021–2023) or forecast (2024–2030). Chart & table clip to the selected year.</span>
//       </div>

//       <div className="controls">
//         <div className="row">
//           <div>
//             <div className="help">Province</div>
//             <select value={place} onChange={e => setPlace(e.target.value)}>
//               {places.map(p => (<option key={p} value={p}>{p}</option>))}
//             </select>
//           </div>

//           <div>
//             <div className="help">Crimes (multi-select)</div>
//             <select
//               multiple className="select-multi"
//               value={selectedViolations}
//               onChange={(e) => {
//                 const opts = Array.from(e.target.selectedOptions).map(o => o.value);
//                 setSelectedViolations(opts);
//               }}
//             >
//               {allViolations.map(v => (<option key={v} value={v}>{v}</option>))}
//             </select>
//             <div style={{ display:'flex', gap:8, marginTop:8 }}>
//               <button className="btn" onClick={onSelectAll}>Select all</button>
//               <button className="btn" onClick={onClear}>Clear</button>
//             </div>
//           </div>

//           <div>
//             <div className="help">Select Year (2021–2030)</div>
//             <select value={year} onChange={e => setYear(parseInt(e.target.value, 10))}>
//               {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
//             </select>
//           </div>
//         </div>
//       </div>

//       {err && <div className="error card">Error: {err}</div>}
//       {loading && <div className="loading card">Loading...</div>}

//       {!loading && rows.length > 0 && (
//         <>
//           <CrimeChart
//             data={rows}
//             legend={legend}
//             xMin={xMin}
//             xMax={xMax}
//             lastObservedYear={lastObservedYear}
//             selectedYear={year}
//           />
//           <DataTable
//             data={rows}
//             legend={legend}
//             selectedYear={year}
//             lastObservedYear={lastObservedYear}
//           />
//         </>
//       )}
//     </div>
//   );
// }



import { useEffect, useMemo, useState } from 'react';
import CrimeChart from './components/CrimeChart.jsx';
import DataTable from './components/DataTable.jsx';
import {
  getPlaces,
  getViolations,
  getHistoricalMulti,
  getForecastMulti,
  getPredictYearMulti
} from './lib/api.js';

const YEARS = Array.from({ length: 2030 - 2021 + 1 }, (_, i) => 2021 + i);
const PALETTE = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22"];
const slugify = (v) => v.replace(/\s+/g,"_").replace(/[\/\[\]]/g,"");

export default function App() {
  const [places, setPlaces] = useState([]);
  const [selectedPlaces, setSelectedPlaces] = useState([]);

  const [allViolations, setAllViolations] = useState([]);
  const [selectedViolations, setSelectedViolations] = useState([]);

  const [year, setYear] = useState(2030);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const [historical, setHistorical] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [backtest, setBacktest] = useState(null);

  // legend color per violation
  const colorMap = useMemo(() => {
    const m = new Map();
    (selectedViolations.length ? selectedViolations : allViolations).forEach((v, i) => {
      m.set(v, PALETTE[i % PALETTE.length]);
    });
    return m;
  }, [selectedViolations, allViolations]);

  const placesLabel = useMemo(() => {
    if (!selectedPlaces.length) return '—';
    if (selectedPlaces.length === 1) return selectedPlaces[0];
    return `Multiple provinces (${selectedPlaces.length})`;
  }, [selectedPlaces]);

  // load places + violations
  useEffect(() => {
    (async () => {
      try {
        const pl = await getPlaces();
        const vs = await getViolations();
        setPlaces(pl.places || []);
        setAllViolations(vs.violations || []);
        if (vs.violations?.length) setSelectedViolations([vs.violations[0]]);
        // Default to Ontario if present
        if (pl.places?.includes("Ontario [35]")) {
          setSelectedPlaces(["Ontario [35]"]);
        } else if (pl.places?.length) {
          setSelectedPlaces([pl.places[0]]);
        }
      } catch (e) { setErr(String(e)); }
    })();
  }, []);

  // fetch historical for selected place(s) + violations
  useEffect(() => {
    if (!selectedPlaces.length || !allViolations.length) return;
    setErr(""); setLoading(true);
    const vs = selectedViolations.length ? selectedViolations : allViolations;
    getHistoricalMulti(selectedPlaces, vs)
      .then(h => setHistorical(h))
      .catch(e => setErr(String(e)))
      .finally(() => setLoading(false));
  }, [selectedPlaces, allViolations, selectedViolations]);

  // fetch forecast/backtest for selected place(s)
  useEffect(() => {
    if (!historical) return;
    const lastObs = Math.max(...historical.items.map(it => it.last_observed_year || 0));
    const vs = selectedViolations.length ? selectedViolations : allViolations;
    setErr(""); setLoading(true);
    if (year > lastObs) {
      getForecastMulti(selectedPlaces, vs, year)
        .then(f => { setForecast(f); setBacktest(null); })
        .catch(e => setErr(String(e)))
        .finally(() => setLoading(false));
    } else {
      getPredictYearMulti(selectedPlaces, vs, year)
        .then(p => { setBacktest(p); setForecast(null); })
        .catch(e => setErr(String(e)))
        .finally(() => setLoading(false));
    }
  }, [historical, year, selectedViolations, allViolations, selectedPlaces]);

  // unify dataset (same logic as before)
  const { rows, xMin, xMax, lastObservedYear, legend } = useMemo(() => {
    if (!historical) return { rows: [], xMin: null, xMax: null, lastObservedYear: null, legend: [] };
    const items = historical.items;
    const vs = selectedViolations.length ? selectedViolations : allViolations;
    const vsSet = new Set(vs);
    const histMap = new Map();
    for (const it of items) if (vsSet.has(it.violation)) histMap.set(it.violation, it);

    const lastObs = Math.max(...[...histMap.values()].map(it => it.last_observed_year || 0));
    const horizon = year;
    const byYear = new Map();

    // actuals (already aggregated by API when multiple places are passed)
    for (const v of vs) {
      const it = histMap.get(v);
      if (!it) continue;
      const slug = slugify(v);
      for (let i = 0; i < it.years.length; i++) {
        const yr = it.years[i];
        if (yr > horizon) continue;
        const val = it.actual[i];
        if (!byYear.has(yr)) byYear.set(yr, { year: yr });
        byYear.get(yr)[`actual_${slug}`] = val ?? null;
      }
    }

    // forecast + boundary connector (API returned aggregated forecast when multi-places)
    if (forecast?.items?.length) {
      for (const fc of forecast.items) {
        if (!vsSet.has(fc.violation)) continue;
        const slug = slugify(fc.violation);
        const hist = histMap.get(fc.violation);
        const boundary = hist?.last_observed_year ?? lastObs;

        if (boundary <= horizon) {
          if (!byYear.has(boundary)) byYear.set(boundary, { year: boundary });
          const rowB = byYear.get(boundary);
          const av = rowB[`actual_${slug}`] ?? null;
          rowB[`forecast_${slug}`] = av; // connector (hidden in tooltip)
        }

        for (const item of fc.forecast) {
          const yr = item.year;
          if (yr > horizon) continue;
          if (!byYear.has(yr)) byYear.set(yr, { year: yr });
          byYear.get(yr)[`forecast_${slug}`] = item.yhat;
        }
      }
    }

    // backtest predicted (API returned aggregated yhat when multi-places)
    if (backtest?.items?.length) {
      for (const bt of backtest.items) {
        if (!vsSet.has(bt.violation)) continue;
        const slug = slugify(bt.violation);
        const y = bt.year;
        if (y <= horizon && bt.yhat != null) {
          const prev = y - 1;
          if (!byYear.has(prev)) byYear.set(prev, { year: prev });
          const rowP = byYear.get(prev);
          const av = rowP[`actual_${slug}`] ?? null;
          rowP[`predicted_${slug}`] = av; // connector
          if (!byYear.has(y)) byYear.set(y, { year: y });
          byYear.get(y)[`predicted_${slug}`] = bt.yhat;
        }
      }
    }

    const rows = Array.from(byYear.values()).sort((a, b) => a.year - b.year);
    const xMin = rows[0]?.year ?? null;
    const xMax = rows[rows.length - 1]?.year ?? null;
    const legend = vs.map(v => ({ v, color: colorMap.get(v) || "#666", slug: slugify(v) }));
    return { rows, xMin, xMax, lastObservedYear: lastObs, legend };
  }, [historical, forecast, backtest, selectedViolations, allViolations, year, colorMap]);

  const onSelectAllViol = () => setSelectedViolations(allViolations);
  const onClearViol = () => setSelectedViolations([]);

  const onSelectAllPlaces = () => setSelectedPlaces(places);
  const onClearPlaces = () => setSelectedPlaces([]);

  return (
    <div className="container">
      <div className="header">
        <h1>Crime Prediction — {placesLabel}</h1>
        <span className="help">Multi-select provinces and crimes; backtest (2021–2023) or forecast (2024–2030). Chart & table clip to the selected year.</span>
      </div>

      <div className="controls">
        <div className="row">

          <div>
            <div className="help">Provinces (multi-select)</div>
            <select
              multiple
              className="select-multi"
              value={selectedPlaces}
              onChange={(e) => {
                const opts = Array.from(e.target.selectedOptions).map(o => o.value);
                setSelectedPlaces(opts);
              }}
            >
              {places.map(p => (<option key={p} value={p}>{p}</option>))}
            </select>
            <div style={{ display:'flex', gap:8, marginTop:8 }}>
              <button className="btn" onClick={onSelectAllPlaces}>Select all</button>
              <button className="btn" onClick={onClearPlaces}>Clear</button>
            </div>
          </div>

          <div>
            <div className="help">Crimes (multi-select)</div>
            <select
              multiple
              className="select-multi"
              value={selectedViolations}
              onChange={(e) => {
                const opts = Array.from(e.target.selectedOptions).map(o => o.value);
                setSelectedViolations(opts);
              }}
            >
              {allViolations.map(v => (<option key={v} value={v}>{v}</option>))}
            </select>
            <div style={{ display:'flex', gap:8, marginTop:8 }}>
              <button className="btn" onClick={onSelectAllViol}>Select all</button>
              <button className="btn" onClick={onClearViol}>Clear</button>
            </div>
          </div>

          <div>
            <div className="help">Select Year (2021–2030)</div>
            <select value={year} onChange={e => setYear(parseInt(e.target.value, 10))}>
              {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>

        </div>
      </div>

      {err && <div className="error card">Error: {err}</div>}
      {loading && <div className="loading card">Loading...</div>}

      {!loading && rows.length > 0 && (
        <>
          <CrimeChart
            data={rows}
            legend={legend}
            xMin={xMin}
            xMax={xMax}
            lastObservedYear={lastObservedYear}
            selectedYear={year}
          />
          <DataTable
            data={rows}
            legend={legend}
            selectedYear={year}
            lastObservedYear={lastObservedYear}
          />
        </>
      )}
    </div>
  );
}
