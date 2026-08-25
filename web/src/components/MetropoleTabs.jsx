import { useState } from "react";
import GovernanceStructure from "./GovernanceStructure.jsx";
import DirectoratesDashboard from "./DirectoratesDashboard.jsx";
import MapTab from "./MapTab.jsx";
import IndustryTab from "./IndustryTab.jsx";
import SchoolsTab from "./SchoolsTab.jsx";
import TransportationTab from "./TransportationTab.jsx";

const TABS = [
  { id: "structure", label: "🏛️ Decentralization Structure" },
  { id: "directorates", label: "🏢 Directorates" },
  { id: "map", label: "🗺️ Map" },
  { id: "industry", label: "🏭 Industry" },
  { id: "schools", label: "🎓 Schools" },
  { id: "transport", label: "🚌 Transportation" },
];

// One flat scrolling page got chaotic once every governance layer,
// dashboard, and reference section piled up in sequence. A proper menu
// instead: each tab's content stays mounted (toggled with the `hidden`
// attribute, not conditional rendering) so map state, drill-down
// selections, and expander state all survive switching tabs.
export default function MetropoleTabs() {
  const [activeTab, setActiveTab] = useState("structure");

  return (
    <section className="panel">
      <h3>🏙️ Florești Metropole</h3>
      <div className="tab-bar" role="tablist">
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={activeTab === t.id}
            className={`tab-btn ${activeTab === t.id ? "active" : ""}`}
            onClick={() => setActiveTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div hidden={activeTab !== "structure"}>
        <GovernanceStructure />
      </div>
      <div hidden={activeTab !== "directorates"}>
        <DirectoratesDashboard />
      </div>
      <div hidden={activeTab !== "map"}>
        <MapTab />
      </div>
      <div hidden={activeTab !== "industry"}>
        <IndustryTab />
      </div>
      <div hidden={activeTab !== "schools"}>
        <SchoolsTab />
      </div>
      <div hidden={activeTab !== "transport"}>
        <TransportationTab />
      </div>
    </section>
  );
}
