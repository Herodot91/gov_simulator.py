import { useState } from "react";
import { useSimState, useSimActions } from "../state/SimulationContext.jsx";
import { METRO_STRUCTURE, SUBURBS, INAUGURATION_COST, TECHNOPOLIS_OKRUGS } from "../data/metroStructure.js";
import { METRO_PROJECTS, MUNICIPALITY_PROJECTS, DISTRICT_PROJECTS, districtProjectKey } from "../data/projects.js";
import { SCENARIOS } from "../data/scenarios.js";
import { PREFECTURE_POLICIES, PREFECTURE_TOWNS, TOWN_POLICIES } from "../data/directorates.js";
import { findLocality } from "./MetroMap.jsx";
import { useLocalities } from "./useLocalities.js";
import CbdMasterplan from "./CbdMasterplan.jsx";

// The governance hierarchy itself, with its click-to-drill-down navigation
// -- every tier's own org chart (directorates, departments, civic offices)
// lives in the separate Directorates tab, and every policy/project actually
// gets DECIDED in the separate Policy Simulation tab (with its own big
// graph); this tab only explains the structure and shows each policy's
// status read-only, so the two tabs stay distinct instead of duplicating
// the same decision UI.
export default function GovernanceStructure() {
  const state = useSimState();
  const localities = useLocalities();

  return (
    <>
      <p>
        Florești's governance is explained top to bottom, Prefecture down to Municipality/District/
        Town, as <strong>three borrowed models layered on top of each other</strong> rather than one
        uniform system:
      </p>
      <ol className="governance-hierarchy">
        <li>
          🇫🇷 <strong>Prefecture</strong> — the outer tier, a real French-style <em>deconcentrated</em>{" "}
          state administration (a reframing of Raionul Florești). Always in effect, whether or not the
          metropole below has been established.
        </li>
        <li>
          🏙️ <strong>Metropole</strong> — carved out <em>within</em> the Prefecture, this tier is
          genuinely <strong>mixed decentralization</strong>, combining three different real-world
          models at once:
          <ul>
            <li>
              🇹🇷 <strong>Istanbul's ilçe</strong> + 🇭🇺 <strong>Budapest's kerület</strong> — the
              metropolitan tier itself, governing 4 <strong>Municipalities</strong>, each inaugurated
              separately and each split into its own 4 <strong>Districts</strong> (16 total).
            </li>
            <li>
              🇷🇺 <strong>Moscow's Zelenograd</strong> — the <strong>Technopolis Okrugs</strong> (Prajila,
              Ciripcău), detached single-industry okrugs administratively sponsored by the metropole
              rather than ordinary municipalities.
            </li>
            <li>
              <strong>Suburbs</strong> stay administratively dependent on the metropole, with no local
              government of their own.
            </li>
          </ul>
        </li>
        <li>
          🏘️ <strong>Prefecture Towns</strong> — Cunicea and Răduleni sit <em>alongside</em> the
          Metropole, not under it: real French-model small towns directly under the Prefecture, each
          with its own town council.
        </li>
      </ol>

      {!state.metroActive ? (
        <div className="callout callout-info">
          Choose <strong>B) Establish Florești Metropole</strong> in Scenario 1 to activate the
          Metropole tier described above.
        </div>
      ) : (
        <p className="caption">
          Click a municipality below (or on the Map tab) to drill down into its districts. See the
          Directorates tab for every tier's own org chart, and the Policy Simulation tab to actually
          decide any of the policies mentioned below.
        </p>
      )}

      <PrefecturePolicies />

      {state.metroActive && <DrillDown localities={localities} />}

      {/* A third branch under the Prefecture, alongside the Metropole (with
          its Suburbs and Technopolis Okrugs) above: same governance scheme
          top to bottom -- Prefecture, then the Metropole (drill down into
          its municipalities/districts by clicking), then the Prefecture's
          two towns. */}
      <PrefectureTowns />
    </>
  );
}

