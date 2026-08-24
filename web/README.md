# Florești Metropole — React port

A React + Vite port of the Streamlit app in the repo root, with the same
feature set: real-time simulation, the 5 scripted scenarios, the
Metropole → Municipality → District governance drill-down (map click or
list click), layer-scoped development projects with map markers, the
Zelenograd-model Technopolis Okrugs with browsable company product
catalogs, the FlorTech and AgroFlor university campus/faculty/department
drill-downs, the public transit network (trams, BRT, commuter rail) with
named-street routes and interchange markers, the Metropolitan Ring Road
and Technopolis Expressway, the Coach Terminal/Centrul Civic/CBD zone map
sites, each governance tier's own directorates/departments org chart
(plus interactive Prefecture Policies and a Current Policies review
panel), on-map district boundaries once a municipality is selected, and
CSV/JSON export. Vanilla CSS throughout — no UI framework. See the
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
                    flortech.js (FlorTech campuses/faculties/vocational tracks),
                    agroflor.js (AgroFlor campuses/faculties/research centers),
                    transit.js (tram/BRT/commuter lines with named-street
                    routes, interchange computation, the Ring Road/Expressway,
                    Coach Terminal, Civic District, and CBD zone),
                    directorates.js (Prefecture/Metro Council directorates,
                    Prefecture Policies, per-municipality departments,
                    per-district civic offices)
  state/           SimulationContext.jsx — the whole game state as a reducer
                    (incl. resolvedScenarios, for the Current Policies panel)
  components/      Sidebar, ScenarioPanel, ScoreChart (hand-rolled SVG),
                    CitizenProgressCard, MetroMap (react-leaflet, incl. the
                    FlorTech/AgroFlor campus markers, the transit lines/
                    interchange markers, the Ring Road/Expressway, the
                    Coach Terminal/Centrul Civic markers and CBD zone
                    rectangle, and the on-map district quadrant overlay),
                    GovernanceStructure (the drill-down, incl. the
                    Technopolis Okrugs' nested product-line expanders, the
                    Public Transit Network expander, the Roads & Key Sites
                    expander, the Prefecture/Metro Council/municipal/district
                    directorate panels, Prefecture Policies, and the Current
                    Policies review panel),
                    ProjectCard, CbdMasterplan (fetches
                    public/data/cbd_masterplan.svg — the same concept CBD
                    site plan the Streamlit app embeds), FlorTechSection
                    (campus grid → campus detail drill-down, Vocational
                    Institutes expander), AgroFlorSection (same shape, plus
                    a Research Centers & Labs list per campus)
  utils/           geo.js (point-in-polygon, zoom-fit, and Sutherland-Hodgman
                    polygon clipping for the district quadrant overlay --
                    small manual replacements for the Python app's shapely
                    calls), export.js (CSV/JSON download)
public/data/       the same real geojson/locality data as the Streamlit app
```
