import { useState } from "react";
import { useSimState } from "../state/SimulationContext.jsx";
import { METRO_STRUCTURE, SUBURBS } from "../data/metroStructure.js";
import { SCHOOLS } from "../data/directorates.js";

const BESIDE_METROPOLE = ["Cunicea", "Răduleni"];

// Every location's own K-12/lycee schools -- the universities (FlorTech,
// AgroFlor) get their own separate tab, since they're not part of this same
// tier: they answer to the national Ministry of Education, not the
// Prefecture's own decentralized education directorate.
export default function SchoolsTab() {
  const state = useSimState();
  const withinMetropole = [...Object.keys(METRO_STRUCTURE), ...SUBURBS.map((s) => s.name), "Ciripcău"];

  return (
    <>
      <p className="caption">
        Every location's own K-12/lycee schools, browsable in one place — purely descriptive, no cost
        or score effects. See the Universities tab for FlorTech and AgroFlor.
      </p>
      <p>
        <strong>Beside the metropole</strong>
      </p>
      {BESIDE_METROPOLE.map((name) => (
        <SchoolExpander key={name} name={name} />
      ))}
      {state.metroActive ? (
        <>
          <p>
            <strong>Within the metropole</strong>
          </p>
          {withinMetropole.map((name) => (
            <SchoolExpander key={name} name={name} />
          ))}
        </>
      ) : (
        <p className="caption">
          Establish the metropole (Scenario 1, option B) to see schools across the municipalities,
          suburbs, and Ciripcău too.
        </p>
      )}
    </>
  );
}

function SchoolExpander({ name }) {
  const [open, setOpen] = useState(false);
  const schools = SCHOOLS[name] || [];
  if (schools.length === 0) return null;
  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        {name} — {schools.length} schools
      </button>
      {open && (
        <ul className="suburb-list">
          {schools.map((s) => (
            <li key={s}>{s}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
