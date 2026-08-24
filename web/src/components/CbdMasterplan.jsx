import { useEffect, useState } from "react";

// Concept site plan for the new CBD proposed in Florești Central, anchored
// on Metro Line 1 and the Răut Plaza municipal project. Fetched as a static
// SVG (same file the Streamlit app embeds) rather than hand-ported to JSX,
// so both apps render from exactly one drawing.
export default function CbdMasterplan() {
  const [open, setOpen] = useState(false);
  const [svg, setSvg] = useState(null);

  useEffect(() => {
    if (open && svg === null) {
      fetch("/data/cbd_masterplan.svg")
        .then((r) => r.text())
        .then(setSvg);
    }
  }, [open, svg]);

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
          {svg ? (
            <div className="masterplan-svg" dangerouslySetInnerHTML={{ __html: svg }} />
          ) : (
            <p className="caption">Loading masterplan…</p>
          )}
        </div>
      )}
    </div>
  );
}
