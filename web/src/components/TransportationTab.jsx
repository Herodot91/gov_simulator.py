import { useState } from "react";
import {
  TRANSIT_LINES,
  TRANSIT_MODE_LABELS,
  TRANSIT_OPERATORS,
  transitInterchanges,
  transitRouteLabel,
  ROAD_NETWORK,
  roadRouteLabel,
} from "../data/transit.js";

// Transit lines/interchanges and roads/key sites, plus the two operators
// that run them: MetroFlor (the Metropolitan Council's own operator,
// everything that stays within the metropole) and FlorLink (the
// Prefecture's own operator, connecting Florești to the Prefecture Towns
// and beyond).
export default function TransportationTab() {
  return (
    <>
      <h4>🚍 Operators</h4>
      {TRANSIT_OPERATORS.map((op) => (
        <OperatorExpander key={op.id} operator={op} />
      ))}

      <TransitExpander />
      <RoadsExpander />
    </>
  );
}

function OperatorExpander({ operator }) {
  const [open, setOpen] = useState(false);
  const lines = TRANSIT_LINES.filter((l) => operator.lineIds.includes(l.id));
  return (
    <div className="expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        {operator.name} — {operator.level} operator ({lines.length} lines)
      </button>
      {open && (
        <div className="technopolis-body">
          <p className="caption">{operator.note}</p>
          <ul className="suburb-list">
            {lines.map((line) => (
              <li key={line.id}>
                <strong>{line.name}</strong> — {TRANSIT_MODE_LABELS[line.mode]}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

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
            <strong>Gara Florești</strong> (the Florești Central stop) is the hub where every mode
            meets. Rail runs in two tiers: <strong>Metro M1</strong> is the backbone spanning all 4
            municipalities; <strong>Metro M2</strong> crosses it there, running Coach Terminal ↔ Gara
            Florești ↔ Florești Central North. <strong>Tram T1</strong> is a short local shuttle from
            Gara Florești out to Centrul Civic. Road transit runs in three tiers, each with denser
            stops than the rail lines: <strong>BRT</strong> lines reach further out at commuter-rail-
            equivalent speed and don't stop as often; plain <strong>biogas/electric buses</strong>{" "}
            cover local routes with no dedicated lane; <strong>regional rail</strong> reaches the
            prefecture's own small towns (Cunicea, Răduleni). Routes below are proposed street-level
            alignments, not a surveyed plan.
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
            Committed infrastructure shown on the Map tab, not a development-project decision to
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
              Quarter boundary, on the Metropolitan Ring Road, Tram T1's terminus and a FlorLink coach
              hub.
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
              <strong>🏘️ Cunicea &amp; Răduleni</strong> — Prefecture Towns, each with its own 🏘️ sign
              on the map, reached by FlorLink regional rail and the Regional Expressway (which joins
              the Metropolitan Ring Road at Ghindești).
            </li>
            <li>
              <strong>📐 Proposed CBD</strong> — the riverside zone shown on the map between Centrul
              Civic and the Răut; see the full concept masterplan in Florești Central's own municipal
              view.
            </li>
            <li>
              <strong>⚡ Florești HPP</strong> — the hydroelectric power plant on the Răut river, just
              downstream of the CBD riverside land, managed by HydroTechnique Ltd. (see the Industry
              tab).
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}