// Read-only status for a policy/project -- shown in this tab, which
// explains structure and navigation but doesn't resolve decisions itself;
// resolve from the Policy Simulation tab, which every card here points to.
function ReadOnlyProject({ project }) {
  const state = useSimState();
  const resolved = state.resolvedProjects[project.id];
  return (
    <p className="readonly-project">
      <strong>{project.title}</strong> —{" "}
      {resolved == null ? (
        <>
          not yet decided <em>(see the Policy Simulation tab)</em>
        </>
      ) : resolved.choice === null ? (
        "⏭️ Skipped"
      ) : (
        `✅ ${resolved.choice}) ${resolved.label}`
      )}
    </p>
  );
}

function DrillDown({ localities }) {
  const state = useSimState();
  const actions = useSimActions();
  const selMuni = state.selectedMunicipality;
  const selDist = state.selectedDistrict;

  if (selMuni === null) {
    return (
      <>
        <p className="hint">👆 Click a municipality to see its 4 districts.</p>
        <div className="muni-grid">
          {Object.keys(METRO_STRUCTURE).map((name) => {
            const active = state.inaugurated.includes(name);
            return (
              <button key={name} className="btn btn-select" onClick={() => actions.selectMunicipality(name)}>
                {name} {active ? "✅" : ""}
              </button>
            );
          })}
        </div>

        <SuburbsExpander localities={localities} />
        <TechnopolisExpander localities={localities} />
        <CurrentPolicies />

        <h4>🏗️ Metropolitan Projects</h4>
        {METRO_PROJECTS.map((p) => (
          <ReadOnlyProject key={p.id} project={p} />
        ))}
      </>
    );
  }

  const info = METRO_STRUCTURE[selMuni];
  const active = state.inaugurated.includes(selMuni);
  const anchor = localities ? findLocality(localities, info.anchor) : null;

  if (selDist === null) {
    const muniProjects = MUNICIPALITY_PROJECTS[selMuni] || [];
    return (
      <>
        <button className="btn btn-back" onClick={() => actions.backToMetro()}>← Back to Metropole</button>
        <h3 className="muni-heading">{selMuni} {active ? "✅ inaugurated" : ""}</h3>
        {anchor && (
          <p className="caption">
            Anchor: {anchor.display_name} · see the Directorates tab for this municipality's own
            departments.
          </p>
        )}

        <p className="hint">👆 Click a district for details:</p>
        <div className="muni-grid">
          {info.districts.map((d) => (
            <button key={d} className="btn btn-select" onClick={() => actions.selectDistrict(d)}>{d}</button>
          ))}
        </div>

        {active ? (
          <div className="callout callout-success">Inaugurated</div>
        ) : (
          <button
            className="btn btn-primary"
            disabled={state.budget < INAUGURATION_COST}
            onClick={() => actions.inaugurate(selMuni)}
          >
            Inaugurate ({INAUGURATION_COST})
          </button>
        )}

        {muniProjects.length > 0 && (
          <>
            <h4>🏗️ Municipal Projects</h4>
            {active ? (
              muniProjects.map((p) => <ReadOnlyProject key={p.id} project={p} />)
            ) : (
              <p className="caption">Inaugurate {selMuni} to unlock its municipal projects.</p>
            )}
          </>
        )}

        {selMuni === "Florești Central" && <CbdMasterplan />}
      </>
    );
  }

  const distProjects = DISTRICT_PROJECTS[districtProjectKey(selMuni, selDist)] || [];
  return (
    <>
      <button className="btn btn-back" onClick={() => actions.backToMunicipality()}>← Back to {selMuni}</button>
      <h3 className="muni-heading">{selDist}</h3>
      <p className="caption">
        District of <strong>{selMuni}</strong>, Florești Metropole · see the Directorates tab for this
        district's own civic office.
      </p>
      {active ? (
        <div className="callout callout-info">
          This district shares in its municipality's local government, inaugurated as part of the
          mixed-decentralization reform.
        </div>
      ) : (
        <>
          <div className="callout callout-warning">
            {selMuni} hasn't been inaugurated yet — inaugurate it to activate local government here,
            including this district.
          </div>
          <button
            className="btn btn-primary"
            disabled={state.budget < INAUGURATION_COST}
            onClick={() => actions.inaugurate(selMuni)}
          >
            Inaugurate {selMuni} ({INAUGURATION_COST})
          </button>
        </>
      )}

      {distProjects.length > 0 && (
        <>
          <h4>🏗️ District Projects</h4>
          {active ? (
            distProjects.map((p) => <ReadOnlyProject key={p.id} project={p} />)
          ) : (
            <p className="caption">Inaugurate {selMuni} to unlock projects in this district.</p>
          )}
        </>
      )}
    </>
  );
}

