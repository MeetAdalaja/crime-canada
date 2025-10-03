import { useEffect, useMemo, useState } from 'react';
import CrimeChart from './components/CrimeChart.jsx';
import { getViolations, getHistorical, getForecast } from './lib/api.js';

const YEARS = Array.from({ length: 2030 - 2024 + 1 }, (_, i) => 2024 + i);

export default function App() {
  const [province] = useState("Ontario [35]");
  const [violations, setViolations] = useState([]);
  const [violation, setViolation] = useState("");
  const [year, setYear] = useState(2030);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [hist, setHist] = useState(null);
  const [fc, setFc] = useState(null);

  // load violations once
  useEffect(() => {
    (async () => {
      try {
        const js = await getViolations();
        setViolations(js.violations || []);
        // default to first violation
        if (js.violations?.length) setViolation(js.violations[0]);
      } catch (e) {
        setErr(String(e));
      }
    })();
  }, []);

  // whenever violation or year change, load data
  useEffect(() => {
    if (!violation) return;
    setErr("");
    setLoading(true);
    Promise.all([getHistorical(violation), getForecast(violation, year)])
      .then(([h, f]) => {
        setHist(h);
        setFc(f);
      })
      .catch(e => setErr(String(e)))
      .finally(() => setLoading(false));
  }, [violation, year]);

  const chartData = useMemo(() => {
    if (!hist) return [];
    const last = hist.last_observed_year;
    const rows = [];

    // actuals
    for (let i = 0; i < hist.years.length; i++) {
      rows.push({ year: hist.years[i], actual: hist.actual[i] });
    }

    // forecasts
    if (fc?.forecast?.length) {
      const m = new Map(fc.forecast.map(d => [d.year, d.yhat]));
      const maxYear = Math.max(...fc.forecast.map(d => d.year));
      for (let y = last + 1; y <= Math.min(maxYear, year); y++) {
        rows.push({ year: y, forecast: m.get(y) ?? null });
      }
    }

    // ensure sorted and fields present
    rows.sort((a, b) => a.year - b.year);
    return rows;
  }, [hist, fc, year]);

  return (
    <div className="container">
      

      <div className="controls">
        <div>
          <div className="help">Province</div>
          <select value={province} disabled>
            <option value={province}>{province}</option>
          </select>
        </div>
        <div>
          <div className="help">Crime (Violation)</div>
          <select value={violation} onChange={e => setViolation(e.target.value)} className='dropdown_select'>
            {violations.map(v => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
        </div>
        <div>
          <div className="help">Forecast to Year</div>
          <select value={year} onChange={e => setYear(parseInt(e.target.value, 10))} className='dropdown_select'>
            {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
      </div>

      {err && <div className="error card">Error: {err}</div>}
      {loading && <div className="loading card">Loading...</div>}
      {!loading && hist && (
        <CrimeChart data={chartData} lastObservedYear={hist.last_observed_year} />
      )}

    </div>
  );
}
