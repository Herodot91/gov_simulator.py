import { useEffect, useState } from "react";
import { useSimState, useSimActions } from "../state/SimulationContext.jsx";
import { METRO_STRUCTURE, SUBURBS, INAUGURATION_COST, TECHNOPOLIS_OKRUGS } from "../data/metroStructure.js";
import { METRO_PROJECTS, MUNICIPALITY_PROJECTS, DISTRICT_PROJECTS, districtProjectKey } from "../data/projects.js";
import { SCENARIOS } from "../data/scenarios.js";
import { COMPANY_PRODUCTS } from "../data/companies.js";
import {
  TRANSIT_LINES,
  transitInterchanges,
  transitRouteLabel,
  ROAD_NETWORK,
  roadRouteLabel,
} from "../data/transit.js";
import {
  PREFECTURE_DIRECTORATES,
  PREFECTURE_POLICIES,
  METRO_COUNCIL_DIRECTORATES,
  MUNICIPALITY_DEPARTMENTS,
  districtOffice,
} from "../data/directorates.js";
import MetroMap, { findLocality } from "./MetroMap.jsx";
import ProjectCard from "./ProjectCard.jsx";
import CbdMasterplan from "./CbdMasterplan.jsx";

function useLocalities() {
  const [localities, setLocalities] = useState(null);
  useEffect(() => {
    fetch("/data/floresti_localities.json").then((r) => r.json()).then(setLocalities);
  }, []);
  return localities;
}

export default function GovernanceStructure() {
  const state = useSimState();
  const actions = useSimActions();
  const localities = useLocalities();

  return (
    <section className="panel">
      <h3>🏙️ Florești Metropole — Governance Structure</h3>
      {!state.metroActive ? (
        <div className="callout callout-info">
          Choose <strong>B) Establish Florești Metropole</strong> in Scenario 1 to activate
          mixed-decentralization governance: a metropolitan tier (Istanbul/Budapest-style) carved out of
          the French-style Florești Prefecture, over 4 municipalities, each with its own local government
          and districts.
        </div>
      ) : (
        <p className="caption">
          Mixed decentralization is in effect — click a municipality on the map (or below) to drill down
          into its districts. Suburbs stay administratively dependent on the metropole.
        </p>
      )}

      <PrefectureExpander />
      <PrefecturePolicies />

      <MetroMap />

      {state.metroActive && <DrillDown localities={localities} />}
    </section>
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
        <TransitExpander />
        <RoadsExpander />
        <MetroCouncilExpander />
        <CurrentPolicies />

        <h4>🏗️ Metropolitan Projects</h4>
        {METRO_PROJECTS.map((p) => (
          <ProjectCard key={p.id} project={p} scopeLabel="Metropolitan" />
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
        {anchor && <p className="caption">Anchor: {anchor.display_name}</p>}

        <MunicipalityDepartmentsExpander municipality={selMuni} />

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
              muniProjects.map((p) => <ProjectCard key={p.id} project={p} scopeLabel={`${selMuni} municipal`} />)
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
      <p className="caption">District of <strong>{selMuni}</strong>, Florești Metropole.</p>
      <DistrictOffice municipality={selMuni} district={selDist} />
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
            distProjects.map((p) => <ProjectCard key={p.id} project={p} scopeLabel={`${selDist} district`} />)
          ) : (
            <p className="caption">Inaugurate {selMuni} to unlock projects in this district.</p>
          )}
        </>
      )}
    </>
  );
}

