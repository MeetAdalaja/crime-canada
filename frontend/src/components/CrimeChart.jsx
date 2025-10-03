import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';


function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || payload.length === 0) return null;

  const actual = payload.find(p => p.dataKey === 'actual')?.value;
  const forecast = payload.find(p => p.dataKey === 'forecast')?.value;

  return (
    <div className="card mono" style={{ padding: 8 }}>
      <div><strong>Year:</strong> {label}</div>
      {actual != null && <div>Actual: {Math.round(actual).toLocaleString()}</div>}
      {forecast != null && <div>Forecast: {Math.round(forecast).toLocaleString()}</div>}
    </div>
  );
}




export default function CrimeChart({ data, lastObservedYear }) {
  // data: [{year, type: 'actual'|'forecast', value}]
  return (
    <div className="card">
      <div className="legend">
        <span className="badge">Ontario [35]</span>
        <span className="badge">Target: Actual_incidents</span>
      </div>
      <ResponsiveContainer width="100%" height={420}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="4 4" />
          <XAxis dataKey="year" />
          <YAxis />
          {/* <Tooltip /> */}
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          {/* Actual: solid */}
          <Line
            type="monotone"
            dataKey="actual"
            name="Actual"
            dot={true}
            strokeWidth={2}
            isAnimationActive={true}
          />
          {/* Forecast: semi-transparent */}
          <Line
            type="monotone"
            dataKey="forecast"
            name="Forecast"
            dot={true}
            strokeWidth={2}
            isAnimationActive={true}
            strokeOpacity={0.6}
          />
        </LineChart>
      </ResponsiveContainer>
      <div className="footer">
        <div>Method: History (solid) shows published counts up to {lastObservedYear}. Forecast (faded) is model-estimated using lagged incidents, not actuals.</div>
      </div>
    </div>
  );
}
