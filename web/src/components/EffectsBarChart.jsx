const METRIC_COLORS = {
  Governance: "#1f77b4",
  Economy: "#ff7f0e",
  Stability: "#2ca02c",
  Risk: "#d62728",
};

const W = 280;
const ROW_H = 22;
const PAD = { top: 4, right: 42, bottom: 4, left: 84 };

// A small diverging bar chart of a resolved policy/project's own
// Governance/Economy/Stability/Risk deltas -- the "result" half of
// "result and explanation" once a card is resolved.
export default function EffectsBarChart({ effects }) {
  const entries = Object.entries(effects);
  if (entries.length === 0) return null;

  const maxAbs = Math.max(1, ...entries.map(([, v]) => Math.abs(v)));
  const innerW = W - PAD.left - PAD.right;
  const H = entries.length * ROW_H + PAD.top + PAD.bottom;
  const mid = PAD.left + innerW / 2;
  const scale = (v) => (v / maxAbs) * (innerW / 2);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="effects-chart" role="img" aria-label="Effects chart">
      {entries.map(([key, value], i) => {
        const y = PAD.top + i * ROW_H;
        const barW = Math.abs(scale(value));
        const x = value >= 0 ? mid : mid - barW;
        return (
          <g key={key}>
            <text
              x={PAD.left - 8}
              y={y + ROW_H / 2}
              textAnchor="end"
              dominantBaseline="middle"
              className="chart-axis-label"
            >
              {key}
            </text>
            <rect x={x} y={y + 3} width={barW} height={ROW_H - 8} fill={METRIC_COLORS[key] || "#888"} rx="2" />
            <text
              x={value >= 0 ? mid + barW + 4 : mid - barW - 4}
              y={y + ROW_H / 2}
              textAnchor={value >= 0 ? "start" : "end"}
              dominantBaseline="middle"
              className="chart-axis-label"
            >
              {value >= 0 ? `+${value}` : value}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
