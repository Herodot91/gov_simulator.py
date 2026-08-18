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
(Ghindești, Gura Camencii, Prajila) are listed in the app but not drawn on
the map, keeping its extent to just the 4 merged municipalities.
