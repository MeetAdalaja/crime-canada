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

  const { actualSeries, forecastSeries, maxYear } = useMemo(() => {
    if (!hist) return { actualSeries: [], forecastSeries: [], maxYear: null };

    const last = hist.last_observed_year;

    // Actual line: up to last observed
    const actualSeries = hist.years.map((yr, i) => ({
      year: yr,
      value: hist.actual[i],
    }));

    // Forecast line: start by duplicating the boundary point so lines join visually
    const forecastSeries = [];
    if (actualSeries.length) {
      const lastPoint = actualSeries[actualSeries.length - 1];
      forecastSeries.push({ ...lastPoint }); // duplicate boundary point
    }
    if (fc?.forecast?.length) {
      for (const item of fc.forecast) {
        if (item.year <= year) {
          forecastSeries.push({ year: item.year, value: item.yhat });
        }
      }
    }

    const maxYear = Math.max(
      actualSeries.length ? actualSeries[actualSeries.length - 1].year : 0,
      forecastSeries.length ? forecastSeries[forecastSeries.length - 1].year : 0,
    );

    return { actualSeries, forecastSeries, maxYear };
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
        <CrimeChart
          actualSeries={actualSeries}
          forecastSeries={forecastSeries}
          lastObservedYear={hist?.last_observed_year}
          maxYear={maxYear}
        />)}

    </div>
  );
}
