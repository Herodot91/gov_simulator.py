# Florești Metropole — React port

A React + Vite port of the Streamlit app in the repo root, with the same
feature set: real-time simulation, the 5 scripted scenarios, the
Metropole → Municipality → District governance drill-down (map click or
list click), layer-scoped development projects with map markers, the
Zelenograd-model Technopolis Okrugs with browsable company product
catalogs, the FlorTech and AgroFlor university campus/faculty/department
drill-downs, the public transit network (Metro M1/M2, Tram T1, BRT/Bus/Regional Rail
road+regional transit, all interchanging at Gara Florești) with
named-street routes and interchange markers, the Metropolitan Ring Road,
Technopolis Expressway and Regional Expressway, the Coach
Terminal/Airport/Centrul Civic/CBD zone/Florești HPP (Răut river,
HydroTechnique Ltd.) map sites, each governance tier's
own directorates/departments org chart (plus interactive Prefecture
Policies, two Prefecture Towns — each with an expanded, dashed-circle
territory, its own town council/policies, and a non-mono-industrial
factory roster — a Current Policies review panel, a consolidated
Directorates Dashboard, and an Industries & Schools Dashboard of every
location's factories/products/sectors and schools, incl. six fictional
international schools), on-map district boundaries once a municipality is
selected, and CSV/JSON export. Vanilla CSS throughout — no UI framework.
See the [root README](../README.md) for the full rationale behind each
feature.

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
                    Civic District, and CBD zone),
                    directorates.js (Prefecture/Metro Council directorates,
                    Prefecture Policies, Prefecture Towns with their own
                    town councils/policies, per-municipality departments,
                    per-district civic offices, FACTORIES and SCHOOLS per
                    location for the Industries & Schools Dashboard)
  state/           SimulationContext.jsx — the whole game state as a reducer
                    (incl. resolvedScenarios, for the Current Policies panel)
  components/      Sidebar, ScenarioPanel, ScoreChart (hand-rolled SVG),
                    CitizenProgressCard, MetroMap (react-leaflet, incl. the
                    FlorTech/AgroFlor campus markers, the transit lines/
                    interchange markers, the Ring Road/Expressway, the
                    Coach Terminal/Centrul Civic markers, the Prefecture
                    Towns' dashed territory circles, CBD zone rectangle,
                    and the on-map district quadrant overlay),
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
                    a Research Centers & Labs list per campus),
                    DirectoratesDashboard (every tier's directorates/
                    departments/civic offices flattened into one panel),
                    IndustriesSchoolsDashboard (every location's factories
                    — name/sector/products — and schools, split into
                    "beside the metropole" Prefecture Towns and "within the
                    metropole" municipalities/suburbs/Ciripcău)
  utils/           geo.js (point-in-polygon, zoom-fit, and Sutherland-Hodgman
                    polygon clipping for the district quadrant overlay --
                    small manual replacements for the Python app's shapely
                    calls), export.js (CSV/JSON download)
public/data/       the same real geojson/locality data as the Streamlit app
```
