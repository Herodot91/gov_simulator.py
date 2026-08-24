import { createContext, useContext, useReducer, useRef, useEffect, useCallback } from "react";
import { SCENARIOS, RANDOM_EVENTS, BASE_SCORES } from "../data/scenarios.js";
import { METRO_STRUCTURE, INAUGURATION_COST } from "../data/metroStructure.js";

function clamp(v) {
  return Math.max(0, Math.min(100, v));
}

export function fmtEffects(effects) {
  return Object.entries(effects)
    .map(([k, v]) => `${k} ${v >= 0 ? "+" : ""}${v}`)
    .join(", ");
}

function applyEffects(scores, effects) {
  const next = { ...scores };
  for (const [k, dv] of Object.entries(effects)) {
    next[k] = clamp(next[k] + dv);
  }
  return next;
}

function initialState(startBudget) {
  return {
    scores: { ...BASE_SCORES },
    budget: startBudget,
    startBudget,
    history: [{ ...BASE_SCORES }],
    monthLabels: ["Start"],
    logs: [],
    turn: 0,
    lastIntl: "",
    simMonth: 0,
    autoplay: false,
    metroActive: false,
    inaugurated: [],
    selectedMunicipality: null,
    selectedDistrict: null,
    resolvedProjects: {},
    mode: "Democracy",
    tickInterval: 3,
    selectedCampus: null,
    selectedAgroCampus: null,
  };
}

function record(state, note, scores) {
  return {
    ...state,
    scores,
    history: [...state.history, scores],
    monthLabels: [...state.monthLabels, `M${state.simMonth}`],
    logs: [...state.logs, note],
  };
}

function reducer(state, action) {
  switch (action.type) {
    case "RESET":
      return initialState(action.startBudget);

    case "SET_MODE":
      return { ...state, mode: action.mode };

    case "SET_AUTOPLAY":
      return { ...state, autoplay: action.value };

    case "SET_TICK_INTERVAL":
      return { ...state, tickInterval: action.value };

    case "SELECT_MUNICIPALITY":
      return { ...state, selectedMunicipality: action.name, selectedDistrict: null };

    case "SELECT_DISTRICT":
      return { ...state, selectedDistrict: action.name };

    case "SELECT_CAMPUS":
      return { ...state, selectedCampus: action.id };

    case "SELECT_AGRO_CAMPUS":
      return { ...state, selectedAgroCampus: action.id };

    case "BACK_TO_METRO":
      return { ...state, selectedMunicipality: null, selectedDistrict: null };

    case "BACK_TO_MUNICIPALITY":
      return { ...state, selectedDistrict: null };

    case "RESOLVE_SCENARIO": {
      const { scenario, key } = action;
      const simMonth = state.simMonth + 1;
      if (key === null) {
        return {
          ...record({ ...state, simMonth }, `Month ${simMonth}: Skipped — ${scenario.title}.`, state.scores),
          turn: state.turn + 1,
        };
      }
      const [desc, effects, cost] = scenario.options[key];
      if (state.budget < cost) {
        return {
          ...record(
            { ...state, simMonth },
            `Month ${simMonth}: Not enough budget for ${key}) ${desc} on '${scenario.title}'. Skipped.`,
            state.scores
          ),
          turn: state.turn + 1,
        };
      }
      const scores = applyEffects(state.scores, effects);
      let note = `Month ${simMonth}: ${scenario.title} → ${key}) ${desc} | Cost ${cost} | Intl: ${scenario.intl} | Scores ${JSON.stringify(
        scores
      )} | Budget ${state.budget - cost}`;
      if (state.mode === "Democracy") {
        const turnout = clamp(Math.round(30 + 0.5 * scores.Stability));
        const passed = scores.Stability + scores.Governance > 90;
        note += ` | Vote: turnout ${turnout}% → ${passed ? "PASSED" : "FAILED"}`;
      }
      let metroActive = state.metroActive;
      if (scenario === SCENARIOS[0] && key === "B") {
        metroActive = true;
        note += " | 🏙️ Mixed-decentralization governance enabled — Florești Metropole can now inaugurate its municipalities below.";
      }
      return {
        ...record({ ...state, simMonth, budget: state.budget - cost, lastIntl: scenario.intl }, note, scores),
        turn: state.turn + 1,
        metroActive,
      };
    }

    case "INAUGURATE": {
      const { name } = action;
      if (state.inaugurated.includes(name)) return state;
      const simMonth = state.simMonth + 1;
      if (state.budget < INAUGURATION_COST) {
        return record(
          { ...state, simMonth },
          `Month ${simMonth}: Not enough budget (${INAUGURATION_COST}) to inaugurate ${name}. Skipped.`,
          state.scores
        );
      }
      const scores = applyEffects(state.scores, { Governance: +4, Stability: +3 });
      const districts = METRO_STRUCTURE[name].districts.join(", ");
      const note = `Month ${simMonth}: 🏛️ ${name} municipality inaugurated — districts: ${districts} | Cost ${INAUGURATION_COST} | Scores ${JSON.stringify(
        scores
      )} | Budget ${state.budget - INAUGURATION_COST}`;
      return record(
        {
          ...state,
          simMonth,
          budget: state.budget - INAUGURATION_COST,
          inaugurated: [...state.inaugurated, name],
        },
        note,
        scores
      );
    }

    case "RESOLVE_PROJECT": {
      const { project, key, scopeLabel } = action;
      const simMonth = state.simMonth + 1;
      if (key === null) {
        return record(
          {
            ...state,
            simMonth,
            resolvedProjects: { ...state.resolvedProjects, [project.id]: { choice: null, label: "Skipped" } },
          },
          `Month ${simMonth}: Skipped — ${project.title} (${scopeLabel}).`,
          state.scores
        );
      }
      const [desc, effects, cost] = project.options[key];
      if (state.budget < cost) {
        return record(
          { ...state, simMonth },
          `Month ${simMonth}: Not enough budget for ${key}) ${desc} on '${project.title}'. Skipped.`,
          state.scores
        );
      }
      const scores = applyEffects(state.scores, effects);
      const note = `Month ${simMonth}: ${project.title} (${scopeLabel}) → ${key}) ${desc} | Cost ${cost} | Intl: ${project.intl} | Scores ${JSON.stringify(
        scores
      )} | Budget ${state.budget - cost}`;
      return record(
        {
          ...state,
          simMonth,
          budget: state.budget - cost,
          lastIntl: project.intl,
          resolvedProjects: { ...state.resolvedProjects, [project.id]: { choice: key, label: desc } },
        },
        note,
        scores
      );
    }

    case "RANDOM_TICK": {
      const simMonth = state.simMonth + 1;
      const [title, effects, blurb] = RANDOM_EVENTS[Math.floor(Math.random() * RANDOM_EVENTS.length)];
      const scores = applyEffects(state.scores, effects);
      const note = `Month ${simMonth}: 🌍 ${title} — ${blurb} | Scores ${JSON.stringify(scores)}`;
      return record({ ...state, simMonth, lastIntl: blurb }, note, scores);
    }

    default:
      return state;
  }
}