function SuburbsExpander({ localities }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        🏘️ Suburbs ({SUBURBS.length}) — dependent on the metropole, no local government
      </button>
      {open && localities && (
        <ul className="suburb-list">
          {SUBURBS.map((s) => {
            const loc = findLocality(localities, s.name);
            return (
              <li key={s.name}>
                <strong>{loc.display_name}</strong> ({loc.type})
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

function PrefecturePolicies() {
  return (
    <>
      <h4>🏛️ Prefecture Policies</h4>
      {PREFECTURE_POLICIES.map((policy) => (
        <ReadOnlyProject key={policy.id} project={policy} />
      ))}
    </>
  );
}

function PrefectureTowns() {
  return (
    <>
      <h4>🏘️ Prefecture Towns</h4>
      <p className="caption">
        Beside the metropole (with its Technopolis Okrugs and suburbs), two real villages have grown
        into small towns directly under the prefecture, each with its own town council and policies —
        connected to Florești by regional rail, and to the Metropolitan Ring Road by a regional
        expressway.
      </p>
      {PREFECTURE_TOWNS.map((town) => (
        <div key={town.id}>
          <p>
            <strong>{town.name}</strong> — {town.note}
          </p>
          {TOWN_POLICIES[town.id].map((policy) => (
            <ReadOnlyProject key={policy.id} project={policy} />
          ))}
        </div>
      ))}
    </>
  );
}

function CurrentPolicies() {
  const state = useSimState();
  const resolved = Object.entries(state.resolvedScenarios);
  if (resolved.length === 0) return null;
  const [open, setOpen] = useState(false);
  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        📋 Current Policies ({resolved.length} decided)
      </button>
      {open && (
        <ul className="suburb-list">
          {SCENARIOS.filter((s) => state.resolvedScenarios[s.id]).map((s) => {
            const r = state.resolvedScenarios[s.id];
            return (
              <li key={s.id}>
                <strong>{s.title}</strong> —{" "}
                {r.choice === null ? "⏭️ Skipped" : `${r.choice}) ${r.label}`}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

function TechnopolisExpander({ localities }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        🏭 Technopolis Okrugs ({TECHNOPOLIS_OKRUGS.length}) — Zelenograd model
      </button>
      {open && localities && (
        <div className="technopolis-body">
          <p className="caption">
            Alongside the French-style prefecture, the metropole borrows a second model from Moscow: a
            detached, single-industry administrative okrug, after Zelenograd — Moscow's own physically
            separate microelectronics okrug. These two villages sit outside the metropole's own territory
            but are administratively sponsored by it, each built around one flagship company rather than
            ordinary municipal government. See the Industry tab for each okrug's full product line.
          </p>
          <ul className="suburb-list">
            {TECHNOPOLIS_OKRUGS.map((okrug) => {
              const loc = findLocality(localities, okrug.name);
              return (
                <li key={okrug.name}>
                  <strong>{loc.display_name}</strong> ({loc.type}) — {okrug.company} · {okrug.sector}
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
