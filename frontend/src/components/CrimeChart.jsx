// import {
//   LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
//   CartesianGrid, Legend, ReferenceArea
// } from 'recharts';

// /**
//  * Custom tooltip that:
//  * - Always shows Year
//  * - Shows Actual / Forecast normally, EXCEPT hides Forecast at the boundary year (lastObservedYear)
//  * - Shows "Predicted (selected year)" ONLY on the selected year (not on the connector year-1)
//  */
// function CustomTooltip({ active, payload, label, selectedYear, lastObservedYear }) {
//   if (!active || !payload?.length) return null;

//   const yr = Number(label);

//   // Filter rules:
//   // 1) Hide the duplicated forecast connector at the boundary (yr === lastObservedYear)
//   // 2) Hide the duplicated predicted connector at (selectedYear - 1)
//   const filtered = payload.filter((p) => {
//     if (p?.value == null) return false;
//     if (p?.dataKey === 'forecast' && yr === Number(lastObservedYear)) return false;
//     if (p?.dataKey === 'predicted' && yr !== Number(selectedYear)) return false;
//     return true;
//   });

//   if (!filtered.length) return null;

//   return (
//     <div className="card mono" style={{ padding: 8 }}>
//       <div><strong>Year:</strong> {label}</div>
//       {filtered.map((p) => (
//         <div key={p.dataKey}>
//           {p.name}: {Math.round(p.value).toLocaleString()}
//         </div>
//       ))}
//     </div>
//   );
// }

// export default function CrimeChart({
//   data,               // [{year, actual, forecast, predicted}]
//   xMin,
//   xMax,
//   lastObservedYear,   // e.g., 2023
//   showForecastRegion, // boolean
//   selectedYear,       // year chosen in the UI
//   predMeta,           // optional backtest meta
// }) {
//   // Hide the dot at the boundary for the forecast line so you don't see a duplicate dot at 2023
//   const ForecastDot = (props) => {
//     const { cx, cy, payload } = props;
//     if (!payload || payload.year === Number(lastObservedYear)) return null; // hide boundary dot
//     return <circle cx={cx} cy={cy} r={3} />;
//   };

//   return (
//     <div className="card">
//       <div className="legend">
//         <span className="badge">Ontario [35]</span>
//         <span className="badge">Target: Actual_incidents</span>
//       </div>

//       <ResponsiveContainer width="100%" height={420}>
//         <LineChart data={data}>
//           <CartesianGrid strokeDasharray="4 4" />
//           <XAxis type="number" dataKey="year" domain={[xMin, xMax]} tickFormatter={(y) => `${y}`} />
//           <YAxis />
//           {/* Pass both selectedYear and lastObservedYear so the tooltip can filter properly */}
//           <Tooltip content={(props) => (
//             <CustomTooltip
//               {...props}
//               selectedYear={selectedYear}
//               lastObservedYear={lastObservedYear}
//             />
//           )} />
//           <Legend />

//           {/* Shaded forecast region (only when horizon > lastObservedYear) */}
//           {showForecastRegion && lastObservedYear != null && (
//             <ReferenceArea x1={lastObservedYear} x2={xMax} fillOpacity={0.07} />
//           )}

//           {/* Actual line */}
//           <Line
//             type="monotone"
//             dataKey="actual"
//             name="Actual"
//             dot={{ r: 3 }}
//             strokeWidth={2}
//             isAnimationActive={false}
//           />

//           {/* Forecast line (connected via duplicated boundary value at lastObservedYear) */}
//           <Line
//             type="monotone"
//             dataKey="forecast"
//             name="Forecast"
//             stroke="#ffffffff"           // line color
//             dot={<ForecastDot />}
//             activeDot={{ r: 5, fill: "#ffffffff", stroke: "#ffffffff" }} // hover dot (optional)
//             strokeWidth={2}
//             strokeOpacity={0.9}
//             strokeDasharray="6 6"
//             isAnimationActive={false}
//             connectNulls
//           />

//           {/* Backtest short segment (only two points populated) */}
//           <Line
//             type="monotone"
//             dataKey="predicted"
//             name="Predicted (selected year)"
//             stroke="#f97316"           // line color
//             strokeWidth={2}
//             strokeOpacity={0.9}
//             strokeDasharray="2 8"
//             dot={{ r: 4, fill: "#f97316", stroke: "#f97316" }}  // dot color
//             activeDot={{ r: 5, fill: "#f97316", stroke: "#f97316" }} // hover dot (optional)
//             isAnimationActive={false}
//             connectNulls
//           />

//         </LineChart>
//       </ResponsiveContainer>

//       {/* Context footer */}
//       {predMeta?.year && predMeta?.yhat != null ? (
//         <div className="footer">
//           Backtest for <strong>{predMeta.year}</strong>:
//           {' '}Predicted {Math.round(predMeta.yhat).toLocaleString()}
//           {predMeta.actual != null && <> · Actual {Math.round(predMeta.actual).toLocaleString()}</>}
//           {predMeta.train_upto_year && <> · Trained on ≤ {predMeta.train_upto_year}</>}
//         </div>
//       ) : (
//         <div className="footer">
//           History (solid) shows published counts up to {lastObservedYear}. Shaded region is forecast using lagged incidents (no unemployment).
//         </div>
//       )}
//     </div>
//   );
// }




