import { useEffect, useState } from "react";
import { useSimState, useSimActions } from "../state/SimulationContext.jsx";
import { METRO_STRUCTURE, SUBURBS, INAUGURATION_COST } from "../data/metroStructure.js";
import { METRO_PROJECTS, MUNICIPALITY_PROJECTS, DISTRICT_PROJECTS, districtProjectKey } from "../data/projects.js";
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
