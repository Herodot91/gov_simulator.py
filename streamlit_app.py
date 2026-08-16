# app.py (real-time)
import os
import random
import time
import json
from copy import deepcopy

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Florești Metropole — CivicTech Simulator", layout="wide")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ROOT_DISTRICT = "Florești District"
DISTRICT_COLORS = ["#2a9d8f", "#e76f51", "#e9c46a", "#264653", "#f4a261",
                    "#8ab17d", "#6d597a", "#eaac8b", "#457b9d", "#bc6c25"]


@st.cache_data
def load_geo_data():
    with open(os.path.join(DATA_DIR, "floresti_localities.json"), encoding="utf-8") as f:
        localities = json.load(f)
    with open(os.path.join(DATA_DIR, "floresti_district.geojson"), encoding="utf-8") as f:
        boundary = json.load(f)
    return localities, boundary


LOCALITIES, DISTRICT_BOUNDARY = load_geo_data()
LOCALITIES_BY_ID = {loc["id"]: loc for loc in LOCALITIES}


def convex_hull(points):
    """Andrew's monotone chain. points: list of (lat, lon). No extra deps needed."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]

SCENARIOS = [
    {"title": "Decentralization of Customs & Border Police",
     "options": {"A": ("Centralize for control", {"Governance": -5, "Risk": +5}, 10),
                 "B": ("Decentralize to regions", {"Governance": +10, "Stability": +5}, 20)},
     "intl": "EU encourages decentralization."},
    {"title": "Create Technical University in Bender",
     "options": {"A": ("Skip investment", {"Economy": -5}, 0),
                 "B": ("IT faculty only", {"Economy": +5}, 15),
                 "C": ("Full technical university", {"Economy": +10, "Governance": +5}, 25)},
     "intl": "Russia warns against outside influence."},
    {"title": "Digital Justice & Procurement Reform",
     "options": {"A": ("Delay reform", {"Governance": -5}, 0),
                 "B": ("Implement transparency tools", {"Governance": +10, "Risk": -5}, 15)},
     "intl": "EU praises Moldova's rule of law improvement."},
    {"title": "Budget Allocation: Green Tech Factories",
     "options": {"A": ("One per region", {"Economy": +5}, 20),
                 "B": ("Ignore sector", {"Economy": -5}, 0)},
     "intl": "UN welcomes clean tech expansion."},
    {"title": "Education: New Agricultural Universities",
     "options": {"A": ("EU model in Taul, Karmanovo", {"Economy": +5, "Stability": +5}, 25),
                 "B": ("Keep colleges as-is", {"Economy": -5}, 0)},
     "intl": "Foreign students show interest in Moldova."},
]

# Ambient events that fire on their own once the clock is live, independent of
# the scripted policy decisions above — this is what makes the world keep
# moving in real time even while the player is deliberating.
RANDOM_EVENTS = [
    ("Foreign Direct Investment Surge", {"Economy": +3}, "Investors from the EU pour capital into Florești."),
    ("Border Smuggling Incident", {"Risk": +4, "Stability": -2}, "Customs intercepts a smuggling ring; public trust shaken."),
    ("Anti-Corruption Audit Released", {"Governance": +3, "Risk": -2}, "An independent audit boosts transparency confidence."),
    ("Energy Price Spike", {"Economy": -4, "Stability": -1}, "Regional energy costs surge, straining households."),
    ("Diaspora Remittance Boom", {"Economy": +2, "Stability": +1}, "The diaspora sends record remittances home."),
    ("Protest Over Public Services", {"Stability": -3, "Governance": -1}, "Citizens rally over slow service delivery."),
    ("EU Grant Approved", {"Economy": +4, "Governance": +2}, "Brussels approves a new development grant."),
    ("Cyberattack on Government Systems", {"Risk": +5, "Governance": -3}, "A cyberattack disrupts digital services."),
    ("Bumper Harvest", {"Economy": +3, "Stability": +2}, "Agricultural output exceeds expectations."),
    ("Regional Tension Escalates", {"Risk": +3, "Stability": -2}, "Cross-border tensions raise local anxiety."),
]

BASE = {"Governance": 50, "Economy": 50, "Stability": 50, "Risk": 50}


def clamp(v):
    return max(0, min(100, v))


def fmt_effects(eff):
    return ", ".join(f"{k} {'+' if v >= 0 else ''}{v}" for k, v in eff.items())


# ---------- Simulation state ----------

def reset_simulation(start_budget):
    st.session_state.scores = deepcopy(BASE)
    st.session_state.budget = start_budget
    st.session_state.start_budget = start_budget
    st.session_state.history = [deepcopy(BASE)]
    st.session_state.month_labels = ["Start"]
    st.session_state.logs = []
    st.session_state.turn = 0
    st.session_state.last_intl = ""
    st.session_state.sim_month = 0
    st.session_state.autoplay = False
    st.session_state.decentralized = False
    st.session_state.districts = {ROOT_DISTRICT: [loc["id"] for loc in LOCALITIES]}


if "scores" not in st.session_state:
    reset_simulation(100)


def record(note):
    st.session_state.history.append(deepcopy(st.session_state.scores))
    st.session_state.month_labels.append(f"M{st.session_state.sim_month}")
    st.session_state.logs.append(note)


def apply_effects(effects):
    for k, dv in effects.items():
        st.session_state.scores[k] = clamp(st.session_state.scores[k] + dv)


def resolve_choice(scenario, key):
    st.session_state.sim_month += 1
    if key is None:
        record(f"Month {st.session_state.sim_month}: Skipped — {scenario['title']}.")
        st.session_state.turn += 1
        return
    desc, effects, cost = scenario["options"][key]
    if st.session_state.budget < cost:
        record(f"Month {st.session_state.sim_month}: Not enough budget for {key}) {desc} "
               f"on '{scenario['title']}'. Skipped.")
        st.session_state.turn += 1
        return
    st.session_state.budget -= cost
    apply_effects(effects)
    st.session_state.last_intl = scenario["intl"]
    note = (f"Month {st.session_state.sim_month}: {scenario['title']} → {key}) {desc} "
            f"| Cost {cost} | Intl: {scenario['intl']} | Scores {st.session_state.scores} "
            f"| Budget {st.session_state.budget}")
    if st.session_state.mode == "Democracy":
        turnout = clamp(int(30 + 0.5 * st.session_state.scores["Stability"]))
        passed = (st.session_state.scores["Stability"] + st.session_state.scores["Governance"]) > 90
        note += f" | Vote: turnout {turnout}% → {'PASSED' if passed else 'FAILED'}"
    if scenario is SCENARIOS[0] and key == "B":
        st.session_state.decentralized = True
        note += " | 🗺️ Decentralization enabled — new districts can now be founded on the map below."
    record(note)
    st.session_state.turn += 1


def found_district(name, member_ids, cost):
    st.session_state.sim_month += 1
    if not member_ids or not name:
        return
    if name in st.session_state.districts:
        record(f"Month {st.session_state.sim_month}: District formation failed — '{name}' already exists.")
        return
    if st.session_state.budget < cost:
        record(f"Month {st.session_state.sim_month}: Not enough budget ({cost}) to found district '{name}'. Skipped.")
        return
    st.session_state.budget -= cost
    st.session_state.districts[ROOT_DISTRICT] = [
        i for i in st.session_state.districts[ROOT_DISTRICT] if i not in member_ids
    ]
    st.session_state.districts[name] = list(member_ids)
    apply_effects({"Governance": +5, "Stability": +3})
    names_preview = ", ".join(LOCALITIES_BY_ID[i]["display_name"] for i in member_ids[:5])
    more = "" if len(member_ids) <= 5 else f" +{len(member_ids) - 5} more"
    record(f"Month {st.session_state.sim_month}: 🏛️ New district founded — '{name}' "
           f"({len(member_ids)} localities: {names_preview}{more}) | Cost {cost} "
           f"| Scores {st.session_state.scores} | Budget {st.session_state.budget}")


def apply_random_tick():
    st.session_state.sim_month += 1
    title, effects, blurb = random.choice(RANDOM_EVENTS)
    apply_effects(effects)
    st.session_state.last_intl = blurb
    record(f"Month {st.session_state.sim_month}: 🌍 {title} — {blurb} | Scores {st.session_state.scores}")


def build_map():
    m = folium.Map(location=[47.90, 28.35], zoom_start=10, tiles="CartoDB positron")
    folium.GeoJson(
        DISTRICT_BOUNDARY,
        name="Florești District boundary",
        style_function=lambda f: {"color": "#333333", "weight": 2, "dashArray": "6,4", "fillOpacity": 0},
    ).add_to(m)

    for i, (dname, ids) in enumerate(st.session_state.districts.items()):
        color = DISTRICT_COLORS[i % len(DISTRICT_COLORS)]
        pts = [(LOCALITIES_BY_ID[i_]["lat"], LOCALITIES_BY_ID[i_]["lon"])
               for i_ in ids if i_ in LOCALITIES_BY_ID]
        if dname != ROOT_DISTRICT and len(pts) >= 3:
            hull = convex_hull(pts)
            folium.Polygon(
                hull, color=color, weight=2, fill=True, fill_opacity=0.18,
                tooltip=f"{dname} ({len(ids)} localities)",
            ).add_to(m)
        for loc_id in ids:
            loc = LOCALITIES_BY_ID.get(loc_id)
            if not loc:
                continue
            folium.CircleMarker(
                location=[loc["lat"], loc["lon"]],
                radius=7 if loc["type"] == "town" else 4,
                color=color, fill=True, fill_color=color, fill_opacity=0.9, weight=1,
                popup=f"{loc['display_name']} ({loc['type']}) — {dname}",
                tooltip=loc["display_name"],
            ).add_to(m)

    legend_items = "".join(
        f'<div style="display:flex;align-items:center;gap:6px;margin:2px 0;">'
        f'<span style="width:12px;height:12px;border-radius:50%;background:{DISTRICT_COLORS[i % len(DISTRICT_COLORS)]};display:inline-block;"></span>'
        f'<span style="font-size:12px;">{dname} ({len(ids)})</span></div>'
        for i, (dname, ids) in enumerate(st.session_state.districts.items())
    )
    legend_html = f'''
    <div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; background: white;
                padding: 10px 12px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.25);
                max-height: 220px; overflow-y: auto;">
      <div style="font-weight:700;font-size:12px;margin-bottom:4px;">Districts</div>
      {legend_items}
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    return m


# ---------- Sidebar ----------
st.title("Florești Metropole — CivicTech Simulator")

with st.sidebar:
    st.session_state.mode = st.radio("Mode", ["Democracy", "Autocracy"], key="mode_radio",
                                      index=0 if st.session_state.get("mode", "Democracy") == "Democracy" else 1)

    start_budget_input = st.slider("Starting Budget (units)", 0, 150, st.session_state.start_budget, 5)
    if st.button("🔄 New Simulation"):
        reset_simulation(start_budget_input)
        st.rerun()

    st.divider()
    st.caption("Real-time clock")
    st.session_state.autoplay = st.checkbox(
        "▶️ Live auto-play (world keeps moving)", value=st.session_state.autoplay
    )
    tick_interval = st.slider("Tick speed (seconds)", 1, 10, 3)
    if st.session_state.autoplay:
        st.success("🟢 LIVE — simulation is ticking on its own.")
    else:
        st.info("⏸ Paused — nothing advances until you act or resume auto-play.")

# ---------- Live status row ----------
status_cols = st.columns(5)
prev = st.session_state.history[-2] if len(st.session_state.history) > 1 else st.session_state.history[-1]
scores = st.session_state.scores
status_cols[0].metric("🕒 Month", st.session_state.sim_month)
status_cols[1].metric("Governance", scores["Governance"], scores["Governance"] - prev["Governance"])
status_cols[2].metric("Economy", scores["Economy"], scores["Economy"] - prev["Economy"])
status_cols[3].metric("Stability", scores["Stability"], scores["Stability"] - prev["Stability"])
status_cols[4].metric("Risk", scores["Risk"], scores["Risk"] - prev["Risk"])

st.markdown(f"**Budget Left:** {st.session_state.budget} / {st.session_state.start_budget}")

# ---------- Decision / live-event area ----------
if st.session_state.turn < len(SCENARIOS):
    s = SCENARIOS[st.session_state.turn]
    st.subheader(f"📘 Scenario {st.session_state.turn + 1}: {s['title']}")
    st.caption(s["intl"])
    opt_items = list(s["options"].items())
    cols = st.columns(len(opt_items) + 1)
    for i, (k, v) in enumerate(opt_items):
        desc, effects, cost = v
        label = f"{k}) {desc}\nCost {cost} | {fmt_effects(effects)}"
        if cols[i].button(label, key=f"opt_{st.session_state.turn}_{k}", use_container_width=True):
            resolve_choice(s, k)
            st.rerun()
    if cols[-1].button("⏭️ Skip", key=f"skip_{st.session_state.turn}", use_container_width=True):
        resolve_choice(s, None)
        st.rerun()
else:
    st.subheader("🌐 Ongoing Governance")
    st.caption("All scripted decisions are resolved. The world keeps evolving live via random events.")
    if st.button("⚡ Trigger next event now"):
        apply_random_tick()
        st.rerun()

# ---------- Live chart + progress card ----------
df = pd.DataFrame(st.session_state.history, index=st.session_state.month_labels)

left, right = st.columns([2, 1], gap="large")

with left:
    fig, ax = plt.subplots(figsize=(7, 3))
    for col in df.columns:
        ax.plot(df.index, df[col], marker="o", label=col)
    ax.set_title("Score Evolution (live)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Score (0–100)")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    st.download_button("Download History CSV", df.to_csv().encode(), "history.csv", "text/csv")
    report = {
        "mode": st.session_state.mode,
        "starting_budget": st.session_state.start_budget,
        "current_budget": st.session_state.budget,
        "current_month": st.session_state.sim_month,
        "current_scores": st.session_state.scores,
        "districts": {name: len(ids) for name, ids in st.session_state.districts.items()},
        "log": st.session_state.logs,
    }
    st.download_button("Download Report JSON", json.dumps(report, indent=2).encode(),
                        "report.json", "application/json")
    st.text_area("Log", "\n".join(reversed(st.session_state.logs)), height=220)


def risk_badge(val: int):
    if val <= 33:
        return ('<span style="padding:4px 10px;border-radius:999px;background:rgba(42,157,143,.1);'
                'border:1px solid rgba(42,157,143,.35);color:#156b5d;font-weight:700;font-size:12px;">LOW RISK</span>')
    if val <= 66:
        return ('<span style="padding:4px 10px;border-radius:999px;background:rgba(255,183,3,.1);'
                'border:1px solid rgba(255,183,3,.35);color:#7a5a00;font-weight:700;font-size:12px;">MEDIUM RISK</span>')
    return ('<span style="padding:4px 10px;border-radius:999px;background:rgba(230,57,70,.1);'
            'border:1px solid rgba(230,57,70,.35);color:#8a1b23;font-weight:700;font-size:12px;">HIGH RISK</span>')


def bar_html(value, color):
    return f'''
      <div style="height:10px;background:#e9eef5;border-radius:999px;overflow:hidden;">
        <div style="height:100%;width:{int(value)}%;background:{color};transition:width .35s ease;"></div>
      </div>
    '''


with right:
    g, e, st_, r = scores["Governance"], scores["Economy"], scores["Stability"], scores["Risk"]
    live_dot = "🟢" if st.session_state.autoplay else "⚪"
    card_html = f"""
    <div style="background:linear-gradient(145deg,#0b1b2b 0%,#0a223a 100%);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:16px;color:#eaf4ff;box-shadow:0 8px 30px rgba(2,62,138,.18);">
      <h4 style="margin:0 0 8px 0;">{live_dot} Citizen Progress Card</h4>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px;font-size:12px;">
        <div style="background:rgba(255,255,255,.06);padding:8px 10px;border-radius:10px;">Month: <b>{st.session_state.sim_month}</b></div>
        <div style="background:rgba(255,255,255,.06);padding:8px 10px;border-radius:10px;">Budget: <b>{st.session_state.budget}</b></div>
        <div style="background:rgba(255,255,255,.06);padding:8px 10px;border-radius:10px;">Districts: <b>{len(st.session_state.districts)}</b></div>
        <div style="background:rgba(255,255,255,.06);padding:8px 10px;border-radius:10px;">Governance: <b>{g}</b></div>
        <div style="background:rgba(255,255,255,.06);padding:8px 10px;border-radius:10px;">Economy: <b>{e}</b></div>
        <div style="background:rgba(255,255,255,.06);padding:8px 10px;border-radius:10px;">Stability: <b>{st_}</b></div>
        <div style="background:rgba(255,255,255,.06);padding:8px 10px;border-radius:10px;">Risk: <b>{r}</b> {risk_badge(r)}</div>
      </div>
      <div style="margin-top:10px;font-size:12px;">Governance</div>
      {bar_html(g, '#4cc9f0')}
      <div style="margin-top:6px;font-size:12px;">Economy</div>
      {bar_html(e, '#48cae4')}
      <div style="margin-top:6px;font-size:12px;">Stability</div>
      {bar_html(st_, '#90e0ef')}
      <div style="margin-top:6px;font-size:12px;">Risk</div>
      {bar_html(r, '#e63946')}
      <div style="margin-top:8px;font-size:12px;color:#bfd8ff;">🌐 Last Intl Reaction: {st.session_state.last_intl or '—'}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# ---------- Regional map & district formation ----------
