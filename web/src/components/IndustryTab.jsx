import { useState } from "react";
import { useSimState } from "../state/SimulationContext.jsx";
import { METRO_STRUCTURE, SUBURBS, TECHNOPOLIS_OKRUGS } from "../data/metroStructure.js";
import { FACTORIES } from "../data/directorates.js";
import { COMPANY_PRODUCTS } from "../data/companies.js";
import { TECHNOPOLIS_POLICIES } from "../data/projects.js";
import { findLocality } from "./MetroMap.jsx";
import { useLocalities } from "./useLocalities.js";
import ProjectCard from "./ProjectCard.jsx";

const BESIDE_METROPOLE = ["Cunicea", "Răduleni"];

// Technopolis Okrugs' full product lines (the Decentralization Structure tab
// only names them administratively) and their own real policy, plus every
// location's own factories.
export default function IndustryTab() {
  const state = useSimState();
  const localities = useLocalities();
  const withinMetropole = [...Object.keys(METRO_STRUCTURE), ...SUBURBS.map((s) => s.name), "Ciripcău"];

  return (
    <>
      <p className="caption">
        Every Technopolis Okrug's flagship company, product line, and its own real production-line
        policy, plus every location's own factories (name, sector, products) — factories are purely
        descriptive, but each okrug's own policy is a real Cost + effects decision like any other
        governance level's (see also the Policy Simulation tab).
      </p>

      <h4>🏭 Technopolis Okrugs</h4>
      {localities &&
        TECHNOPOLIS_OKRUGS.map((okrug) => {
          const loc = findLocality(localities, okrug.name);
          return (
            <div key={okrug.name}>
              <p>
                <strong>{loc.display_name}</strong> ({loc.type}) — {okrug.company}
                <br />
                <span className="caption">
                  <em>{okrug.sector}.</em> {okrug.note}
                </span>
              </p>
              <CompanyProducts company={okrug.company} />
              {(TECHNOPOLIS_POLICIES[okrug.name] || []).map((policy) => (
                <ProjectCard key={policy.id} project={policy} scopeLabel={`${loc.display_name} Technopolis Okrug`} />
              ))}
            </div>
          );
        })}

      <h4>🏭 Factories</h4>
      <p>
        <strong>Beside the metropole</strong>
      </p>
      {BESIDE_METROPOLE.map((name) => (
        <FactoryExpander key={name} name={name} />
      ))}
      {state.metroActive ? (
        <>
          <p>
            <strong>Within the metropole</strong>
          </p>
          {withinMetropole.map((name) => (
            <FactoryExpander key={name} name={name} />
          ))}
        </>
      ) : (
        <p className="caption">
          Establish the metropole (Scenario 1, option B) to see factories across the municipalities,
          suburbs, and Ciripcău too.
        </p>
      )}
    </>
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

function FactoryExpander({ name }) {
  const [open, setOpen] = useState(false);
  const factories = FACTORIES[name] || [];
  if (factories.length === 0) return null;
  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        {name} — {factories.length} factories
      </button>
      {open && (
        <ul className="suburb-list">
          {factories.map((f) => (
            <li key={f.name}>
              <strong>{f.name}</strong> — <em>{f.sector}.</em> {f.products.join(", ")}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
