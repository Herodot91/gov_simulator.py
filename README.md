# gov_simulator.py
Simulation of Moldova — Florești Metropole CivicTech Simulator.

A governance-simulation proof of concept aimed at policy makers, political
analysts, and staff at each tier of the metropole's own administration —
metropolitan city hall, a municipal council, or a district office — to
explore mixed-decentralization tradeoffs interactively rather than on paper.

A Streamlit app where you make a handful of scripted policy decisions
(metropole administration reform, education, procurement reform, green tech,
universities), then the simulation keeps running live: random world events
(investment, protests, grants, cyberattacks, ...) fire on their own and shift
Governance, Economy, Stability, and Risk in real time.

## Run it

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## React port

A full-feature-parity React + Vanilla CSS port of this app lives in
[`web/`](web/) — same simulation, same real map data, but a fully
client-side static app instead of a Streamlit/Python backend. See
[`web/README.md`](web/README.md) to run it.

## Real-time mode

- Each policy decision resolves the instant you click it — scores, budget,
  the live chart, and the Citizen Progress Card update immediately, no
  "submit" step.
- Once the five scripted scenarios are done, the sim enters an **Ongoing
  Governance** phase. Turn on **Live auto-play** in the sidebar and the world
  keeps evolving on its own tick after tick (speed adjustable), or trigger a
  single event manually with "Trigger next event now".
- History (scores per month) and the full event log can be exported at any
  point as CSV / JSON, even mid-run.

## Governance structure UI — drill-down navigation

The governance section follows the model's own layers, one screen at a
time: **Metropole → Municipality → District**.

- At the Metropole layer, the map shows all 4 municipalities at once.
  Click a municipality's shape on the map, or its name below the map, to
  drill into it.
- At the Municipality layer, its 4 districts are listed as buttons —
  click one to open it. Inauguration happens here too.
- At the District layer, you see which municipality it belongs to and
  its inauguration status. "← Back" always returns one layer up.

Once a municipality is selected, its own 4 districts are also drawn on the
map itself — its real territory split into a 2x2 quadrant grid (Florești's
districts aren't real cadastral units, so this is a legible approximation,
not a survey), each in its own color with a label, clickable the same way
municipalities are. This only appears once you've drilled into a
municipality, keeping the top-level metro map uncluttered.

## Development projects — one set per governance layer

Beyond the 5 scripted top-level scenarios, each layer of the drill-down has
its own real development projects to decide on, same interactive shape as
the scenarios (pick an option — Cost + Governance/Economy/Stability/Risk
effects — or Skip):

- **Metropolitan Projects** (shown at the Metropole layer, once the
  metropole is established): Florești Ring Road, Metro Line 1, and the
  Railway Station – Airport Link.
- **Municipal Projects** (shown at each Municipality layer, once that
  municipality is inaugurated): Răut Plaza in Florești Central, a New
  Avenue in Vărvăreuca.
