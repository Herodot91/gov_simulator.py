# app.py (real-time)
import os
import math
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

# Governance model: mixed decentralization (Istanbul + Budapest hybrid) — a
# metropolitan tier over 4 municipalities (each with real local government and
# its own sub-districts, like Istanbul's ilçe / Budapest's kerület), plus
# dependent suburbs with no independent government of their own.
METRO_STRUCTURE = {
    "Florești Central": {
        "anchor": "Florești", "angle": 270,
        "districts": ["Civic District", "Central Market District",
                      "Răut Riverside District", "University District"],
    },
    "Mărculești": {
        "anchor": "Mărculești", "angle": 0,
        "districts": ["Airport District", "Industrial District",
                      "Logistics District", "Mărculești Residential District"],
    },
    "Vărvăreuca": {
        "anchor": "Vărvăreuca", "angle": 90,
        "districts": ["Vărvăreuca Residential District", "Agricultural District",
                      "Forestry District", "Heritage Quarter"],
    },
    "Lunga": {
        "anchor": "Lunga", "angle": 180,
        "districts": ["Lunga Residential District", "Orchard District",
                      "Green Belt District", "Artisan Quarter"],
    },
}
SUBURBS = [
    {"name": "Ghindești", "angle": 45},
    {"name": "Gura Camencii", "angle": 135},
    {"name": "Prajila", "angle": 225},
]
MUNICIPALITY_COLORS = {"Florești Central": "#4cc9f0", "Mărculești": "#f4a261",
                        "Vărvăreuca": "#8ab17d", "Lunga": "#e76f51"}
INAUGURATION_COST = 15


@st.cache_data
def load_geo_data():
    with open(os.path.join(DATA_DIR, "floresti_localities.json"), encoding="utf-8") as f:
        localities = json.load(f)
    with open(os.path.join(DATA_DIR, "floresti_district.geojson"), encoding="utf-8") as f:
        boundary = json.load(f)
    return localities, boundary


LOCALITIES, DISTRICT_BOUNDARY = load_geo_data()
LOCALITIES_BY_ID = {loc["id"]: loc for loc in LOCALITIES}


def find_locality(name):
    """Look up a locality by name, preferring the 'town' entry when a village shares the name."""
    matches = [loc for loc in LOCALITIES if loc["name"] == name]
    towns = [loc for loc in matches if loc["type"] == "town"]
    return (towns or matches)[0]

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
    st.session_state.metro_active = False
    st.session_state.inaugurated = []


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
        st.session_state.metro_active = True
        note += (" | 🏙️ Mixed-decentralization governance enabled — Florești Metropole can now "
                  "inaugurate its municipalities below.")
    record(note)
    st.session_state.turn += 1


