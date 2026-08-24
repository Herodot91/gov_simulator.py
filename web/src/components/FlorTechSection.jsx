import { useState } from "react";
import { useSimState, useSimActions } from "../state/SimulationContext.jsx";
import { FLORTECH } from "../data/flortech.js";

export default function FlorTechSection() {
  const state = useSimState();
  const actions = useSimActions();

  return (
    <section className="panel">
      <h3>🎓 FlorTech — Florești University of Technology</h3>
      {!state.metroActive ? (
        <div className="callout callout-info">
          FlorTech's campuses come online once the metropole is established (Scenario 1, option B).
        </div>
      ) : state.selectedCampus === null ? (
        <CampusList actions={actions} />
      ) : (
        <CampusDetail campusId={state.selectedCampus} actions={actions} />
      )}
    </section>
  );
}

function CampusList({ actions }) {
  return (
    <>
      <p className="caption">{FLORTECH.origin}</p>
      <p className="hint">👆 Click a campus for its faculties, departments, and programs:</p>
      <div className="muni-grid">
        {FLORTECH.campuses.map((campus) => (
          <button
            key={campus.id}
            className="btn btn-select"
            onClick={() => actions.selectCampus(campus.id)}
          >
            {campus.name}
          </button>
        ))}
      </div>

      <VocationalExpander />
    </>
  );
}

function CampusDetail({ campusId, actions }) {
  const campus = FLORTECH.campuses.find((c) => c.id === campusId);
  return (
    <>
      <button className="btn btn-back" onClick={() => actions.selectCampus(null)}>
        ← Back to FlorTech
      </button>
      <h3 className="muni-heading">{campus.name}</h3>
      <p className="caption">
        {campus.location} · Degree levels: {campus.levels.join(", ")}
      </p>
      {campus.faculties.map((fac) => (
        <div key={fac.name} className="technopolis-body">
          <h4>{fac.name}</h4>
          <ul className="suburb-list">
            {fac.departments.map((dept) => (
              <li key={dept}>
                <strong>{dept}</strong> — {campus.levels.join(", ")}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </>
  );
}

function VocationalExpander() {
  const [open, setOpen] = useState(false);
  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        🛠️ Vocational Institutes ({FLORTECH.vocationalInstitutes.length}) — Școala Profesională legacy
        tracks, kept alongside FlorTech
      </button>
      {open && (
        <ul className="suburb-list">
          {FLORTECH.vocationalInstitutes.map((inst) => (
            <li key={inst.id}>
              <strong>{inst.name}</strong> — {inst.location}
              <br />
              <span className="caption">{inst.tracks.join(", ")}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
