import { useState } from "react";
import masterplanSvg from "../../public/data/cbd_masterplan.svg?raw";

// Concept site plan for the new CBD proposed in Florești Central, anchored
// on Metro Line 1 and the Răut Plaza municipal project. Bundled at build
// time as the same static SVG file the Streamlit app embeds (not fetched
// at runtime), so both apps render from exactly one drawing and this also
// works with no server behind it (e.g. published as an Artifact).
export default function CbdMasterplan() {
  const [open, setOpen] = useState(false);

  return (
    <div className="expander masterplan-expander">
      <button className="expander-toggle" onClick={() => setOpen((o) => !o)}>
        <span className={`expander-caret ${open ? "open" : ""}`}>›</span>
        📐 View CBD Masterplan — concept site plan for Răut Plaza's district
      </button>
      {open && (
        <div className="masterplan-body">
          <p className="caption">
            A mixed-use business district proposed for the riverside land between Centrul Civic and the
            Răut, built around the Metro Line 1 station and Răut Plaza as its civic anchor. Concept only —
            not an adopted plan.
          </p>
          <div className="masterplan-svg" dangerouslySetInnerHTML={{ __html: masterplanSvg }} />
        </div>
      )}
    </div>
  );
}
