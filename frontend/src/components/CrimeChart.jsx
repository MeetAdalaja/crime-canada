import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, Legend, ReferenceArea
} from 'recharts';

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const line = payload[0];
  const seriesName = line?.name || '';
  const value = line?.value;
  return (
    <div className="card mono" style={{ padding: 8 }}>
      <div><strong>Year:</strong> {label}</div>
      <div>{seriesName}: {Math.round(value).toLocaleString()}</div>
    </div>
  );
}

export default function CrimeChart({ actualSeries, forecastSeries, lastObservedYear, maxYear }) {
  // Merge for the x-axis domain (we’ll render two separate <Line>s)
  const allYears = [...actualSeries, ...forecastSeries].map(d => d.year);
  const xMin = Math.min(...allYears);
  const xMax = Math.max(...allYears);

  return (
    <div className="card">
      <div className="legend">
        <span className="badge">Ontario [35]</span>
        <span className="badge">Target: Actual_incidents</span>
      </div>

      <ResponsiveContainer width="100%" height={420}>
        <LineChart>
          <CartesianGrid strokeDasharray="4 4" />
          <XAxis type="number" dataKey="year" domain={[xMin, xMax]} tickFormatter={(y) => `${y}`} />
          <YAxis />
          <Tooltip content={<CustomTooltip />} />
          <Legend />

          {/* Shaded forecast region */}
          {lastObservedYear != null && maxYear && maxYear > lastObservedYear && (
            <ReferenceArea x1={lastObservedYear} x2={maxYear} fillOpacity={0.07} />
          )}

          {/* Actual line (solid) */}
          <Line
            data={actualSeries}
            type="monotone"
            dataKey="value"
            name="Actual"
            dot={{ r: 3 }}
            strokeWidth={2}
            isAnimationActive={true}
          />

          {/* Forecast line (dashed, semi-opaque) – starts with duplicated boundary point so it connects */}
          <Line
            data={forecastSeries}
            type="monotone"
            dataKey="value"
            name="Forecast"
            dot={{ r: 3 }}
            strokeWidth={2}
            strokeOpacity={0.8}
            strokeDasharray="6 6"
            isAnimationActive={true}
          />
        </LineChart>
      </ResponsiveContainer>

      <div className="footer">
        <div>
          Left of the shaded region: <strong>Actuals</strong> (published). Inside the shaded region: <strong>Forecast</strong> (model estimates using lagged incidents).
        </div>
      </div>
    </div>
  );
}