def inaugurate_municipality(name):
    st.session_state.sim_month += 1
    if name in st.session_state.inaugurated:
        return
    if st.session_state.budget < INAUGURATION_COST:
        record(f"Month {st.session_state.sim_month}: Not enough budget ({INAUGURATION_COST}) "
               f"to inaugurate {name}. Skipped.")
        return
    st.session_state.budget -= INAUGURATION_COST
    st.session_state.inaugurated.append(name)
    apply_effects({"Governance": +4, "Stability": +3})
    districts = ", ".join(METRO_STRUCTURE[name]["districts"])
    record(f"Month {st.session_state.sim_month}: 🏛️ {name} municipality inaugurated — "
           f"districts: {districts} | Cost {INAUGURATION_COST} "
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

    for name, info in METRO_STRUCTURE.items():
        loc = find_locality(info["anchor"])
        color = MUNICIPALITY_COLORS[name]
        active = name in st.session_state.inaugurated
        folium.CircleMarker(
            location=[loc["lat"], loc["lon"]],
            radius=11 if active else 8,
            color=color, fill=True, fill_color=color if active else "#ffffff",
            fill_opacity=0.95 if active else 0.5, weight=3 if active else 2,
            popup=f"{name} municipality (anchor: {loc['display_name']}) — "
                  f"{'inaugurated' if active else 'not yet inaugurated'}",
            tooltip=f"{name} {'✅' if active else '(not yet inaugurated)'}",
        ).add_to(m)

    for suburb in SUBURBS:
        loc = find_locality(suburb["name"])
        folium.CircleMarker(
            location=[loc["lat"], loc["lon"]],
            radius=5, color="#8a8f98", fill=True, fill_color="#c9ccd1", fill_opacity=0.8, weight=1,
            popup=f"{loc['display_name']} — dependent suburb of Florești Metropole",
            tooltip=f"{loc['display_name']} (suburb)",
        ).add_to(m)

    legend_rows = "".join(
        f'<div style="display:flex;align-items:center;gap:6px;margin:2px 0;">'
        f'<span style="width:12px;height:12px;border-radius:50%;background:{MUNICIPALITY_COLORS[n]};'
        f'display:inline-block;opacity:{1 if n in st.session_state.inaugurated else 0.35};"></span>'
        f'<span style="font-size:12px;">{n} {"✅" if n in st.session_state.inaugurated else ""}</span></div>'
        for n in METRO_STRUCTURE
    )
    legend_rows += (
        '<div style="margin-top:4px;font-weight:700;font-size:11px;">Suburbs</div>'
        + "".join(
            f'<div style="display:flex;align-items:center;gap:6px;margin:2px 0;">'
            f'<span style="width:10px;height:10px;border-radius:50%;background:#c9ccd1;display:inline-block;"></span>'
            f'<span style="font-size:12px;">{s["name"]}</span></div>'
            for s in SUBURBS
        )
    )
    legend_html = f'''
    <div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; background: white;
                padding: 10px 12px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.25);
                max-height: 260px; overflow-y: auto;">
      <div style="font-weight:700;font-size:12px;margin-bottom:4px;">Municipalities</div>
      {legend_rows}
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    return m


def build_metro_diagram():
    """Schematic Istanbul+Budapest-style hierarchy: metropole core -> municipalities -> districts,
    plus dependent suburbs, rendered as a glowing radial diagram."""
    cx, cy = 320, 320
    muni_r, dist_r, suburb_r = 190, 46, 260
    svg_parts = []

    def pt(radius, angle_deg, origin=(cx, cy)):
        rad = math.radians(angle_deg)
        return origin[0] + radius * math.cos(rad), origin[1] + radius * math.sin(rad)

    # metropole -> municipality lines + district fans
    for name, info in METRO_STRUCTURE.items():
        active = name in st.session_state.inaugurated
        color = MUNICIPALITY_COLORS[name] if active else "#4a5568"
        mx, my = pt(muni_r, info["angle"])
        svg_parts.append(
            f'<line x1="{cx}" y1="{cy}" x2="{mx:.1f}" y2="{my:.1f}" stroke="{color}" '
            f'stroke-width="{3 if active else 1.5}" opacity="{0.95 if active else 0.4}" '
            f'filter="{"url(#glow)" if active else ""}" />'
        )
        if active:
            for i, dname in enumerate(info["districts"]):
                d_angle = info["angle"] + (i - 1.5) * 22
                dx, dy = pt(dist_r, d_angle, origin=(mx, my))
                svg_parts.append(
                    f'<line x1="{mx:.1f}" y1="{my:.1f}" x2="{dx:.1f}" y2="{dy:.1f}" '
                    f'stroke="{color}" stroke-width="1.2" opacity="0.7" />'
                )
                svg_parts.append(
                    f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="6" fill="{color}" opacity="0.9">'
                    f'<title>{dname} ({name})</title></circle>'
                )
        svg_parts.append(
            f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="22" fill="{color if active else "#1a2332"}" '
            f'stroke="{color}" stroke-width="2.5" filter="{"url(#glow)" if active else ""}">'
            f'<title>{name}{" ✅ inaugurated" if active else " — not yet inaugurated"}</title></circle>'
        )
        angle = info["angle"] % 360
        anchor = "middle"
        lx, ly = mx, my
        if angle == 270:
            ly -= 32
        elif angle == 90:
            ly += 40
        elif angle == 0:
            lx += 14
            anchor = "start"
        elif angle == 180:
            lx -= 14
            anchor = "end"
        svg_parts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" fill="#eaf4ff" font-size="14" font-weight="700" '
            f'text-anchor="{anchor}">{name}</text>'
        )

    # metropole -> suburb dashed lines
    for suburb in SUBURBS:
        sx, sy = pt(suburb_r, suburb["angle"])
        svg_parts.append(
            f'<line x1="{cx}" y1="{cy}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="#5a6472" '
            f'stroke-width="1.5" stroke-dasharray="5,5" opacity="0.6" />'
        )
        svg_parts.append(
            f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="10" fill="#3a4252" stroke="#8a94a6" stroke-width="2">'
            f'<title>{suburb["name"]} — dependent suburb, no independent government</title></circle>'
        )
        angle = suburb["angle"]
        anchor = "start" if angle in (45,) else "end"
        dy = 22 if angle == 45 else (22 if angle == 135 else -18)
        svg_parts.append(
            f'<text x="{sx + (16 if anchor == "start" else -16):.1f}" y="{sy + dy:.1f}" fill="#9aa5b8" '
            f'font-size="11" text-anchor="{anchor}">{suburb["name"]}</text>'
        )

    # metropole core, drawn last so it sits on top
    svg_parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="38" fill="#e91e8c" opacity="0.9" filter="url(#glow)" />'
        f'<circle cx="{cx}" cy="{cy}" r="38" fill="none" stroke="#ffb3e6" stroke-width="2" />'
        f'<text x="{cx}" y="{cy - 4}" fill="#fff" font-size="13" font-weight="800" '
        f'text-anchor="middle">Florești</text>'
        f'<text x="{cx}" y="{cy + 12}" fill="#fff" font-size="13" font-weight="800" '
        f'text-anchor="middle">Metropole</text>'
    )

    svg = f'''
    <div style="background:linear-gradient(160deg,#0b1220 0%,#0a1830 100%);border:1px solid rgba(255,255,255,.08);
                border-radius:16px;padding:8px;box-shadow:0 8px 30px rgba(2,62,138,.25);">
      <svg viewBox="0 0 640 640" style="width:100%;height:auto;display:block;">
        <defs>
          <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" /><feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        {"".join(svg_parts)}
      </svg>
    </div>
    '''
    return svg


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
        "metro_active": st.session_state.metro_active,
        "inaugurated_municipalities": st.session_state.inaugurated,
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
        <div style="background:rgba(255,255,255,.06);padding:8px 10px;border-radius:10px;">Municipalities: <b>{len(st.session_state.inaugurated)}/{len(METRO_STRUCTURE)}</b></div>
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

# ---------- Governance structure: metropole, municipalities, districts ----------
st.subheader("🏙️ Florești Metropole — Governance Structure")
if not st.session_state.metro_active:
    st.info("Choose **B) Decentralize to regions** in Scenario 1 to activate mixed-decentralization "
            "governance: a metropolitan tier (Istanbul/Budapest-style) over 4 municipalities, each "
            "with its own local government and districts.")
else:
    st.caption("Mixed decentralization is in effect — each municipality below has real local "
               "government once inaugurated. Suburbs stay administratively dependent on the metropole.")

if st.session_state.metro_active:
    diagram_col, map_col = st.columns([1, 1], gap="large")
    with diagram_col:
        st.markdown(build_metro_diagram(), unsafe_allow_html=True)
    with map_col:
        st_folium(build_map(), height=460, use_container_width=True, key="metro_map")

    muni_cols = st.columns(4)
    for col, (name, info) in zip(muni_cols, METRO_STRUCTURE.items()):
        active = name in st.session_state.inaugurated
        anchor = find_locality(info["anchor"])
        with col:
            st.markdown(f"**{name}** {'✅' if active else ''}")
            st.caption(f"Anchor: {anchor['display_name']}")
            for d in info["districts"]:
                st.markdown(f"- {d}")
            if active:
                st.success("Inaugurated")
            else:
                if st.button(f"Inaugurate ({INAUGURATION_COST})", key=f"inaugurate_{name}",
                              disabled=st.session_state.budget < INAUGURATION_COST):
                    inaugurate_municipality(name)
                    st.rerun()

    with st.expander(f"🏘️ Suburbs ({len(SUBURBS)}) — dependent on the metropole, no local government"):
        for suburb in SUBURBS:
            loc = find_locality(suburb["name"])
            st.markdown(f"- **{loc['display_name']}** ({loc['type']})")
else:
    st_folium(build_map(), height=420, use_container_width=True, key="metro_map")

# ---------- Real-time clock loop ----------
# While auto-play is on, the app sleeps for one tick then reruns itself,
# firing a random world event each time — this is what keeps the
# simulation moving in real time without any extra polling/JS.
if st.session_state.autoplay:
    time.sleep(tick_interval)
    apply_random_tick()
    st.rerun()