const SimulationStateContext = createContext(null);
const SimulationDispatchContext = createContext(null);

export function SimulationProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, 100, initialState);

  // Real-time clock: while autoplay is on, fire one random event per tick,
  // same cadence as the Python version's sleep(tick_interval) + rerun loop.
  const timerRef = useRef(null);
  useEffect(() => {
    if (state.autoplay) {
      timerRef.current = setInterval(() => {
        dispatch({ type: "RANDOM_TICK" });
      }, state.tickInterval * 1000);
      return () => clearInterval(timerRef.current);
    }
  }, [state.autoplay, state.tickInterval]);

  return (
    <SimulationStateContext.Provider value={state}>
      <SimulationDispatchContext.Provider value={dispatch}>{children}</SimulationDispatchContext.Provider>
    </SimulationStateContext.Provider>
  );
}

export function useSimState() {
  const ctx = useContext(SimulationStateContext);
  if (!ctx) throw new Error("useSimState must be used within SimulationProvider");
  return ctx;
}

export function useSimDispatch() {
  const ctx = useContext(SimulationDispatchContext);
  if (!ctx) throw new Error("useSimDispatch must be used within SimulationProvider");
  return ctx;
}

// Convenience action creators, mirroring the Python function names.
export function useSimActions() {
  const dispatch = useSimDispatch();
  return {
    reset: useCallback((startBudget) => dispatch({ type: "RESET", startBudget }), [dispatch]),
    setMode: useCallback((mode) => dispatch({ type: "SET_MODE", mode }), [dispatch]),
    setAutoplay: useCallback((value) => dispatch({ type: "SET_AUTOPLAY", value }), [dispatch]),
    setTickInterval: useCallback((value) => dispatch({ type: "SET_TICK_INTERVAL", value }), [dispatch]),
    selectMunicipality: useCallback((name) => dispatch({ type: "SELECT_MUNICIPALITY", name }), [dispatch]),
    selectDistrict: useCallback((name) => dispatch({ type: "SELECT_DISTRICT", name }), [dispatch]),
    selectCampus: useCallback((id) => dispatch({ type: "SELECT_CAMPUS", id }), [dispatch]),
    selectAgroCampus: useCallback((id) => dispatch({ type: "SELECT_AGRO_CAMPUS", id }), [dispatch]),
    backToMetro: useCallback(() => dispatch({ type: "BACK_TO_METRO" }), [dispatch]),
    backToMunicipality: useCallback(() => dispatch({ type: "BACK_TO_MUNICIPALITY" }), [dispatch]),
    resolveScenario: useCallback((scenario, key) => dispatch({ type: "RESOLVE_SCENARIO", scenario, key }), [dispatch]),
    inaugurate: useCallback((name) => dispatch({ type: "INAUGURATE", name }), [dispatch]),
    resolveProject: useCallback(
      (project, key, scopeLabel) => dispatch({ type: "RESOLVE_PROJECT", project, key, scopeLabel }),
      [dispatch]
    ),
    triggerRandomTick: useCallback(() => dispatch({ type: "RANDOM_TICK" }), [dispatch]),
  };
}