import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, ReferenceArea
} from 'recharts';

// Parse "actual_<slug>", "forecast_<slug>", "predicted_<slug>"
function parseKey(k) {
  const m = /^(actual|forecast|predicted)_(.+)$/.exec(k || "");
  if (!m) return null;
  return { kind: m[1], slug: m[2] };
}

/**
 * Custom tooltip:
 * - Always shows Year
 * - For each violation, shows Actual
 * - Shows Forecast except at boundary (lastObservedYear)
 * - Shows Predicted ONLY on selectedYear (not on connector at selectedYear-1)
 */
function CustomTooltip({ active, payload, label, lastObservedYear, selectedYear, legend }) {
  if (!active || !payload?.length) return null;
  const yr = Number(label);

  // Build a map: slug -> { name, color, rows[{label, value}] }
  const metaBySlug = new Map(legend.map(l => [l.slug, l]));
  const bySlug = new Map();

  for (const p of payload) {
    const key = p?.dataKey;
    const val = p?.value;
    if (val == null) continue;

    const info = parseKey(key);
    if (!info) continue;
    const { kind, slug } = info;
    const meta = metaBySlug.get(slug);
    if (!meta) continue;

    // Filter out boundary forecast & connector predicted
    if (kind === "forecast" && yr === Number(lastObservedYear)) continue;
    if (kind === "predicted" && yr !== Number(selectedYear)) continue;

    if (!bySlug.has(slug)) bySlug.set(slug, { name: meta.v, color: meta.color, rows: [] });
    const labelTxt =
      kind === "actual" ? "Actual"
      : kind === "forecast" ? "Forecast"
      : "Predicted (selected year)";
    bySlug.get(slug).rows.push({ label: labelTxt, value: val });
  }

  const groups = Array.from(bySlug.values());
  if (!groups.length) return null;

  return (
    <div className="card mono" style={{ padding: 8, maxWidth: 360 }}>
      <div><strong>Year:</strong> {label}</div>
      {groups.map(g => (
        <div key={g.name} style={{ marginTop: 6 }}>
          <div style={{ display:'flex', alignItems:'center', gap:6 }}>
            <span style={{
              width:10, height:10, borderRadius:50, background:g.color, border:'1px solid #0003'
            }} />
            <strong>{g.name}</strong>
          </div>
          {g.rows.map((r,i) => (
            <div key={i} style={{ marginLeft:16 }}>
              {r.label}: {Math.round(r.value).toLocaleString()}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

export default function CrimeChart({
  data,              // rows: [{year, actual_<slug>, forecast_<slug>, predicted_<slug>, ...}]
  legend,            // [{v,color,slug}]
  xMin, xMax,
  lastObservedYear,  // int (e.g., 2023)
  selectedYear,      // int
}) {
  // Draw shaded region only when selectedYear > boundary
  const showForecastRegion = selectedYear > Number(lastObservedYear);

  // Custom dot renderers to hide connector dots
  const ForecastDot = ({ cx, cy, payload, dataKey }) => {
    // hide the boundary dot at lastObservedYear for ANY forecast series
    if (payload?.year === Number(lastObservedYear)) return null;
    return <circle cx={cx} cy={cy} r={3} />;
  };
  const PredictedDot = ({ cx, cy, payload }) => {
    // show predicted dot only on the selectedYear (hide connector at selectedYear-1)
    if (payload?.year !== Number(selectedYear)) return null;
    return <circle cx={cx} cy={cy} r={4} />;
  };

  return (
    <div className="card">
      <ResponsiveContainer width="100%" height={460}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="4 4" />
          <XAxis type="number" dataKey="year" domain={[xMin, xMax]} tickFormatter={(y) => `${y}`} />
          <YAxis />
          <Tooltip content={(props) => (
            <CustomTooltip
              {...props}
              legend={legend}
              lastObservedYear={lastObservedYear}
              selectedYear={selectedYear}
            />
          )} />

          {/* Shaded forecast region */}
          {showForecastRegion && lastObservedYear != null && (
            <ReferenceArea x1={lastObservedYear} x2={xMax} fillOpacity={0.07} />
          )}

          {/* Lines per violation */}
          {legend.map(({ slug, color, v }) => (
            <g key={slug}>
              {/* Actual (solid) */}
              <Line
                type="monotone"
                dataKey={`actual_${slug}`}
                stroke={color}
                name={`${v} — Actual`}
                dot={{ r: 3 }}
                strokeWidth={2}
                isAnimationActive={false}
                connectNulls
              />
              {/* Forecast (dashed, same color) */}
              <Line
                type="monotone"
                dataKey={`forecast_${slug}`}
                stroke={color}
                name={`${v} — Forecast`}
                dot={<ForecastDot />}
                strokeWidth={2}
                strokeDasharray="6 6"
                strokeOpacity={0.95}
                isAnimationActive={false}
                connectNulls
              />
              {/* Predicted (backtest short segment, only two points populated) */}
              <Line
                type="monotone"
                dataKey={`predicted_${slug}`}
                stroke={color}
                name={`${v} — Predicted`}
                dot={<PredictedDot />}
                strokeWidth={2}
                strokeDasharray="2 8"
                strokeOpacity={0.95}
                isAnimationActive={false}
                connectNulls
              />
            </g>
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
