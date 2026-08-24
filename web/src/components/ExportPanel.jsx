import { useSimState } from "../state/SimulationContext.jsx";
import { downloadBlob, historyToCsv } from "../utils/export.js";

export default function ExportPanel() {
  const state = useSimState();

  const downloadCsv = () => {
    downloadBlob(historyToCsv(state.history, state.monthLabels), "history.csv", "text/csv");
  };

  const downloadReport = () => {
    const report = {
      mode: state.mode,
      starting_budget: state.startBudget,
      current_budget: state.budget,
      current_month: state.simMonth,
      current_scores: state.scores,
      metro_active: state.metroActive,
      inaugurated_municipalities: state.inaugurated,
      log: state.logs,
    };
    downloadBlob(JSON.stringify(report, null, 2), "report.json", "application/json");
  };

  return (
    <div className="export-panel">
      <div className="export-buttons">
        <button className="btn btn-secondary" onClick={downloadCsv}>Download History CSV</button>
        <button className="btn btn-secondary" onClick={downloadReport}>Download Report JSON</button>
      </div>
      <div className="field-label">Log</div>
      <textarea
        className="log-box"
        readOnly
        value={[...state.logs].reverse().join("\n")}
        rows={10}
      />
    </div>
  );
}
