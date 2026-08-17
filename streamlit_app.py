# app.py (real-time)
import os
import random
import time
import json
from copy import deepcopy

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, MultiPoint, shape, mapping

st.set_page_config(page_title="Florești Metropole — CivicTech Simulator", layout="wide")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Governance model: mixed decentralization (Istanbul + Budapest hybrid) — a
# metropolitan tier over 4 municipalities (each with real local government and
# its own sub-districts, like Istanbul's ilçe / Budapest's kerület), plus
# dependent suburbs with no independent government of their own.
METRO_STRUCTURE = {
    "Florești Central": {
        "anchor": "Florești",
        "districts": ["Civic District", "Central Market District",
                      "Răut Riverside District", "University District"],
    },
    "Mărculești": {
        "anchor": "Mărculești",
        "districts": ["Airport District", "Industrial District",
                      "Logistics District", "Mărculești Residential District"],
    },
    "Vărvăreuca": {
        "anchor": "Vărvăreuca",
        "districts": ["Vărvăreuca Residential District", "Agricultural District",
                      "Forestry District", "Heritage Quarter"],
    },
    "Lunga": {
        "anchor": "Lunga",
        "districts": ["Lunga Residential District", "Orchard District",
                      "Green Belt District", "Artisan Quarter"],
    },
}
SUBURBS = [{"name": "Ghindești"}, {"name": "Gura Camencii"}, {"name": "Prajila"}]
MUNICIPALITY_COLORS = {"Florești Central": "#4cc9f0", "Mărculești": "#f4a261",
                        "Vărvăreuca": "#8ab17d", "Lunga": "#e76f51"}
INAUGURATION_COST = 15


@st.cache_data
def load_geo_data():
    with open(os.path.join(DATA_DIR, "floresti_localities.json"), encoding="utf-8") as f:
        localities = json.load(f)
    # Real OSM boundary of "Raionul Florești" (the Moldovan raion) — reused
    # here as the outer footprint for the fictional French-style "Florești
    # Prefecture" this simulation models instead of the raion system.
    with open(os.path.join(DATA_DIR, "floresti_district.geojson"), encoding="utf-8") as f:
        boundary = json.load(f)
    return localities, boundary


LOCALITIES, PREFECTURE_BOUNDARY = load_geo_data()


def find_locality(name):
    """Look up a locality by name, preferring the 'town' entry when a village shares the name."""
    matches = [loc for loc in LOCALITIES if loc["name"] == name]
    towns = [loc for loc in matches if loc["type"] == "town"]
    return (towns or matches)[0]


def _voronoi_finite_polygons_2d(vor, radius):
    """Reconstruct infinite Voronoi regions as finite polygons by extending
    unbounded ridges out past the given radius. Standard recipe: unbounded
    Voronoi cells (for seed points on the convex hull) have no far vertex, so
    each open ridge is projected outward before the region can be closed."""
    new_regions = []
    new_vertices = vor.vertices.tolist()
    center = vor.points.mean(axis=0)

    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    for p1, region_index in enumerate(vor.point_region):
        vertices = vor.regions[region_index]
        if all(v >= 0 for v in vertices):
            new_regions.append(vertices)
            continue
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]
        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                continue
            t = vor.points[p2] - vor.points[p1]
            t = t / np.linalg.norm(t)
            n = np.array([-t[1], t[0]])
            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius
            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:, 1] - c[1], vs[:, 0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]
        new_regions.append(new_region.tolist())
    return new_regions, np.asarray(new_vertices)


@st.cache_data
def compute_metro_polygons():
    """Real, non-overlapping territory for each municipality/suburb: a Voronoi
    tessellation seeded at each anchor locality, clipped to the metropole's own
    footprint — a buffered hull around its 7 constituent localities, not the
    entire (much larger) Florești Prefecture. A metropole is a compact urban
    agglomeration carved out of the prefecture, not the prefecture itself;
    clipping to the full prefecture would let the more isolated suburbs
    balloon across unrelated parts of it well beyond the actual urban area."""
    labels = list(METRO_STRUCTURE.keys()) + [s["name"] for s in SUBURBS]
    seeds = [(find_locality(info["anchor"])["lon"], find_locality(info["anchor"])["lat"])
             for info in METRO_STRUCTURE.values()]
    seeds += [(find_locality(s["name"])["lon"], find_locality(s["name"])["lat"]) for s in SUBURBS]

    points = np.array(seeds)
    vor = Voronoi(points)
    radius = np.ptp(points, axis=0).max() * 4
    regions, vertices = _voronoi_finite_polygons_2d(vor, radius)

    prefecture_poly = shape(PREFECTURE_BOUNDARY["geometry"]).buffer(0)
    metro_boundary = MultiPoint(seeds).convex_hull.buffer(0.035).intersection(prefecture_poly)

    polygons = {}
    for label, region in zip(labels, regions):
        raw = Polygon(vertices[region]).buffer(0)
        polygons[label] = raw.intersection(metro_boundary)
    return polygons, metro_boundary

