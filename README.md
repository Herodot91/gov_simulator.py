# gov_simulator.py
Simulation of Moldova — Florești Metropole CivicTech Simulator.

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
- 3 **suburbs** (Ghindești, Gura Camencii, Prajila) — administratively
  dependent on the metropole, no local government of their own.

The structure is shown as a real street-level Leaflet map, not a schematic
diagram: each of the 4 municipalities starts from its actual current
territory — the real OpenStreetMap administrative boundary (admin_level=8)
of Florești, Mărculești, Vărvăreuca, and Lunga — with a few deliberate real
adjustments on top:

- **Mărculești is one unified territory comprising its own whole real
  village *and* the whole real airport** — the actual "orașul Mărculești"
  admin boundary, plus the real Mărculești International Airport (OSM
  aerodrome `LUBM`), matching its own "Airport District", joined by a
  ~120m corridor across the strip of Lunga's real land between them (the
  real village already reaches its own open exterior, so this corridor
  gives the whole shape genuine outside access without a separate hole to
  patch).
- **Lunga comprises the whole real Lunga village** minus only the sliver
  needed for that corridor. When the village-airport corridor is cut out,
  Lunga's real boundary happens to stay in one connected piece (no need to
  fold any part of it elsewhere) and still keeps its narrow real-gap
  corridor out to Florești Central. Florești Central and Mărculești are
  *not* linked directly — Lunga is the only path between them, same as the
  real geography (Mărculești/the airport sit well southwest of both).
- **Vărvăreuca** is trimmed inward from its full rural comuna boundary
  toward its built-up core, so it doesn't dominate the map with a long thin
  spike of open farmland, and still borders Florești Central directly.

Florești Metropole is the union of all four — verified hole-free, with zero
overlap between any two municipalities that aren't directly bridged (bridged
pairs share a small strip of jointly-claimed corridor by construction, same
as any shared border). The map view is fit tightly to that merged territory
only (no suburbs, no extra padding out to the full prefecture), computed
once and baked into `data/floresti_municipalities.geojson`. Inaugurated
municipalities render with a bright fill; the rest stay muted. Suburbs
(Ghindești, Gura Camencii, Prajila) are listed in the app but not drawn on
the map, keeping its extent to just the 4 merged municipalities.
