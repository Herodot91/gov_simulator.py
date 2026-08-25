import { useState } from "react";
import { useSimState } from "../state/SimulationContext.jsx";
import { METRO_STRUCTURE } from "../data/metroStructure.js";
import {
  PREFECTURE_DIRECTORATES,
  PREFECTURE_TOWNS,
  METRO_COUNCIL_DIRECTORATES,
  MUNICIPALITY_DEPARTMENTS,
  districtOffice,
} from "../data/directorates.js";

// Every governance tier's own directorates/departments/civic offices, in
// one consolidated view -- the drill-down elsewhere in the app shows each
// tier only once you've navigated to it; this is the same data laid out
// flat, so a user can see the whole decentralized structure without
// clicking through every municipality and district one at a time.
export default function DirectoratesDashboard() {
  const state = useSimState();

  return (
    <>
      <p className="caption">
        Every governance tier's own directorates/departments/civic offices, in one place — purely
        descriptive, no cost or score effects.
      </p>

      <PrefectureDirectoratesExpander />
      {PREFECTURE_TOWNS.map((town) => (
        <TownCouncilExpander key={town.id} town={town} />
      ))}

      {state.metroActive ? (
        <>
          <MetroCouncilExpander />
          {Object.entries(METRO_STRUCTURE).map(([muniName, info]) => (
            <MunicipalityExpander key={muniName} muniName={muniName} info={info} />
          ))}
        </>
      ) : (
        <p className="caption">
          Establish the metropole (Scenario 1, option B) to see the Metropolitan Council and each
          municipality's own departments and district civic offices here too.
        </p>
      )}
    </>
  );
}

function PrefectureDirectoratesExpander() {
  const [open, setOpen] = useState(false);
  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        🏛️ Florești Prefecture — Directorates ({PREFECTURE_DIRECTORATES.length})
      </button>
      {open && (
        <div className="technopolis-body">
          <p className="caption">
            The French-style prefecture's own deconcentrated state administration, in effect
            regardless of whether the metropole has been established — the state tier the metropole is
            carved out of.
          </p>
          <ul className="suburb-list">
            {PREFECTURE_DIRECTORATES.map((d) => (
              <li key={d.name}>
                <strong>{d.name}</strong> — {d.mandate}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function MetroCouncilExpander() {
  const [open, setOpen] = useState(false);
  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        🏢 Metropolitan Council — Directorates ({METRO_COUNCIL_DIRECTORATES.length})
      </button>
      {open && (
        <ul className="suburb-list">
          {METRO_COUNCIL_DIRECTORATES.map((d) => (
            <li key={d.name}>
              <strong>{d.name}</strong> — {d.mandate}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function TownCouncilExpander({ town }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        🏘️ {town.name} Town Council ({town.council.length})
      </button>
      {open && (
        <ul className="suburb-list">
          {town.council.map((d) => (
            <li key={d.name}>
              <strong>{d.name}</strong> — {d.mandate}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function MunicipalityExpander({ muniName, info }) {
  const [open, setOpen] = useState(false);
  const depts = MUNICIPALITY_DEPARTMENTS[muniName];
  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        🏢 {muniName} — {depts.length} departments, {info.districts.length} district offices
      </button>
      {open && (
        <div className="technopolis-body">
          <ul className="suburb-list">
            {depts.map((d) => (
              <li key={d.name}>
                <strong>{d.name}</strong> — {d.mandate}
              </li>
            ))}
          </ul>
          <p className="caption">
            <strong>District Civic Offices</strong>
          </p>
          <ul className="suburb-list">
            {info.districts.map((dist) => {
              const office = districtOffice(muniName, dist);
              return <li key={dist}>{office.name}</li>;
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