function MunicipalityDepartmentsExpander({ municipality }) {
  const [open, setOpen] = useState(false);
  const departments = MUNICIPALITY_DEPARTMENTS[municipality] || [];
  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        🏢 {municipality} — Departments ({departments.length})
      </button>
      {open && (
        <ul className="suburb-list">
          {departments.map((d) => (
            <li key={d.name}>
              <strong>{d.name}</strong> — {d.mandate}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function DistrictOffice({ municipality, district }) {
  const office = districtOffice(municipality, district);
  return (
    <p className="caption">
      🏢 <strong>{office.name}</strong> — {office.mandate}
    </p>
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

function CompanyProducts({ company }) {
  const [open, setOpen] = useState(false);
  const products = COMPANY_PRODUCTS[company] || [];
  return (
    <div className="expander expander-nested">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        🔧 {company} — product line ({products.length})
      </button>
      {open && (
        <ul className="suburb-list">
          {products.map((p) => (
            <li key={p.model}>
              <strong>{p.model}</strong> — {p.category} · {p.spec}
            </li>
          ))}
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
        <ProjectCard key={policy.id} project={policy} scopeLabel="Prefecture" />
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

function PrefectureExpander() {
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
            The French-style prefecture's own deconcentrated state administration, in effect regardless
            of whether the metropole has been established — the state tier the metropole is carved out of.
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

const TRANSIT_MODE_LABELS = { tram: "🚋 Tram", brt: "🚌 BRT", commuter: "🚆 Commuter" };

function TransitExpander() {
  const [open, setOpen] = useState(false);
  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        🚊 Public Transit Network ({TRANSIT_LINES.length} lines)
      </button>
      {open && (
        <div className="technopolis-body">
          <p className="caption">
            The metropole's metro system runs on trams, not heavy rail, and stays within the 4
            municipalities' own boundaries — unlike the BRT and commuter lines, it doesn't reach the
            suburbs. Tram M2 runs strictly between Vărvăreuca's Heritage Quarter boundary (the Coach
            Terminal) and Florești Central's own northern boundary. A BRT corridor (biogas/electric
            buses) covers what the trams don't, and two commuter rail lines reach past the metropole's
            own territory. Routes below are proposed street-level alignments, not a surveyed plan.
          </p>
          <ul className="suburb-list">
            {TRANSIT_LINES.map((line) => (
              <li key={line.id}>
                <strong>{line.name}</strong> — {TRANSIT_MODE_LABELS[line.mode]}
                <br />
                <span className="caption">{transitRouteLabel(line)}</span>
              </li>
            ))}
          </ul>
          <p className="caption"><strong>⇄ Interchanges</strong></p>
          <ul className="suburb-list">
            {Object.entries(transitInterchanges()).map(([stop, lines]) => (
              <li key={stop}>
                <strong>{stop}</strong> — {lines.join(", ")}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function RoadsExpander() {
  const [open, setOpen] = useState(false);
  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        🛣️ Roads & Key Sites ({ROAD_NETWORK.length} roads)
      </button>
      {open && (
        <div className="technopolis-body">
          <p className="caption">
            Committed infrastructure shown on the map itself, not a development-project decision to
            resolve. The Ring Road stays outside the municipalities' own built territory, tracing the
            metro's southern periphery close to Vărvăreuca's Heritage Quarter and Forestry District
            rather than cutting through the metropole itself.
          </p>
          <ul className="suburb-list">
            {ROAD_NETWORK.map((road) => (
              <li key={road.id}>
                <strong>{road.name}</strong>
                <br />
                <span className="caption">{roadRouteLabel(road)}</span>
              </li>
            ))}
            <li>
              <strong>🚌 Autogara Metropolitană (Coach Terminal)</strong> — on Vărvăreuca's Heritage
              Quarter boundary, on the Metropolitan Ring Road, Tram M2's terminus.
            </li>
            <li>
              <strong>✈️ Mărculești–Florești International Airport</strong> — its own sign on the map,
              same treatment as the Coach Terminal.
            </li>
            <li>
              <strong>🏛️ Centrul Civic (Civic Center)</strong> — Florești Central's own civic district,
              seat of the Metropolitan Council, the Florești Prefecture, and their directorates.
            </li>
            <li>
              <strong>📐 Proposed CBD</strong> — the riverside zone shown on the map between Centrul
              Civic and the Răut; see the full concept masterplan in Florești Central's own municipal
              view.
            </li>
          </ul>
        </div>
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
            ordinary municipal government.
          </p>
          <ul className="suburb-list">
            {TECHNOPOLIS_OKRUGS.map((okrug) => {
              const loc = findLocality(localities, okrug.name);
              return (
                <li key={okrug.name}>
                  <strong>{loc.display_name}</strong> ({loc.type}) — {okrug.company}
                  <br />
                  <span className="caption">
                    <em>{okrug.sector}.</em> {okrug.note}
                  </span>
                  <CompanyProducts company={okrug.company} />
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
