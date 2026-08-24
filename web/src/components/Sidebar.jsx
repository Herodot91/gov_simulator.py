import { useState } from "react";
import { useSimState, useSimActions } from "../state/SimulationContext.jsx";

export default function Sidebar() {
  const state = useSimState();
  const actions = useSimActions();
  const [startBudgetInput, setStartBudgetInput] = useState(state.startBudget);

  return (
    <aside className="sidebar">
      <div className="field-group">
        <div className="field-label">Mode</div>
        <label className="radio-row">
          <input
            type="radio"
            name="mode"
            checked={state.mode === "Democracy"}
            onChange={() => actions.setMode("Democracy")}
          />
          Democracy
        </label>
        <label className="radio-row">
          <input
            type="radio"
            name="mode"
            checked={state.mode === "Autocracy"}
            onChange={() => actions.setMode("Autocracy")}
          />
          Autocracy
        </label>
      </div>

      <div className="field-group">
        <div className="field-label">
          Starting Budget (units) <span className="field-value">{startBudgetInput}</span>
        </div>
        <input
          type="range"
          min="0"
          max="150"
          step="5"
          value={startBudgetInput}
          onChange={(e) => setStartBudgetInput(Number(e.target.value))}
          className="slider"
        />
      </div>

      <button className="btn btn-primary" onClick={() => actions.reset(startBudgetInput)}>
        🔄 New Simulation
      </button>

      <hr className="divider" />

      <div className="field-label muted">Real-time clock</div>
      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={state.autoplay}
          onChange={(e) => actions.setAutoplay(e.target.checked)}
        />
        ▶️ Live auto-play (world keeps moving)
      </label>

      <div className="field-group">
        <div className="field-label">
          Tick speed (seconds) <span className="field-value">{state.tickInterval}</span>
        </div>
        <input
          type="range"
          min="1"
          max="10"
          step="1"
          value={state.tickInterval}
          onChange={(e) => actions.setTickInterval(Number(e.target.value))}
          className="slider"
        />
      </div>

      {state.autoplay ? (
        <div className="callout callout-success">🟢 LIVE — simulation is ticking on its own.</div>
      ) : (
        <div className="callout callout-info">⏸ Paused — nothing advances until you act or resume auto-play.</div>
      )}
    </aside>
  );
}