- **District Projects** (shown at each District layer, once the parent
  municipality is inaugurated): a Community Park (Lunga's Green Belt
  District) and School Reconstruction (Lunga's Lunga Residential District).

Once you pick a real option for a project (not Skip), it shows up on the
metropole map itself: point projects get a 🏗️ marker near their real
location, corridor-shaped ones (the Railway Station – Airport Link, the
New Avenue) are drawn as a line between their two endpoints with a marker
at the midpoint. Hover any of them for the project name and the choice
made. Markers persist across the whole map regardless of which layer
you're currently viewing.

A municipality's/district's projects stay locked with a note to inaugurate
first — same gate as the district detail view itself.

### CBD masterplan

Florești Central's municipal view also has a **📐 View CBD Masterplan**
expander — a concept site plan (`data/cbd_masterplan.svg`) for a new
central business district on the riverside land between Centrul Civic and
the Răut, anchored on the Metro Line 1 station and the Răut Plaza project.
It's illustrative context, not tied to any score effects or budget cost of
its own.

## Governance model — mixed decentralization

Choosing **B) Establish Florești Metropole** in Scenario 1 ("Florești
Metropole Administration Reform") activates an Istanbul/Budapest-style
two-tier governance structure, carved out of a fictional French-style
**Florești Prefecture** (standing in for the real Moldovan raion) instead of
the raion system itself:

- **Florești Prefecture** — the outer, French-style administrative region
  (real OpenStreetMap boundary of Raionul Florești, reframed for this sim).
- **Florești Metropole** — the metropolitan tier carved out within it.
- 4 **municipalities**, each with real local government once inaugurated
  (budget cost + a small Governance/Stability boost), each with 4 named
  districts: Florești Central, Mărculești, Vărvăreuca, Lunga.
- 2 **suburbs** (Ghindești, Gura Camencii) — administratively dependent on
  the metropole, no local government of their own.
- 2 **Technopolis Okrugs** (Prajila, Ciripcău) — see below.

### A second model, alongside the French one: Zelenograd-style okrugs

The French-prefecture reframing covers the raion-to-prefecture and
metropole/municipality/district layers. A separate, second borrowing —
from Moscow this time — covers two real villages that sit **outside** the
metropole's own territory: **Prajila** and **Ciripcău**, after
**Zelenograd**, Moscow's own physically detached, single-industry
administrative okrug (real-world Russia's microelectronics hub). Each is
sponsored by the metropole as a one-company technopolis rather than folded
into ordinary municipal government:

- **Prajila** — home to **PHI (Prajila Heavy Industry)**, a fictional
  heavy-machinery and construction-equipment maker (an alternative to
  Hitachi, Caterpillar, Komatsu, Hyundai's construction arm).
- **Ciripcău** — home to **Sigma Motors**, a fictional hybrid/EV automaker
  (coupé, hatchback, urban SUV lines).

This is structural world-building, not a scenario: it's shown as a plain
info panel (🏭 Technopolis Okrugs, next to the 🏘️ Suburbs panel at the
Metropole layer) with no budget cost, no score effects. Each company's
name is itself a nested expander — 🔧 *Company — product line (n)* — with
a browsable catalog of its named models: PHI's 10-model heavy-equipment
line (excavators, wheel loaders, dozers, graders, cranes, dump trucks,
a skid-steer), and Sigma Motors' 5-model hybrid/EV line (coupé, hatchback
in both hybrid and EV trims, urban SUV in both trims).

Both okrugs are also marked directly on the metropole map itself — a small
dashed gold circle at each village's real coordinates (distinct from the
4 municipalities' solid fill, so it doesn't read as a 5th ordinary
municipality), labeled with the village name and its company. Since real
Prajila and Ciripcău sit outside the metropole's own territory — Ciripcău
well to the northeast — the map's fitted view widens to include both
alongside the 4 municipalities, the same way a real Moscow map has to
zoom out to fit Zelenograd in alongside the city proper.

The structure is shown as a real street-level Leaflet map, not a schematic
diagram: each of the 4 municipalities starts from its actual current
territory — the real OpenStreetMap administrative boundary (admin_level=8)
of Florești, Mărculești, Vărvăreuca, and Lunga — with a few deliberate real
adjustments on top:

- **Mărculești is one unified territory comprising its own whole real
  village *and* the whole real airport** — the actual "orașul Mărculești"
  admin boundary, plus the real Mărculești International Airport (OSM
  aerodrome `LUBM`), matching its own "Airport District", still linked by
  the real ~120m corridor between them. Only the *village's own* edge is
  smoothed with a small buffered convex hull (so it doesn't interlock with
  Lunga's raw boundary in a way that reads as "Mărculești trapped inside
  Lunga"); the airport/corridor stretch keeps its real boundary as-is.
  An earlier version of this fix hulled the village *and* airport
  together, which swept a huge convex sheet across ~2km of Lunga's real
  territory and swallowed Lunga's actual named locality — hulling only
  the village avoids that while keeping every real locality point
  (Lunga's own village, Mărculești's town center, the full airport) inside
  its correct municipality. Mărculești does **not** touch Florești Central
  or Vărvăreuca directly — its boundary is kept at least ~130m clear of
  Florești Central everywhere, so at normal map zoom it never reads as
  touching the corridor that only Lunga uses.
- **Lunga comprises the real Lunga village**, including its own real
  named locality, minus only the small piece ceded to Mărculești's
  village-hull edge above, plus its real-gap corridor out to Florești
  Central — widened beyond its literal narrow real-world width so the
  connection reads as an unmistakable, solid merge at normal map zoom
  instead of a thin, easy-to-miss sliver. Florești Central and Mărculești
  are *not* linked directly — Lunga is the only path between them, same
  as the real geography (Mărculești/the airport sit well southwest of
  both).
- **Vărvăreuca** is trimmed inward from its full rural comuna boundary
  toward its built-up core, so it doesn't dominate the map with a long thin
  spike of open farmland, and still borders Florești Central directly —
  that border is likewise widened for a clearly visible merge.

Florești Metropole is the union of all four — verified hole-free, with zero
overlap between any two municipalities that aren't directly bridged (bridged
pairs share a small strip of jointly-claimed corridor by construction, same
as any shared border). The map view is fit tightly to that merged territory
only (no suburbs, no extra padding out to the full prefecture), computed
once and baked into `data/floresti_municipalities.geojson`. Inaugurated
municipalities render with a bright fill; the rest stay muted. Suburbs
(Ghindești, Gura Camencii) are listed in the app but not drawn on the map
as territory, keeping its extent to just the 4 merged municipalities —
the Technopolis Okrugs get their own dashed-circle map markers instead,
described above.

## FlorTech — Florești University of Technology

A second piece of structural world-building, alongside the Technopolis
Okrugs: a mass development that grows the real **Școala Profesională din
Florești** (a real vocational school) into a full technical university,
without replacing it — the vocational tracks continue to run alongside
the new university, not folded into it.

Shown as its own top-level panel (🎓 FlorTech — Florești University of
Technology), right after the Governance Structure panel, once the
metropole is established. It has no cost or score effects — it's browsable
content, same as the Technopolis Okrugs.

- **6 campuses**, spread across the metropole's municipalities, its
  suburbs, and the two Technopolis Okrugs, each tied to that location's own
  theming already established elsewhere in the app:
  - **Central Campus** (Florești Central, Politeh District) — Electrical/
    Electronics/Telecom + Programming & Cybersecurity; Civil Engineering,
    Architecture & Urban Planning; Engineering Economics.
  - **Mărculești Campus** (Aviagorodok) — Transportation Engineering,
    Automation & Computer Engineering.
  - **Vărvăreuca Campus** (Agricultural District) — Applied Natural
    Sciences in Engineering, Food Engineering.
  - **Lunga Campus** (Artisan Quarter) — Industrial Design, Interior
    Design, Textile Engineering & Design.
  - **Prajila Campus** (PHI-sponsored) — Mechanical, Industrial, and
    Construction Engineering, Mining (incl. Oil & Gas), Robotics &
    Mechatronics — mirroring PHI's own heavy-machinery identity.
  - **Ciripcău Campus** (Sigma Motors-sponsored) — Automotive Design,
    Electrical Engineering (EV Systems), Robotics & Mechatronics —
    mirroring Sigma Motors' own EV identity.

  Between them, the 6 campuses cover every field requested: design
  (automotive, industrial, interior), engineering economics, robotics &
  mechatronics, applied natural sciences in engineering, architecture,
  urban planning, mechanical engineering, transportation engineering,
  electrical engineering, industrial engineering, construction
  engineering, programming & cybersecurity, telecommunications,
  electronics & microelectronics, mining (incl. oil & gas), textile
  engineering & design, food engineering, and automation & computer
  science/engineering.

- Click a campus to drill into its faculties and departments, each
  department offered at that campus's own degree levels — up to BEng,
  BSc, MEng, MSc, PhD, and Postdoc at the flagship Central Campus, a
  narrower BEng/MEng/MSc band at the specialist campuses. "← Back to
  FlorTech" returns to the campus grid.
- Each campus also gets its own 🎓 marker on the metropole map itself, at
  a point near its home municipality/okrug — click the marker (same as
  clicking a municipality's shape, or an okrug's circle) to drill straight
  into that campus's detail, no need to scroll to the campus grid first.
- A **🛠️ Vocational Institutes** expander lists the two branches keeping
  Școala Profesională's own non-degree tracks running: Electrical
  Technician, Automotive Mechanic, Welding & Metalwork, CNC Machining
  (Ghindești branch), and Construction Trades, HVAC Technician, Industrial
  Maintenance (Gura Camencii branch).

## AgroFlor — Florești University of Agricultural Sciences and Technologies

A second university, alongside FlorTech: grew out of Scenario 5's
investment in a Vărvăreuca agricultural college into a full
metropole-wide university — campuses across every municipality and both
suburbs (not the Technopolis Okrugs, which stay single-company rather
than academic). Same shape as FlorTech: its own top-level panel (🌾
AgroFlor...), no cost or score effects, browsable content only, gated on
the metropole being established.

- **6 campuses**, one per municipality plus one per suburb:
  - **Vărvăreuca Campus** (Agricultural District, the flagship) —
    Agronomy, Horticulture, Crop Engineering; Genetics & Plant Breeding,
    Biotechnology.
  - **Central Campus** (Politeh District) — Agricultural Economics,
    Sustainable Development, Rural Planning.
  - **Mărculești Campus** (Aviagorodok) — Agricultural Machinery
    Engineering, Agritech & Precision Farming.
  - **Lunga Campus** (Artisan Quarter) — Animal Husbandry, Veterinary
    Medicine.
  - **Ghindești Campus** (suburb) — Food Engineering, Biology, Chemistry.
  - **Gura Camencii Campus** (suburb) — Physics, Informatics & Applied
    Mathematics in Agriculture.

  Between them, the 6 campuses cover every field requested: agronomy,
  horticulture, crop engineering, genetics, biotechnology, plant growth
  and genetics, food engineering, agricultural economics, sustainable
  development, husbandry and veterinary medicine, agricultural machinery
  engineering and agritech, biology, chemistry, physics, informatics and
  math applications in agriculture, and rural planning.

- Click a campus to drill into its faculties/departments (offered at that
  campus's own degree levels — BSc/MSc/PhD/Postdoc at the flagship
  Vărvăreuca and Central campuses, a narrower band at the specialist
  campuses) **and** its 🔬 Research Centers & Labs — e.g. the Crop
  Genetics Research Center and Soil & Water Sustainability Lab at
  Vărvăreuca, the Animal Health Research Lab at Lunga.
- Each campus also gets its own 🌾 marker on the metropole map — a green
  badge distinct from FlorTech's navy 🎓 badges so the two universities'
  campuses read apart at a glance, even where both have a campus in the
  same municipality (e.g. Florești Central). Click the marker to drill
  straight into that campus's detail, same as FlorTech's markers.

## Public Transit Network

A third piece of structural world-building shown on the metropole map:
the network of tram, bus, and commuter rail lines that actually move
people around. No cost, no score effects — always drawn once the
metropole is established, alongside its own **🚊 Public Transit Network**
expander (next to Suburbs and Technopolis Okrugs) listing every line's
stops in order.

- **The metro system runs on trams**, not heavy rail: **Tram M1**
  (Vărvăreuca → Florești Central → Lunga → Mărculești) is the backbone,
  tracing the same real municipal corridors the map's own territory is
  built from (Mărculești is only ever reachable via Lunga); **Tram M2**
  (Ghindești → Florești Central → Vărvăreuca) extends tram service out to
  the Ghindești suburb.
- **BRT 1** (biogas/electric buses) covers what the trams don't: Gura
  Camencii → Florești Central → Mărculești Airport.
- **Two commuter rail lines** reach past the metropole's own territory —
  **Commuter C1**: Ghindești → Florești Central → Lunga → Mărculești
  Airport → Gura Căinarului (a real village further west); **Commuter
  C2**: Gura Camencii → Florești Central → Lunga → Prajila, reaching the
  Prajila Technopolis Okrug.
- Each line is drawn on the map in its own color, styled by mode — trams
  solid, BRT dashed (it's a bus corridor, not rail), commuter rail
  dash-dotted — with a hover tooltip listing its full stop sequence.
- **Interchanges** — any stop served by 2+ lines — get a white-on-black
  ring marker (⇄), computed from the lines' own stop lists rather than
  hardcoded: Florești Central is the 5-way hub (both trams, BRT, both
  commuter lines); Vărvăreuca (both trams), Lunga, Ghindești, Gura
  Camencii, and Mărculești Airport are each 2–3-way interchanges between
  trams, the BRT line, and the commuter lines.
- The map's auto-fit view widens once more (past the Technopolis Okrugs)
  to keep the whole network in frame, including Gura Căinarului out past
  Prajila to the west.

## Directorates & Departments

The app is built for real users at each governance tier — the
metropolitan council, the prefecture, a municipal council, a district
office — to work through policy and project decisions the way their own
administration is actually organized. Every tier now shows its own
organizational chart: purely descriptive world-building (no cost, no
score effects), same shape as everything else in this section.

- **🏛️ Florești Prefecture — Directorates (4)**, shown at the top of the
  Governance Structure section regardless of whether the metropole has
  been established — the prefecture is the outer state tier the metropole
  gets carved out of, so it's in effect either way. Public Order & Civil
  Protection, State Finance & Treasury Oversight, Public Administration &
  Legal Affairs, Civil Registry & Documents.
- **🏢 Metropolitan Council — Directorates (6)**, alongside Suburbs,
  Technopolis Okrugs, and the transit network at the Metropole layer, once
  established: Urban Planning & Territorial Development, Transport &
  Infrastructure, Economic Development & Investment, Environment &
  Sustainability, Education & Culture, Health & Social Assistance.
- **🏢 Departments (3 each)**, one per municipality, shown in that
  municipality's own drill-down view: two generic departments every
  municipality needs (Municipal Finance, Public Services) plus one
  thematic department tied to its established identity — Urban
  Development & CBD Management at Florești Central, Transport & Airport
  Liaison at Mărculești, Agriculture & Rural Development at Vărvăreuca,
  Local Economy & Crafts at Lunga.
- **🏢 Civic Office**, one per district (16 total), shown in that
  district's own drill-down view — districts sit below the municipal
  tier, so each gets a single lightweight office (e.g. "Politeh Civic
  Office") rather than a full directorate roster of its own, framed as a
  first-line liaison to its municipality's council.

### Prefecture Policies — a fourth decision-making layer

Unlike the directorates above, the prefecture also gets real interactive
policies to decide on — same Cost + Governance/Economy/Stability/Risk
shape as every other scenario/project in the app, always available
(the prefecture is in effect with or without the metropole): **Property
Tax Reform**, **State Digital Services Modernization**, and **Civil
Protection Budget**. This closes the gap where three of the four
governance tiers (metropole, municipality, district) already had
projects to resolve but the prefecture only had a read-only directorates
list.

### Current Policies — reviewing what's already been decided

The 5 top-level scenarios disappear from the main flow once resolved
(only the text Log kept a record). A **📋 Current Policies** expander at
the Metropole layer, next to the Metropolitan Council directorates, now
lists every resolved scenario with the option actually chosen, so you can
review past decisions without digging through the log.
