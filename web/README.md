# Florești Metropole — React port

A React + Vite port of the Streamlit app in the repo root, with the same
feature set: real-time simulation, the 5 scripted scenarios, the
Metropole → Municipality → District governance drill-down (map click or
list click), layer-scoped development projects with map markers, the
Zelenograd-model Technopolis Okrugs with browsable company product
catalogs, the FlorTech University campus/faculty/department drill-down,
and CSV/JSON export. Vanilla CSS throughout — no UI framework. See the
[root README](../README.md) for the full rationale behind each feature.

The map uses [react-leaflet](https://react-leaflet.js.org/) over the same
real OpenStreetMap-derived territory data as the Streamlit app
(`public/data/*.geojson` / `.json`, copied from `../data/`).

## Run it

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

Outputs a static site to `dist/` — deployable to any static host (Vercel,
Netlify, GitHub Pages, etc.). Unlike the Streamlit app, this one runs
entirely client-side: no Python backend, no server-side session state.

## Structure

```
src/
  data/            scenarios, metro/district structure (incl. the two
                    Zelenograd-model Technopolis Okrugs), development projects,
                    companies.js (Technopolis Okrug product catalogs),
                    flortech.js (FlorTech campuses/faculties/vocational tracks)
  state/           SimulationContext.jsx — the whole game state as a reducer
  components/      Sidebar, ScenarioPanel, ScoreChart (hand-rolled SVG),
                    CitizenProgressCard, MetroMap (react-leaflet),
                    GovernanceStructure (the drill-down, incl. the Technopolis
                    Okrugs' nested product-line expanders), ProjectCard,
                    CbdMasterplan (fetches public/data/cbd_masterplan.svg —
                    the same concept CBD site plan the Streamlit app embeds),
                    FlorTechSection (campus grid → campus detail drill-down,
                    Vocational Institutes expander)
  utils/           geo.js (point-in-polygon, zoom-fit — small manual
                    replacements for the Python app's shapely calls),
                    export.js (CSV/JSON download)
public/data/       the same real geojson/locality data as the Streamlit app
```