st.subheader("🗺️ Regional Map — Florești District")
if not st.session_state.decentralized:
    st.info("Choose **B) Decentralize to regions** in Scenario 1 to unlock founding new districts. "
            "The map below shows the real localities of Florești District, Moldova (OpenStreetMap data).")
else:
    st.caption("Decentralization is in effect — found new districts from real localities below.")

st_folium(build_map(), height=420, use_container_width=True, key="district_map")

if st.session_state.decentralized:
    unassigned = st.session_state.districts.get(ROOT_DISTRICT, [])
    if unassigned:
        with st.expander("🏛️ Found a New District"):
            options = sorted(unassigned, key=lambda i_: LOCALITIES_BY_ID[i_]["display_name"])
            picked = st.multiselect(
                "Localities to split off",
                options=options,
                format_func=lambda i_: f"{LOCALITIES_BY_ID[i_]['display_name']} ({LOCALITIES_BY_ID[i_]['type']})",
                key="district_picker",
            )
            new_name = st.text_input("New district name", key="new_district_name",
                                      placeholder="e.g. Ghindești District")
            cost = max(10, 4 * len(picked))
            st.caption(f"Cost: {cost} units | Effect: Governance +5, Stability +3")
            if st.button("🏛️ Found District", disabled=not picked or not new_name.strip()):
                found_district(new_name.strip(), picked, cost)
                st.rerun()
    else:
        st.success("All localities have been assigned to a district.")

    if len(st.session_state.districts) > 1:
        st.markdown("**Current districts:**")
        for dname, ids in st.session_state.districts.items():
            towns = [LOCALITIES_BY_ID[i_]["display_name"] for i_ in ids
                     if LOCALITIES_BY_ID.get(i_, {}).get("type") == "town"]
            extra = f" (incl. {', '.join(towns)})" if towns else ""
            st.markdown(f"- **{dname}** — {len(ids)} localities{extra}")

# ---------- Real-time clock loop ----------
# While auto-play is on, the app sleeps for one tick then reruns itself,
# firing a random world event each time — this is what keeps the
# simulation moving in real time without any extra polling/JS.
if st.session_state.autoplay:
    time.sleep(tick_interval)
    apply_random_tick()
    st.rerun()
