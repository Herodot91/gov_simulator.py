import { useSimState, useSimActions, fmtEffects } from "../state/SimulationContext.jsx";
import EffectsBarChart from "./EffectsBarChart.jsx";

// One project's UI at whichever governance layer it's shown: its options as
// buttons (mirrors the top-level scenario buttons) before it's resolved, or
// the result -- effects graph + explanation -- once it is.
export default function ProjectCard({ project, scopeLabel }) {
  const state = useSimState();
  const actions = useSimActions();
  const resolved = state.resolvedProjects[project.id];

  return (
    <div className="project-card">
      <div className="project-title">{project.title}</div>
      {resolved ? (
        resolved.choice === null ? (
          <div className="project-skipped">⏭️ Skipped</div>
        ) : (
          <>
            <div className="callout callout-success">{resolved.choice}) {resolved.label}</div>
            {(() => {
              const [, effects] = project.options[resolved.choice];
              return Object.keys(effects).length > 0 ? <EffectsBarChart effects={effects} /> : null;
            })()}
            <p className="caption">🌐 {project.intl}</p>
          </>
        )
      ) : (
        <div className="option-grid">
          {Object.entries(project.options).map(([key, [desc, effects, cost]]) => (
            <button
              key={key}
              className="btn btn-option"
              disabled={state.budget < cost}
              onClick={() => actions.resolveProject(project, key, scopeLabel)}
            >
              <span className="option-desc">{key}) {desc}</span>
              <span className="option-meta">Cost {cost} | {fmtEffects(effects)}</span>
            </button>
          ))}
          <button
            className="btn btn-option btn-skip"
            onClick={() => actions.resolveProject(project, null, scopeLabel)}
          >
            Skip
          </button>
        </div>
      )}
    </div>
  );
}
