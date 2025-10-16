import { useEffect, useMemo, useState } from 'react';
import CrimeChart from './components/CrimeChart.jsx';
import { getViolations, getHistorical, getForecast, getPredictYear } from './lib/api.js';

const YEARS = Array.from({ length: 2030 - 2021 + 1 }, (_, i) => 2021 + i);

export default function App() {
  const [province] = useState("Ontario [35]");
  const [violations, setViolations] = useState([]);
  const [violation, setViolation] = useState("");
  const [year, setYear] = useState(2030);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [hist, setHist] = useState(null);
  const [fc, setFc] = useState(null);     // forecast response for 2024+
  const [pred, setPred] = useState(null); // backtest response for 2021–2023

  // load violations once
  useEffect(() => {
    (async () => {
      try {
        const js = await getViolations();
        setViolations(js.violations || []);
        if (js.violations?.length) setViolation(js.violations[0]);
      } catch (e) { setErr(String(e)); }
    })();
  }, []);

  // load historical for context
  useEffect(() => {
    if (!violation) return;
    setErr(""); setLoading(true);
    getHistorical(violation)
      .then(h => setHist(h))
      .catch(e => setErr(String(e)))
      .finally(() => setLoading(false));
  }, [violation]);

  // load either forecast (year > last) or single-year backtest (2021–2023)
  useEffect(() => {
    if (!violation || !hist) return;
    const last = hist.last_observed_year;
    setErr(""); setLoading(true);
    if (year > last) {
      getForecast(violation, year)
        .then(f => { setFc(f); setPred(null); })
        .catch(e => setErr(String(e)))
        .finally(() => setLoading(false));
    } else {
      getPredictYear(violation, year)
        .then(p => { setPred(p); setFc(null); })
        .catch(e => setErr(String(e)))
        .finally(() => setLoading(false));
    }
  }, [violation, year, hist]);

  // Build ONE unified dataset: [{year, actual, forecast, predicted}]
  const { rows, xMin, xMax, showForecastRegion } = useMemo(() => {
    if (!hist) return { rows: [], xMin: null, xMax: null, showForecastRegion: false };
    const last = hist.last_observed_year;

    // start with actuals
    const map = new Map();
    for (let i = 0; i < hist.years.length; i++) {
      const yr = hist.years[i];
      const val = hist.actual[i];
      map.set(yr, { year: yr, actual: val ?? null, forecast: null, predicted: null });
    }

    // add forecast for 2024+ and duplicate boundary at 2023 for smooth join
    if (fc?.forecast?.length) {
      const boundary = map.get(last) || { year: last, actual: null, forecast: null, predicted: null };
      boundary.forecast = boundary.actual; // connect lines at boundary
      map.set(last, boundary);

      for (const item of fc.forecast) {
        const yr = item.year;
        if (!map.has(yr)) map.set(yr, { year: yr, actual: null, forecast: null, predicted: null });
        map.get(yr).forecast = item.yhat;
      }
    }

    // add backtest short segment for selected 2021–2023
    if (pred && pred.year && pred.yhat != null) {
      const prev = pred.year - 1;
      // set predicted at (year-1) equal to actual there (so dashed connector draws)
      if (!map.has(prev)) map.set(prev, { year: prev, actual: null, forecast: null, predicted: null });
      map.get(prev).predicted = map.get(prev).actual;

      // set predicted at selected year to yhat
      if (!map.has(pred.year)) map.set(pred.year, { year: pred.year, actual: null, forecast: null, predicted: null });
      map.get(pred.year).predicted = pred.yhat;
    }

    // ⬅️ KEY CHANGE: clip strictly to the user's selected year
    const horizon = year;

    const rows = Array.from(map.values())
      .filter(r => r.year <= horizon)
      .sort((a, b) => a.year - b.year);

    const xMin = rows[0]?.year ?? null;
    const xMax = rows[rows.length - 1]?.year ?? null;

    // Only shade forecast region if the selected horizon is beyond last observed
    const showForecastRegion = year > last;

    return { rows, xMin, xMax, showForecastRegion };
  }, [hist, fc, pred, year]);

  return (
    <div className="container">
      <div className="header">
        <h1>Ontario Crime Prediction</h1>
        <span className="help">Backtest for 2021–2023 (actual vs predicted). Forecast for 2024–2030.</span>
      </div>

      <div className="controls">
        <div>
          <div className="help">Province</div>
          <select value={province} disabled>
            <option value={province}>{province}</option>
          </select>
        </div>
        <div>
          <div className="help">Crime (Violation)</div>
          <select value={violation} onChange={e => setViolation(e.target.value)}>
            {violations.map(v => (<option key={v} value={v}>{v}</option>))}
          </select>
        </div>
        <div>
          <div className="help">Select Year (2021–2030)</div>
          <select value={year} onChange={e => setYear(parseInt(e.target.value, 10))}>
            {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
      </div>

      {err && <div className="error card">Error: {err}</div>}
      {loading && <div className="loading card">Loading...</div>}
      {!loading && hist && (
        <CrimeChart
          data={rows}
          xMin={xMin}
          xMax={xMax}
          lastObservedYear={hist.last_observed_year}
          showForecastRegion={showForecastRegion}
          selectedYear={year}
          predMeta={pred}
        />
      )}

      <hr />
      <div className="help">
        Notes: Forecast models are trained up to 2023. For 2021–2023, the model is re-trained up to (year-1) and predicts that year; chart shows both actual and predicted. The chart always clips to your selected year.
      </div>
    </div>
  );
}
