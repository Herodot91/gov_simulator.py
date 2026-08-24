import { useSimState } from "../state/SimulationContext.jsx";

function Metric({ label, value, delta }) {
  const hasDelta = delta !== undefined && delta !== 0;
  const deltaClass = delta > 0 ? "metric-delta up" : "metric-delta down";
  return (
    <div className="metric">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      {hasDelta && <div className={deltaClass}>{delta > 0 ? `↑ ${delta}` : `↓ ${Math.abs(delta)}`}</div>}
      {!hasDelta && delta === 0 && <div className="metric-delta flat">0</div>}
    </div>
  );
}

export default function StatusRow() {
  const state = useSimState();
  const prev = state.history.length > 1 ? state.history[state.history.length - 2] : state.history[state.history.length - 1];
  const { scores } = state;

  return (
    <>
      <div className="status-row">
        <Metric label="🕒 Month" value={state.simMonth} />
        <Metric label="Governance" value={scores.Governance} delta={scores.Governance - prev.Governance} />
        <Metric label="Economy" value={scores.Economy} delta={scores.Economy - prev.Economy} />
        <Metric label="Stability" value={scores.Stability} delta={scores.Stability - prev.Stability} />
        <Metric label="Risk" value={scores.Risk} delta={scores.Risk - prev.Risk} />
      </div>
      <div className="budget-line">
        <strong>Budget Left:</strong> {state.budget} / {state.startBudget}
      </div>
    </>
  );
}
