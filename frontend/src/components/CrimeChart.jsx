import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, Legend, ReferenceArea
} from 'recharts';

/**
 * Custom tooltip that:
 * - Always shows Year
 * - Shows Actual / Forecast normally, EXCEPT hides Forecast at the boundary year (lastObservedYear)
 * - Shows "Predicted (selected year)" ONLY on the selected year (not on the connector year-1)
 */
function CustomTooltip({ active, payload, label, selectedYear, lastObservedYear }) {
  if (!active || !payload?.length) return null;

  const yr = Number(label);

  // Filter rules:
  // 1) Hide the duplicated forecast connector at the boundary (yr === lastObservedYear)
  // 2) Hide the duplicated predicted connector at (selectedYear - 1)
  const filtered = payload.filter((p) => {
    if (p?.value == null) return false;
    if (p?.dataKey === 'forecast' && yr === Number(lastObservedYear)) return false;
    if (p?.dataKey === 'predicted' && yr !== Number(selectedYear)) return false;
    return true;
  });

  if (!filtered.length) return null;

  return (
    <div className="card mono" style={{ padding: 8 }}>
      <div><strong>Year:</strong> {label}</div>
      {filtered.map((p) => (
        <div key={p.dataKey}>
          {p.name}: {Math.round(p.value).toLocaleString()}
        </div>
      ))}
    </div>
  );
}

export default function CrimeChart({
  data,               // [{year, actual, forecast, predicted}]
  xMin,
  xMax,
  lastObservedYear,   // e.g., 2023
  showForecastRegion, // boolean
  selectedYear,       // year chosen in the UI
  predMeta,           // optional backtest meta
}) {
  // Hide the dot at the boundary for the forecast line so you don't see a duplicate dot at 2023
  const ForecastDot = (props) => {
    const { cx, cy, payload } = props;
    if (!payload || payload.year === Number(lastObservedYear)) return null; // hide boundary dot
    return <circle cx={cx} cy={cy} r={3} />;
  };

  return (
    <div className="card">
      <div className="legend">
        <span className="badge">Ontario [35]</span>
        <span className="badge">Target: Actual_incidents</span>
      </div>

      <ResponsiveContainer width="100%" height={420}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="4 4" />
          <XAxis type="number" dataKey="year" domain={[xMin, xMax]} tickFormatter={(y) => `${y}`} />
          <YAxis />
          {/* Pass both selectedYear and lastObservedYear so the tooltip can filter properly */}
          <Tooltip content={(props) => (
            <CustomTooltip
              {...props}
              selectedYear={selectedYear}
              lastObservedYear={lastObservedYear}
            />
          )} />
          <Legend />

          {/* Shaded forecast region (only when horizon > lastObservedYear) */}
          {showForecastRegion && lastObservedYear != null && (
            <ReferenceArea x1={lastObservedYear} x2={xMax} fillOpacity={0.07} />
          )}

          {/* Actual line */}
          <Line
            type="monotone"
            dataKey="actual"
            name="Actual"
            dot={{ r: 3 }}
            strokeWidth={2}
            isAnimationActive={false}
          />

          {/* Forecast line (connected via duplicated boundary value at lastObservedYear) */}
          <Line
            type="monotone"
            dataKey="forecast"
            name="Forecast"
            stroke="#ffffffff"           // line color
            dot={<ForecastDot />}
            activeDot={{ r: 5, fill: "#ffffffff", stroke: "#ffffffff" }} // hover dot (optional)
            strokeWidth={2}
            strokeOpacity={0.9}
            strokeDasharray="6 6"
            isAnimationActive={false}
            connectNulls
          />

          {/* Backtest short segment (only two points populated) */}
          <Line
            type="monotone"
            dataKey="predicted"
            name="Predicted (selected year)"
            stroke="#f97316"           // line color
            strokeWidth={2}
            strokeOpacity={0.9}
            strokeDasharray="2 8"
            dot={{ r: 4, fill: "#f97316", stroke: "#f97316" }}  // dot color
            activeDot={{ r: 5, fill: "#f97316", stroke: "#f97316" }} // hover dot (optional)
            isAnimationActive={false}
            connectNulls
          />

        </LineChart>
      </ResponsiveContainer>

      {/* Context footer */}
      {predMeta?.year && predMeta?.yhat != null ? (
        <div className="footer">
          Backtest for <strong>{predMeta.year}</strong>:
          {' '}Predicted {Math.round(predMeta.yhat).toLocaleString()}
          {predMeta.actual != null && <> · Actual {Math.round(predMeta.actual).toLocaleString()}</>}
          {predMeta.train_upto_year && <> · Trained on ≤ {predMeta.train_upto_year}</>}
        </div>
      ) : (
        <div className="footer">
          History (solid) shows published counts up to {lastObservedYear}. Shaded region is forecast using lagged incidents (no unemployment).
        </div>
      )}
    </div>
  );
}
