import { SCENARIOS } from "../data/scenarios.js";
import { useSimState, useSimActions, fmtEffects } from "../state/SimulationContext.jsx";

export default function ScenarioPanel() {
  const state = useSimState();
  const actions = useSimActions();

  if (state.turn < SCENARIOS.length) {
    const s = SCENARIOS[state.turn];
    const optItems = Object.entries(s.options);
    return (
      <section className="panel">
        <h3>📘 Scenario {state.turn + 1}: {s.title}</h3>
        <p className="caption">{s.intl}</p>
        <div className="option-grid">
          {optItems.map(([k, [desc, effects, cost]]) => (
            <button
              key={k}
              className="btn btn-option"
              onClick={() => actions.resolveScenario(s, k)}
            >
              <span className="option-desc">{k}) {desc}</span>
              <span className="option-meta">Cost {cost} | {fmtEffects(effects)}</span>
            </button>
          ))}
          <button className="btn btn-option btn-skip" onClick={() => actions.resolveScenario(s, null)}>
            ⏭️ Skip
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="panel">
      <h3>🌐 Ongoing Governance</h3>
      <p className="caption">All scripted decisions are resolved. The world keeps evolving live via random events.</p>
      <button className="btn btn-primary" onClick={() => actions.triggerRandomTick()}>
        ⚡ Trigger next event now
      </button>
    </section>
  );
}
