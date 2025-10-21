// import { useEffect, useMemo, useState } from 'react';
// import CrimeChart from './components/CrimeChart.jsx';
// import { getViolations, getHistorical, getForecast, getPredictYear } from './lib/api.js';

// const YEARS = Array.from({ length: 2030 - 2021 + 1 }, (_, i) => 2021 + i);

// export default function App() {
//   const [province] = useState("Ontario [35]");
//   const [violations, setViolations] = useState([]);
//   const [violation, setViolation] = useState("");
//   const [year, setYear] = useState(2030);
//   const [loading, setLoading] = useState(false);
//   const [err, setErr] = useState("");
//   const [hist, setHist] = useState(null);
//   const [fc, setFc] = useState(null);     // forecast response for 2024+
//   const [pred, setPred] = useState(null); // backtest response for 2021–2023

//   // load violations once
//   useEffect(() => {
//     (async () => {
//       try {
//         const js = await getViolations();
//         setViolations(js.violations || []);
//         if (js.violations?.length) setViolation(js.violations[0]);
//       } catch (e) { setErr(String(e)); }
//     })();
//   }, []);

//   // load historical for context
//   useEffect(() => {
//     if (!violation) return;
//     setErr(""); setLoading(true);
//     getHistorical(violation)
//       .then(h => setHist(h))
//       .catch(e => setErr(String(e)))
//       .finally(() => setLoading(false));
//   }, [violation]);

//   // load either forecast (year > last) or single-year backtest (2021–2023)
//   useEffect(() => {
//     if (!violation || !hist) return;
//     const last = hist.last_observed_year;
//     setErr(""); setLoading(true);
//     if (year > last) {
//       getForecast(violation, year)
//         .then(f => { setFc(f); setPred(null); })
//         .catch(e => setErr(String(e)))
//         .finally(() => setLoading(false));
//     } else {
//       getPredictYear(violation, year)
//         .then(p => { setPred(p); setFc(null); })
//         .catch(e => setErr(String(e)))
//         .finally(() => setLoading(false));
//     }
//   }, [violation, year, hist]);

//   // Build ONE unified dataset: [{year, actual, forecast, predicted}]
//   const { rows, xMin, xMax, showForecastRegion } = useMemo(() => {
//     if (!hist) return { rows: [], xMin: null, xMax: null, showForecastRegion: false };
//     const last = hist.last_observed_year;

//     // start with actuals
//     const map = new Map();
//     for (let i = 0; i < hist.years.length; i++) {
//       const yr = hist.years[i];
//       const val = hist.actual[i];
//       map.set(yr, { year: yr, actual: val ?? null, forecast: null, predicted: null });
//     }

//     // add forecast for 2024+ and duplicate boundary at 2023 for smooth join
//     if (fc?.forecast?.length) {
//       const boundary = map.get(last) || { year: last, actual: null, forecast: null, predicted: null };
//       boundary.forecast = boundary.actual; // connect lines at boundary
//       map.set(last, boundary);

//       for (const item of fc.forecast) {
//         const yr = item.year;
//         if (!map.has(yr)) map.set(yr, { year: yr, actual: null, forecast: null, predicted: null });
//         map.get(yr).forecast = item.yhat;
//       }
//     }

//     // add backtest short segment for selected 2021–2023
//     if (pred && pred.year && pred.yhat != null) {
//       const prev = pred.year - 1;
//       // set predicted at (year-1) equal to actual there (so dashed connector draws)
//       if (!map.has(prev)) map.set(prev, { year: prev, actual: null, forecast: null, predicted: null });
//       map.get(prev).predicted = map.get(prev).actual;

//       // set predicted at selected year to yhat
//       if (!map.has(pred.year)) map.set(pred.year, { year: pred.year, actual: null, forecast: null, predicted: null });
//       map.get(pred.year).predicted = pred.yhat;
//     }

//     // ⬅️ KEY CHANGE: clip strictly to the user's selected year
//     const horizon = year;

//     const rows = Array.from(map.values())
//       .filter(r => r.year <= horizon)
//       .sort((a, b) => a.year - b.year);

//     const xMin = rows[0]?.year ?? null;
//     const xMax = rows[rows.length - 1]?.year ?? null;

//     // Only shade forecast region if the selected horizon is beyond last observed
//     const showForecastRegion = year > last;

//     return { rows, xMin, xMax, showForecastRegion };
//   }, [hist, fc, pred, year]);

//   return (
//     <div className="container">
//       <div className="header">
//         <h1>Ontario Crime Prediction</h1>
//         <span className="help">Backtest for 2021–2023 (actual vs predicted). Forecast for 2024–2030.</span>
//       </div>

//       <div className="controls">
//         <div>
//           <div className="help">Province</div>
//           <select value={province} disabled>
//             <option value={province}>{province}</option>
//           </select>
//         </div>
//         <div>
//           <div className="help">Crime (Violation)</div>
//           <select value={violation} onChange={e => setViolation(e.target.value)}>
//             {violations.map(v => (<option key={v} value={v}>{v}</option>))}
//           </select>
//         </div>
//         <div>
//           <div className="help">Select Year (2021–2030)</div>
//           <select value={year} onChange={e => setYear(parseInt(e.target.value, 10))}>
//             {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
//           </select>
//         </div>
//       </div>

