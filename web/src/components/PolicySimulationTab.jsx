import { useState } from "react";
import { useSimState } from "../state/SimulationContext.jsx";
import { METRO_STRUCTURE, TECHNOPOLIS_OKRUGS } from "../data/metroStructure.js";
import {
  METRO_PROJECTS,
  MUNICIPALITY_PROJECTS,
  DISTRICT_PROJECTS,
  TECHNOPOLIS_POLICIES,
  districtProjectKey,
} from "../data/projects.js";
import { PREFECTURE_POLICIES, PREFECTURE_TOWNS, TOWN_POLICIES } from "../data/directorates.js";
import ProjectCard from "./ProjectCard.jsx";

const LEVELS = ["Prefecture", "Metropole", "Municipality", "District", "Town", "Technopolis"];

// One selector reaching every governance level's own real policies/projects
// directly, instead of navigating to each level's own natural section --
// Prefecture, Metropole, Municipality, District, Town, and Technopolis all
// have their own real Cost + effects decisions. Resolving one here uses the
// exact same ProjectCard/resolveProject mechanism as everywhere else in the
// app (keyed by the project's own id, not by which UI rendered it), so it's
// a real decision, not a preview -- it shows up at that level's own natural
// section too, and vice versa.
export default function PolicySimulationTab() {
  const state = useSimState();
  const [level, setLevel] = useState("Prefecture");
  const [muni, setMuni] = useState(Object.keys(METRO_STRUCTURE)[0]);
  const [distMuni, setDistMuni] = useState(Object.keys(METRO_STRUCTURE)[0]);
  const [dist, setDist] = useState(METRO_STRUCTURE[Object.keys(METRO_STRUCTURE)[0]].districts[0]);
  const [town, setTown] = useState(PREFECTURE_TOWNS[0].name);
  const [okrug, setOkrug] = useState(TECHNOPOLIS_OKRUGS[0].name);

  return (
    <>
      <p className="caption">
        Pick a governance level to jump straight to its own real policies/projects — the same Cost +
        effects decisions available at that level's own section elsewhere in the app. Resolving one
        here is a real decision: it spends budget and shows up at that level's own section too. Once
        resolved, each card shows the effects it applied (graph) and its own explanation.
      </p>

      <div className="level-picker" role="radiogroup" aria-label="Governance level">
        {LEVELS.map((l) => (
          <button
            key={l}
            className={`btn btn-select ${level === l ? "btn-select-active" : ""}`}
            onClick={() => setLevel(l)}
          >
            {l}
          </button>
        ))}
      </div>

      {level === "Prefecture" &&
        PREFECTURE_POLICIES.map((policy) => (
          <ProjectCard key={policy.id} project={policy} scopeLabel="Prefecture" />
        ))}

      {level === "Metropole" &&
        (!state.metroActive ? (
          <div className="callout callout-info">
            Establish the metropole (Scenario 1, option B) to see Metropolitan Projects.
          </div>
        ) : (
          METRO_PROJECTS.map((p) => <ProjectCard key={p.id} project={p} scopeLabel="Metropolitan" />)
        ))}

      {level === "Municipality" &&
        (!state.metroActive ? (
          <div className="callout callout-info">Establish the metropole (Scenario 1, option B) first.</div>
        ) : (
          <>
            <LevelSelect label="Municipality" value={muni} onChange={setMuni} options={Object.keys(METRO_STRUCTURE)} />
            <MunicipalityProjects muni={muni} />
          </>
        ))}

      {level === "District" &&
        (!state.metroActive ? (
          <div className="callout callout-info">Establish the metropole (Scenario 1, option B) first.</div>
        ) : (
          <>
            <LevelSelect
              label="Municipality"
              value={distMuni}
              onChange={(v) => {
                setDistMuni(v);
                setDist(METRO_STRUCTURE[v].districts[0]);
              }}
              options={Object.keys(METRO_STRUCTURE)}
            />
            <LevelSelect label="District" value={dist} onChange={setDist} options={METRO_STRUCTURE[distMuni].districts} />
            <DistrictProjects muni={distMuni} dist={dist} />
          </>
        ))}

      {level === "Town" && (
        <>
          <LevelSelect label="Prefecture Town" value={town} onChange={setTown} options={PREFECTURE_TOWNS.map((t) => t.name)} />
          {TOWN_POLICIES[PREFECTURE_TOWNS.find((t) => t.name === town).id].map((policy) => (
            <ProjectCard key={policy.id} project={policy} scopeLabel={`${town} Town Council`} />
          ))}
        </>
      )}

      {level === "Technopolis" && (
        <>
          <LevelSelect label="Technopolis Okrug" value={okrug} onChange={setOkrug} options={TECHNOPOLIS_OKRUGS.map((o) => o.name)} />
          {(TECHNOPOLIS_POLICIES[okrug] || []).map((policy) => (
            <ProjectCard key={policy.id} project={policy} scopeLabel={`${okrug} Technopolis Okrug`} />
          ))}
        </>
      )}
    </>
  );
}

function LevelSelect({ label, value, onChange, options }) {
  return (
    <label className="policy-sim-select">
      {label}
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </label>
  );
}

function MunicipalityProjects({ muni }) {
  const state = useSimState();
  const projects = MUNICIPALITY_PROJECTS[muni] || [];
  const active = state.inaugurated.includes(muni);
  if (projects.length === 0) return <p className="caption">{muni} has no municipal projects defined.</p>;
  if (!active) {
    return (
      <p className="caption">
        Inaugurate {muni} (from its own municipal view, in the Decentralization Structure tab) to
        unlock its projects.
      </p>
    );
  }
  return projects.map((p) => <ProjectCard key={p.id} project={p} scopeLabel={`${muni} municipal`} />);
}

function DistrictProjects({ muni, dist }) {
  const state = useSimState();
  const projects = DISTRICT_PROJECTS[districtProjectKey(muni, dist)] || [];
  const active = state.inaugurated.includes(muni);
  if (projects.length === 0) return <p className="caption">{dist} has no district projects defined.</p>;
  if (!active) return <p className="caption">Inaugurate {muni} to unlock projects in {dist}.</p>;
  return projects.map((p) => <ProjectCard key={p.id} project={p} scopeLabel={`${dist} district`} />);
}
