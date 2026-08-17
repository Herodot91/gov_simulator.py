# gov_simulator.py
Simulation of Moldova — Florești Metropole CivicTech Simulator.

A Streamlit app where you make a handful of scripted policy decisions
(customs, education, procurement reform, green tech, universities), then the
simulation keeps running live: random world events (investment, protests,
grants, cyberattacks, ...) fire on their own and shift Governance, Economy,
Stability, and Risk in real time.

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

Choosing **B) Decentralize to regions** in Scenario 1 activates an
Istanbul/Budapest-style two-tier governance structure over the real Florești
District, Moldova:

- **Florești Metropole** — the metropolitan tier.
- 4 **municipalities**, each with real local government once inaugurated
  (budget cost + a small Governance/Stability boost), each with 4 named
  districts: Florești Central, Mărculești, Vărvăreuca, Lunga.
- 3 **suburbs** (Ghindești, Gura Camencii, Prajila) — administratively
  dependent on the metropole, no local government of their own.

The structure is shown two ways: a glowing schematic diagram (metropole →
municipalities → districts) and a real Leaflet map built from OpenStreetMap
data (district boundary + all 73 real towns/villages).