//       {err && <div className="error card">Error: {err}</div>}
//       {loading && <div className="loading card">Loading...</div>}
//       {!loading && hist && (
//         <CrimeChart
//           data={rows}
//           xMin={xMin}
//           xMax={xMax}
//           lastObservedYear={hist.last_observed_year}
//           showForecastRegion={showForecastRegion}
//           selectedYear={year}
//           predMeta={pred}
//         />
//       )}

//       <hr />
//       <div className="help">
//         Notes: Forecast models are trained up to 2023. For 2021–2023, the model is re-trained up to (year-1) and predicts that year; chart shows both actual and predicted. The chart always clips to your selected year.
//       </div>
//     </div>
//   );
// }




import { useEffect, useMemo, useState } from 'react';
import CrimeChart from './components/CrimeChart.jsx';
import DataTable from './components/DataTable.jsx';
import {
  getViolations,
  getHistoricalMulti,
  getForecastMulti,
  getPredictYearMulti
} from './lib/api.js';

const YEARS = Array.from({ length: 2030 - 2021 + 1 }, (_, i) => 2021 + i);

// stable palette (distinct colors)
const PALETTE = [
  "#1f77b4","#ff7f0e","#2ca02c","#d62728",
  "#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22"
];

function slugify(v) { return v.replace(/\s+/g,"_").replace(/[\/\[\]]/g,""); }

export default function App() {
  const [province] = useState("Ontario [35]");
  const [allViolations, setAllViolations] = useState([]);
  const [selectedViolations, setSelectedViolations] = useState([]);
  const [year, setYear] = useState(2030);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [historical, setHistorical] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [backtest, setBacktest] = useState(null);

  const colorMap = useMemo(() => {
    const m = new Map();
    (selectedViolations.length ? selectedViolations : allViolations).forEach((v, i) => {
      m.set(v, PALETTE[i % PALETTE.length]);
    });
    return m;
  }, [selectedViolations, allViolations]);

  useEffect(() => {
    (async () => {
      try {
        const js = await getViolations();
        setAllViolations(js.violations || []);
        if (js.violations?.length) setSelectedViolations([js.violations[0]]);
      } catch (e) { setErr(String(e)); }
    })();
  }, []);

  useEffect(() => {
    if (!allViolations.length) return;
    setErr(""); setLoading(true);
    const vs = selectedViolations.length ? selectedViolations : allViolations;
    getHistoricalMulti(vs)
      .then(h => setHistorical(h))
      .catch(e => setErr(String(e)))
      .finally(() => setLoading(false));
  }, [allViolations, selectedViolations]);

  useEffect(() => {
    if (!historical) return;
    const lastObs = Math.max(...historical.items.map(it => it.last_observed_year || 0)); // ~2023
    const vs = selectedViolations.length ? selectedViolations : allViolations;
    setErr(""); setLoading(true);
    if (year > lastObs) {
      getForecastMulti(vs, year)
        .then(f => { setForecast(f); setBacktest(null); })
        .catch(e => setErr(String(e)))
        .finally(() => setLoading(false));
    } else {
      getPredictYearMulti(vs, year)
        .then(p => { setBacktest(p); setForecast(null); })
        .catch(e => setErr(String(e)))
        .finally(() => setLoading(false));
    }
  }, [historical, year, selectedViolations, allViolations]);

  // ONE unified dataset: rows[{year, actual_<slug>, forecast_<slug>, predicted_<slug>}]
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

    // actuals
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

    // forecast + boundary connector
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

    // backtest predicted segment (selected year + connector at year-1)
    if (backtest?.items?.length) {
      for (const bt of backtest.items) {
        const v = bt.violation;
        if (!vsSet.has(v)) continue;
        const slug = slugify(v);
        const y = bt.year;
        if (y <= horizon && bt.yhat != null) {
          const prev = y - 1;
          if (prev >= 0) {
            if (!byYear.has(prev)) byYear.set(prev, { year: prev });
            const rowP = byYear.get(prev);
            const av = rowP[`actual_${slug}`] ?? null;
            rowP[`predicted_${slug}`] = av; // connector (hidden in tooltip)
          }
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

  const onSelectAll = () => setSelectedViolations(allViolations);
  const onClear = () => setSelectedViolations([]);

  return (
    <div className="container">
      <div className="header">
        <h1>Ontario Crime Prediction</h1>
        <span className="help">Multi-select crimes; backtest (2021–2023) or forecast (2024–2030). Chart & table clip to the selected year.</span>
      </div>

      <div className="controls">
        <div className="row">
          <div>
            <div className="help">Province</div>
            <select value={province} disabled>
              <option value={province}>{province}</option>
            </select>
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
              {allViolations.map(v => (
                <option key={v} value={v}>{v}</option>
              ))}
            </select>
            <div style={{ display:'flex', gap:8, marginTop:8 }}>
              <button className="btn" onClick={onSelectAll}>Select all</button>
              <button className="btn" onClick={onClear}>Clear</button>
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
          {/* Chart */}
          <CrimeChart
            data={rows}
            legend={legend}
            xMin={xMin}
            xMax={xMax}
            lastObservedYear={lastObservedYear}
            selectedYear={year}
          />

          {/* Table that mirrors the chart */}
          <DataTable
            data={rows}
            legend={legend}
            selectedYear={year}
            lastObservedYear={lastObservedYear}
          />
        </>
      )}

      <hr />
      <div className="help">
        Notes: For forecast horizons, table shows <strong>Forecast</strong> values for 2024+. For backtests (2021–2023), the selected year shows <strong>Actual / Predicted</strong>.
      </div>
    </div>
  );
}
