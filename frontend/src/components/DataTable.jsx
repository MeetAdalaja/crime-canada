import React, { useMemo } from 'react';

// legend: [{ v, color, slug }]
// data: rows like [{ year, actual_<slug>, forecast_<slug>, predicted_<slug>, ... }]
// selectedYear: number
// lastObservedYear: number (e.g., 2023)
export default function DataTable({ data, legend, selectedYear, lastObservedYear }) {
  const years = useMemo(() => data.map(r => r.year), [data]);
  const rowMap = useMemo(() => {
    const m = new Map();
    for (const r of data) m.set(r.year, r);
    return m;
  }, [data]);

  const fmt = (n) => (n == null ? '—' : Math.round(n).toLocaleString());

  // Return {text, isDual} where isDual means "Actual / Predicted" for the backtest selected year
  const cellDisplay = (slug, year) => {
    const row = rowMap.get(year) || {};
    const actual = row[`actual_${slug}`];
    const forecast = row[`forecast_${slug}`];
    const predicted = row[`predicted_${slug}`];

    // Years up to lastObservedYear -> Actuals domain
    if (year <= Number(lastObservedYear)) {
      // On a backtest selection (2021–2023), show both Actual / Predicted on the selected year
      if (Number(selectedYear) <= Number(lastObservedYear) && year === Number(selectedYear) && predicted != null) {
        return { text: `${fmt(actual)} / ${fmt(predicted)}`, isDual: true };
      }
      // Otherwise, just Actual (ignore the connector predicted on year-1)
      return { text: fmt(actual), isDual: false };
    }

    // For future years (> lastObservedYear), show Forecast (don’t echo the boundary forecast at lastObservedYear)
    return { text: fmt(forecast), isDual: false };
  };

  return (
    <div className="data-table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            <th className="sticky-col">Crime (Violation)</th>
            {years.map(y => (
              <th key={y} className="num">{y}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {legend.map(({ v, color, slug }) => (
            <tr key={slug}>
              <td className="sticky-col">
                <span className="v-name">
                  <span className="v-dot" style={{ background: color }} />
                  {v}
                </span>
              </td>
              {years.map(y => {
                const { text, isDual } = cellDisplay(slug, y);
                return (
                  <td key={y} className={`num ${isDual ? 'cell-dual' : ''}`}>{text}</td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="help" style={{ marginTop: 8 }}>
        • For 2024+ the table shows <strong>Forecast</strong>. For 2021–2023 backtests, the selected year cell shows <strong>Actual / Predicted</strong>.
      </div>
    </div>
  );
}