SCENARIOS = [
    {"title": "Florești Metropole Administration Reform",
     "options": {"A": ("Keep centralized prefecture control", {"Governance": -5, "Risk": +5}, 10),
                 "B": ("Establish Florești Metropole (mixed decentralization)",
                        {"Governance": +10, "Stability": +5}, 20)},
     "intl": "France's Ministry of the Interior offers a prefecture-partnership model."},
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
    """Real map of Florești Prefecture. Once the metropole is active, each
    municipality/suburb is drawn as its actual merged territory (a clipped
    Voronoi cell around its anchor locality) — not a point or a circle."""
    m = folium.Map(location=[47.90, 28.35], zoom_start=10, tiles=None)
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
             'contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name="Streets",
    ).add_to(m)
    folium.GeoJson(
        PREFECTURE_BOUNDARY,
        name="Florești Prefecture boundary",
        style_function=lambda f: {"color": "#333333", "weight": 2, "dashArray": "6,4", "fillOpacity": 0},
        tooltip="Florești Prefecture boundary",
    ).add_to(m)

    if not st.session_state.metro_active:
        return m

    polygons, metro_boundary = compute_metro_polygons()
    if not metro_boundary.is_empty:
        folium.GeoJson(
            mapping(metro_boundary),
            style_function=lambda f: {"color": "#e91e8c", "weight": 3, "fillOpacity": 0},
            tooltip="Florești Metropole boundary",
        ).add_to(m)
        min_lon, min_lat, max_lon, max_lat = metro_boundary.bounds
        m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

    def label(lat, lon, text, color, size=12, weight=700):
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=(
                f'<div style="font-size:{size}px;font-weight:{weight};color:{color};'
                f'text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff;white-space:nowrap;'
                f'transform:translate(-50%,-50%);">{text}</div>'
            )),
        ).add_to(m)

    for name in METRO_STRUCTURE:
        poly = polygons.get(name)
        if poly is None or poly.is_empty:
            continue
        color = MUNICIPALITY_COLORS[name]
        active = name in st.session_state.inaugurated
        folium.GeoJson(
            mapping(poly),
            style_function=lambda f, color=color, active=active: {
                "color": color, "weight": 2.5,
                "fillColor": color, "fillOpacity": 0.5 if active else 0.15,
            },
            tooltip=f"{name} {'✅ inaugurated' if active else '(not yet inaugurated)'}",
        ).add_to(m)
        c = poly.centroid
        label(c.y, c.x, f"{name}{' ✅' if active else ''}", "#111111" if active else "#555555")

    for suburb in SUBURBS:
        poly = polygons.get(suburb["name"])
        if poly is None or poly.is_empty:
            continue
        folium.GeoJson(
            mapping(poly),
            style_function=lambda f: {"color": "#6b7280", "weight": 1.5, "dashArray": "4,4",
                                       "fillColor": "#9ca3af", "fillOpacity": 0.18},
            tooltip=f"{suburb['name']} — dependent suburb, no local government",
        ).add_to(m)
        c = poly.centroid
        label(c.y, c.x, suburb["name"], "#555555", size=11, weight=500)

    legend_rows = "".join(
        f'<div style="display:flex;align-items:center;gap:6px;margin:2px 0;">'
        f'<span style="width:12px;height:12px;border-radius:3px;background:{MUNICIPALITY_COLORS[n]};'
        f'display:inline-block;opacity:{1 if n in st.session_state.inaugurated else 0.35};"></span>'
        f'<span style="font-size:12px;">{n} {"✅" if n in st.session_state.inaugurated else ""}</span></div>'
        for n in METRO_STRUCTURE
    )
    legend_rows += (
        '<div style="margin-top:4px;font-weight:700;font-size:11px;">Suburbs</div>'
        + "".join(
            f'<div style="display:flex;align-items:center;gap:6px;margin:2px 0;">'
            f'<span style="width:10px;height:10px;border-radius:3px;background:#9ca3af;display:inline-block;"></span>'
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
    st.info("Choose **B) Establish Florești Metropole** in Scenario 1 to activate mixed-decentralization "
            "governance: a metropolitan tier (Istanbul/Budapest-style) carved out of the French-style "
            "Florești Prefecture, over 4 municipalities, each with its own local government and districts.")
else:
    st.caption("Mixed decentralization is in effect — the map below shows each municipality's "
               "real merged territory. Suburbs stay administratively dependent on the metropole.")

st_folium(build_map(), height=520, use_container_width=True, key="metro_map")

if st.session_state.metro_active:
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

# ---------- Real-time clock loop ----------
# While auto-play is on, the app sleeps for one tick then reruns itself,
# firing a random world event each time — this is what keeps the
# simulation moving in real time without any extra polling/JS.
if st.session_state.autoplay:
    time.sleep(tick_interval)
    apply_random_tick()
    st.rerun()
