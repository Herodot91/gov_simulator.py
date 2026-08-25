# Florești Metropole — React port

A React + Vite port of the Streamlit app in the repo root, with the same
feature set: real-time simulation, the 5 scripted scenarios, and the
Florești Metropole section's own **six-tab menu** — Decentralization
Structure (Prefecture → Metropole → Prefecture Towns, the
Metropole → Municipality → District drill-down via map click or list
click, layer-scoped development projects with map markers, Suburbs, and
the Technopolis Okrugs' administrative mention), Directorates (every
tier's own org chart, flat), Map (the full interactive map on its own),
Industry (the Zelenograd-model Technopolis Okrugs' full product-line
catalogs plus every location's factories), Schools (every location's own
schools plus the FlorTech and AgroFlor university campus/faculty/
department drill-downs), and Transportation (the public transit network —
Metro M1/M2, Tram T1, BRT/Bus/Regional Rail, all interchanging at Gara
Florești — with named-street routes and interchange markers, Roads & Key
Sites, and the **MetroFlor**/**FlorLink** operator listings). The
Metropolitan Ring Road, Technopolis Expressway, Regional Expressway, and
Coach Terminal/Airport/Centrul Civic/CBD zone/Florești HPP (Răut river,
HydroTechnique Ltd.) map sites are all still drawn on the map itself.
Prefecture Towns each get an expanded, dashed-circle territory, their own
town council/policies, and a non-mono-industrial factory roster; a
Current Policies review panel sits in the Decentralization Structure tab.
All six tabs stay mounted at once (hidden/shown, not conditionally
rendered), so map clicks, drill-down selections, and expander state
survive switching tabs. On-map district boundaries appear once a
municipality is selected, and CSV/JSON export rounds out the feature set.
Vanilla CSS throughout — no UI framework. See the
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
                    transit.js (Metro/Tram/BRT/Bus/Regional Rail lines with
                    named-street routes, interchange computation, the Ring
                    Road/Technopolis/Regional Expressways, Coach Terminal,
                    Civic District, CBD zone, Florești HPP, and
                    TRANSIT_OPERATORS for MetroFlor/FlorLink),
                    directorates.js (Prefecture/Metro Council directorates,
                    Prefecture Policies, Prefecture Towns with their own
                    town councils/policies, per-municipality departments,
                    per-district civic offices, FACTORIES and SCHOOLS per
                    location)
  state/           SimulationContext.jsx — the whole game state as a reducer
                    (incl. resolvedScenarios, for the Current Policies panel)
  components/      Sidebar, ScenarioPanel, ScoreChart (hand-rolled SVG),
                    CitizenProgressCard, MetropoleTabs (the six-tab menu --
                    Decentralization Structure/Directorates/Map/Industry/
                    Schools/Transportation -- keeps every tab's content
                    mounted via the `hidden` attribute rather than
                    conditional rendering, so map/drill-down/expander state
                    survives switching tabs), useLocalities.js (shared hook,
                    fetches public/data/floresti_localities.json),
                    MetroMap (react-leaflet, incl. the FlorTech/AgroFlor
                    campus markers, the transit lines/interchange markers,
                    the Ring Road/Expressway, the Coach Terminal/Centrul
                    Civic/Florești HPP markers, the Prefecture Towns'
                    dashed territory circles, CBD zone rectangle, and the
                    on-map district quadrant overlay), MapTab (thin
                    MetroMap wrapper for its own tab),
                    GovernanceStructure (the Decentralization Structure
                    tab's content: the drill-down, Suburbs and a brief
                    Technopolis Okrugs mention, Prefecture Policies, the
                    Current Policies review panel, and Prefecture Towns --
                    org-chart detail lives in the Directorates tab instead),
                    ProjectCard, CbdMasterplan (fetches
                    public/data/cbd_masterplan.svg — the same concept CBD
                    site plan the Streamlit app embeds),
                    DirectoratesDashboard (every tier's directorates/
                    departments/civic offices flattened into one panel, now
                    the Directorates tab's content), IndustryTab (the
                    Technopolis Okrugs' full product-line catalogs plus
                    every location's factories), SchoolsTab (every
                    location's schools, plus FlorTechSection and
                    AgroFlorSection), FlorTechSection (campus grid → campus
                    detail drill-down, Vocational Institutes expander),
                    AgroFlorSection (same shape, plus a Research Centers &
                    Labs list per campus), TransportationTab (MetroFlor/
                    FlorLink operator expanders, the Public Transit Network
                    expander, and the Roads & Key Sites expander)
  utils/           geo.js (point-in-polygon, zoom-fit, and Sutherland-Hodgman
                    polygon clipping for the district quadrant overlay --
                    small manual replacements for the Python app's shapely
                    calls), export.js (CSV/JSON download)
public/data/       the same real geojson/locality data as the Streamlit app
```
