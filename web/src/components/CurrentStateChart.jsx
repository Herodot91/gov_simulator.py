const METRICS = [
  { key: "Governance", color: "#1f77b4" },
  { key: "Economy", color: "#ff7f0e" },
  { key: "Stability", color: "#2ca02c" },
  { key: "Risk", color: "#d62728" },
];

const W = 640;
const ROW_H = 46;
const PAD = { top: 10, right: 50, bottom: 10, left: 110 };

// The "big graph" at the top of Policy Simulation: current Governance/
// Economy/Stability/Risk scores, at a glance, before picking a policy.
export default function CurrentStateChart({ scores }) {
  const innerW = W - PAD.left - PAD.right;
  const H = METRICS.length * ROW_H + PAD.top + PAD.bottom;
  const scale = (v) => (v / 100) * innerW;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="big-chart" role="img" aria-label="Current state chart">
      {METRICS.map((m, i) => {
        const y = PAD.top + i * ROW_H;
        const barW = scale(scores[m.key]);
        return (
          <g key={m.key}>
            <text
              x={PAD.left - 10}
              y={y + ROW_H / 2}
              textAnchor="end"
              dominantBaseline="middle"
              className="big-chart-label"
            >
              {m.key}
            </text>
            <rect x={PAD.left} y={y + 8} width={innerW} height={ROW_H - 16} fill="#eef1f5" rx="4" />
            <rect x={PAD.left} y={y + 8} width={barW} height={ROW_H - 16} fill={m.color} rx="4" />
            <text
              x={PAD.left + barW + 8}
              y={y + ROW_H / 2}
              dominantBaseline="middle"
              className="big-chart-value"
            >
              {scores[m.key]}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
