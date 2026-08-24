import { useState } from "react";
import { useSimState } from "../state/SimulationContext.jsx";
import { METRO_STRUCTURE, SUBURBS } from "../data/metroStructure.js";
import { FACTORIES, SCHOOLS } from "../data/directorates.js";

const BESIDE_METROPOLE = ["Cunicea", "Răduleni", "Gura Căinarului"];

// Same flat, click-to-browse shape as the Directorates Dashboard: every
// location's factories (name, sector, products) and schools, laid out in
// one place. Purely descriptive world-building, no cost/score effects.
export default function IndustriesSchoolsDashboard() {
  const state = useSimState();
  const withinMetropole = [...Object.keys(METRO_STRUCTURE), ...SUBURBS.map((s) => s.name), "Ciripcău"];

  return (
    <section className="panel">
      <h3>🏭 Industries &amp; Schools Dashboard</h3>
      <p className="caption">
        Every location's factories (name, sector, products) and schools, browsable in one place —
        purely descriptive, no cost or score effects.
      </p>

      <p>
        <strong>Beside the metropole</strong>
      </p>
      {BESIDE_METROPOLE.map((name) => (
        <LocationExpander key={name} name={name} />
      ))}

      {state.metroActive ? (
        <>
          <p>
            <strong>Within the metropole</strong>
          </p>
          {withinMetropole.map((name) => (
            <LocationExpander key={name} name={name} />
          ))}
        </>
      ) : (
        <p className="caption">
          Establish the metropole (Scenario 1, option B) to see factories and schools across the
          municipalities, suburbs, and Ciripcău too.
        </p>
      )}
    </section>
  );
}

function LocationExpander({ name }) {
  const [open, setOpen] = useState(false);
  const factories = FACTORIES[name] || [];
  const schools = SCHOOLS[name] || [];
  if (factories.length === 0 && schools.length === 0) return null;

  const labelBits = [];
  if (factories.length) labelBits.push(`${factories.length} factories`);
  if (schools.length) labelBits.push(`${schools.length} schools`);

  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        {name} — {labelBits.join(", ")}
      </button>
      {open && (
        <div className="technopolis-body">
          {factories.length > 0 && (
            <>
              <p className="caption">
                <strong>🏭 Factories</strong>
              </p>
              <ul className="suburb-list">
                {factories.map((f) => (
                  <li key={f.name}>
                    <strong>{f.name}</strong> — <em>{f.sector}.</em> {f.products.join(", ")}
                  </li>
                ))}
              </ul>
            </>
          )}
          {schools.length > 0 && (
            <>
              <p className="caption">
                <strong>🎓 Schools</strong>
              </p>
              <ul className="suburb-list">
                {schools.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}
