import { useSimState } from "../state/SimulationContext.jsx";

const SERIES = [
  { key: "Governance", color: "#1f77b4" },
  { key: "Economy", color: "#ff7f0e" },
  { key: "Stability", color: "#2ca02c" },
  { key: "Risk", color: "#d62728" },
];

const W = 700;
const H = 300;
const PAD = { top: 20, right: 20, bottom: 40, left: 44 };

export default function ScoreChart() {
  const state = useSimState();
  const { history, monthLabels } = state;

  const innerW = W - PAD.left - PAD.right;
  const innerH = H - PAD.top - PAD.bottom;
  const n = history.length;
  const xFor = (i) => (n <= 1 ? 0 : (i / (n - 1)) * innerW);
  const yFor = (v) => innerH - (v / 100) * innerH;

  const gridLines = [0, 25, 50, 75, 100];

  return (
    <div className="chart-wrap">
      <div className="chart-title">Score Evolution (live)</div>
      <svg viewBox={`0 0 ${W} ${H}`} className="chart-svg" role="img" aria-label="Score evolution chart">
        <g transform={`translate(${PAD.left},${PAD.top})`}>
          {gridLines.map((g) => (
            <g key={g}>
              <line x1={0} x2={innerW} y1={yFor(g)} y2={yFor(g)} className="chart-grid" />
              <text x={-8} y={yFor(g)} className="chart-axis-label" textAnchor="end" dominantBaseline="middle">
                {g}
              </text>
            </g>
          ))}
          {monthLabels.map((label, i) => {
            if (n > 8 && i % Math.ceil(n / 8) !== 0 && i !== n - 1) return null;
            return (
              <text key={i} x={xFor(i)} y={innerH + 20} className="chart-axis-label" textAnchor="middle">
                {label}
              </text>
            );
          })}
          {SERIES.map((s) => {
            const points = history.map((row, i) => `${xFor(i)},${yFor(row[s.key])}`).join(" ");
            return (
              <g key={s.key}>
                <polyline points={points} fill="none" stroke={s.color} strokeWidth="2" />
                {history.map((row, i) => (
                  <circle key={i} cx={xFor(i)} cy={yFor(row[s.key])} r="3" fill={s.color} />
                ))}
              </g>
            );
          })}
        </g>
      </svg>
      <div className="chart-legend">
        {SERIES.map((s) => (
          <span key={s.key} className="chart-legend-item">
            <span className="chart-legend-swatch" style={{ background: s.color }} />
            {s.key}
          </span>
        ))}
      </div>
    </div>
  );
}
