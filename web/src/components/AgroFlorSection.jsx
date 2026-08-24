import { useSimState, useSimActions } from "../state/SimulationContext.jsx";
import { AGROFLOR } from "../data/agroflor.js";

export default function AgroFlorSection() {
  const state = useSimState();
  const actions = useSimActions();

  return (
    <section className="panel">
      <h3>🌾 AgroFlor — Florești University of Agricultural Sciences and Technologies</h3>
      {!state.metroActive ? (
        <div className="callout callout-info">
          AgroFlor's campuses come online once the metropole is established (Scenario 1, option B).
        </div>
      ) : state.selectedAgroCampus === null ? (
        <CampusList actions={actions} />
      ) : (
        <CampusDetail campusId={state.selectedAgroCampus} actions={actions} />
      )}
    </section>
  );
}

function CampusList({ actions }) {
  return (
    <>
      <p className="caption">{AGROFLOR.origin}</p>
      <p className="hint">👆 Click a campus for its faculties, departments, research centers, and programs:</p>
      <div className="muni-grid">
        {AGROFLOR.campuses.map((campus) => (
          <button
            key={campus.id}
            className="btn btn-select"
            onClick={() => actions.selectAgroCampus(campus.id)}
          >
            {campus.name}
          </button>
        ))}
      </div>
    </>
  );
}

function CampusDetail({ campusId, actions }) {
  const campus = AGROFLOR.campuses.find((c) => c.id === campusId);
  return (
    <>
      <button className="btn btn-back" onClick={() => actions.selectAgroCampus(null)}>
        ← Back to AgroFlor
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
      <div className="technopolis-body">
        <h4>🔬 Research Centers &amp; Labs</h4>
        <ul className="suburb-list">
          {campus.researchCenters.map((center) => (
            <li key={center}>{center}</li>
          ))}
        </ul>
      </div>
    </>
  );
}
