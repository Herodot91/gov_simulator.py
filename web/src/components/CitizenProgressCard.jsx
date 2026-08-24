import { useSimState } from "../state/SimulationContext.jsx";
import { METRO_STRUCTURE } from "../data/metroStructure.js";

function riskBadge(val) {
  if (val <= 33) return <span className="risk-badge risk-low">LOW RISK</span>;
  if (val <= 66) return <span className="risk-badge risk-medium">MEDIUM RISK</span>;
  return <span className="risk-badge risk-high">HIGH RISK</span>;
}

function Bar({ value, color }) {
  return (
    <div className="progress-bar-track">
      <div className="progress-bar-fill" style={{ width: `${value}%`, background: color }} />
    </div>
  );
}

export default function CitizenProgressCard() {
  const state = useSimState();
  const { Governance: g, Economy: e, Stability: s, Risk: r } = state.scores;
  const liveDot = state.autoplay ? "🟢" : "⚪";

  return (
    <div className="progress-card">
      <h4>{liveDot} Citizen Progress Card</h4>
      <div className="progress-tiles">
        <div className="progress-tile">Month: <b>{state.simMonth}</b></div>
        <div className="progress-tile">Budget: <b>{state.budget}</b></div>
        <div className="progress-tile">Municipalities: <b>{state.inaugurated.length}/{Object.keys(METRO_STRUCTURE).length}</b></div>
        <div className="progress-tile">Governance: <b>{g}</b></div>
        <div className="progress-tile">Economy: <b>{e}</b></div>
        <div className="progress-tile">Stability: <b>{s}</b></div>
        <div className="progress-tile">Risk: <b>{r}</b> {riskBadge(r)}</div>
      </div>
      <div className="progress-bar-label">Governance</div>
      <Bar value={g} color="#4cc9f0" />
      <div className="progress-bar-label">Economy</div>
      <Bar value={e} color="#48cae4" />
      <div className="progress-bar-label">Stability</div>
      <Bar value={s} color="#90e0ef" />
      <div className="progress-bar-label">Risk</div>
      <Bar value={r} color="#e63946" />
      <div className="progress-intl">🌐 Last Intl Reaction: {state.lastIntl || "—"}</div>
    </div>
  );
}
