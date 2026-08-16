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
