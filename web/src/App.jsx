import { SimulationProvider } from "./state/SimulationContext.jsx";
import Sidebar from "./components/Sidebar.jsx";
import StatusRow from "./components/StatusRow.jsx";
import ScenarioPanel from "./components/ScenarioPanel.jsx";
import ScoreChart from "./components/ScoreChart.jsx";
import ExportPanel from "./components/ExportPanel.jsx";
import CitizenProgressCard from "./components/CitizenProgressCard.jsx";
import GovernanceStructure from "./components/GovernanceStructure.jsx";
import "./App.css";

function AppShell() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">
        <h1 className="app-title">Florești Metropole — CivicTech Simulator</h1>
        <StatusRow />
        <ScenarioPanel />

        <div className="two-col">
          <div className="col-wide">
            <ScoreChart />
            <ExportPanel />
          </div>
          <div className="col-narrow">
            <CitizenProgressCard />
          </div>
        </div>

        <GovernanceStructure />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <SimulationProvider>
      <AppShell />
    </SimulationProvider>
  );
}
