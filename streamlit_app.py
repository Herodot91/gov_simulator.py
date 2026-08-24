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
from shapely.geometry import shape, mapping, Point

st.set_page_config(page_title="Florești Metropole — CivicTech Simulator", layout="wide")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Governance model: mixed decentralization (Istanbul + Budapest hybrid) — a
# metropolitan tier over 4 municipalities (each with real local government and
# its own sub-districts, like Istanbul's ilçe / Budapest's kerület), plus
# dependent suburbs with no independent government of their own.
METRO_STRUCTURE = {
    "Florești Central": {
        "anchor": "Florești",
        "districts": ["Centrul Civic", "Central Market District",
                      "Răut Riverside District", "Politeh"],
    },
    "Mărculești": {
        "anchor": "Mărculești",
        "districts": ["Airport District", "Aviagorodok",
                      "Industrial District", "Mărculești Residential District"],
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
SUBURBS = [{"name": "Ghindești"}, {"name": "Gura Camencii"}]
MUNICIPALITY_COLORS = {"Florești Central": "#4cc9f0", "Mărculești": "#8338ec",
                        "Vărvăreuca": "#8ab17d", "Lunga": "#e76f51"}
INAUGURATION_COST = 15

# A second, non-interactive governance layer sitting alongside the French
# prefecture model: a Moscow-style detached satellite okrug, after Zelenograd
# (Moscow's own physically separate single-industry administrative okrug).
# Real villages, well outside the metropole's own territory, each sponsored
# as a single-company technopolis rather than folded into ordinary municipal
# structure. Structural world-building, not a scenario -- no cost, no score
# effects to the sim, but each company's product line is browsable.
TECHNOPOLIS_OKRUGS = [
    {
        "name": "Prajila",
        "company": "PHI — Prajila Heavy Industry",
        "sector": "Heavy machinery & construction equipment",
        "note": "An alternative to Hitachi, Caterpillar, Komatsu, and Hyundai's construction arm.",
    },
    {
        "name": "Ciripcău",
        "company": "Sigma Motors",
        "sector": "Hybrid & electric vehicles",
        "note": "Coupé, hatchback, and urban SUV lines built for the domestic and regional market.",
    },
]

# Each Technopolis Okrug's flagship company has a browsable product line --
# real-shaped catalogs (named models, a category, a one-line spec), not
# just the company name.
COMPANY_PRODUCTS = {
    "PHI — Prajila Heavy Industry": [
        {"model": "PHI EX200", "category": "Hydraulic Excavator", "spec": "20-tonne class, 120 kW"},
        {"model": "PHI EX450", "category": "Hydraulic Excavator", "spec": "45-tonne class, 260 kW"},
        {"model": "PHI WL180", "category": "Wheel Loader", "spec": "3.0 m³ bucket, 130 kW"},
        {"model": "PHI D8T", "category": "Crawler Dozer", "spec": "310 kW, semi-U blade"},
        {"model": "PHI MG3000", "category": "Motor Grader", "spec": "3.7 m moldboard, 165 kW"},
        {"model": "PHI CR650", "category": "Crawler Crane", "spec": "65-tonne lift capacity"},
        {"model": "PHI RT100", "category": "Rough-Terrain Crane", "spec": "100-tonne lift capacity"},
        {"model": "PHI HD400", "category": "Rigid Dump Truck", "spec": "40-tonne payload"},
        {"model": "PHI ADT300", "category": "Articulated Dump Truck", "spec": "30-tonne payload, 6x6"},
        {"model": "PHI SK150", "category": "Skid-Steer Loader", "spec": "1,500 kg rated operating capacity"},
    ],
    "Sigma Motors": [
        {"model": "Sigma Vela", "category": "Coupé", "spec": "Electric, 420 km range, 0–100 km/h in 5.4s"},
        {"model": "Sigma Brio", "category": "Hatchback", "spec": "Hybrid, 4.2 L/100km combined"},
        {"model": "Sigma Brio-e", "category": "Hatchback", "spec": "Electric, 340 km range"},
        {"model": "Sigma Terra", "category": "Urban SUV", "spec": "Electric, 460 km range, AWD"},
        {"model": "Sigma Terra Hybrid", "category": "Urban SUV", "spec": "Plug-in hybrid, 65 km EV range"},
    ],
}

# FlorTech — Florești University of Technology: a mass development that
# grows the real Școala Profesională din Florești (kept alongside, as
# vocational institutes) into a full university, with campuses spread
# across the metropole's municipalities, its suburbs, and the two
# Technopolis Okrugs. Structural world-building like the okrugs above --
# browsable, not simulated.
FLORTECH = {
    "name": "FlorTech — Florești University of Technology",
    "origin": (
        "Grown out of the real Școala Profesională din Florești, whose vocational programs "
        "continue alongside the new university rather than being replaced by it."
    ),
    "campuses": [
        {
            "id": "central",
            "name": "FlorTech Central Campus",
            "location": "Florești Central — Politeh District",
            "levels": ["BEng", "BSc", "MEng", "MSc", "PhD", "Postdoc"],
            "faculties": [
                {"name": "Faculty of Electrical, Electronics & Telecommunications",
                 "departments": ["Electrical Engineering", "Electronics & Microelectronics",
                                 "Telecommunications", "Programming & Cybersecurity"]},
                {"name": "Faculty of Civil Engineering, Architecture & Urban Planning",
                 "departments": ["Construction Engineering", "Architecture", "Urban Planning"]},
                {"name": "Faculty of Engineering Economics & Management",
                 "departments": ["Engineering Economics"]},
            ],
        },
        {
            "id": "marculesti",
            "name": "FlorTech Mărculești Campus",
            "location": "Mărculești — Aviagorodok",
            "levels": ["BEng", "BSc", "MEng", "MSc"],
            "faculties": [
                {"name": "Faculty of Transportation & Automation Engineering",
                 "departments": ["Transportation Engineering", "Automation & Computer Engineering"]},
            ],
        },
        {
            "id": "varvareuca",
            "name": "FlorTech Vărvăreuca Campus",
            "location": "Vărvăreuca — Agricultural District",
            "levels": ["BEng", "BSc", "MSc"],
            "faculties": [
                {"name": "Faculty of Natural Sciences & Process Engineering",
                 "departments": ["Applied Natural Sciences in Engineering", "Food Engineering"]},
            ],
        },
        {
            "id": "lunga",
            "name": "FlorTech Lunga Campus",
            "location": "Lunga — Artisan Quarter",
            "levels": ["BEng", "BSc", "MSc"],
            "faculties": [
                {"name": "Faculty of Design",
                 "departments": ["Industrial Design", "Interior Design", "Textile Engineering & Design"]},
            ],
        },
        {
            "id": "prajila",
            "name": "FlorTech Prajila Campus (PHI-sponsored)",
            "location": "Prajila Technopolis Okrug",
            "levels": ["BEng", "MEng", "MSc"],
            "faculties": [
                {"name": "Faculty of Mechanical & Heavy Industry Engineering",
                 "departments": ["Mechanical Engineering", "Industrial Engineering",
                                 "Construction Engineering", "Mining Engineering (incl. Oil & Gas)",
                                 "Robotics & Mechatronics"]},
            ],
        },
        {
            "id": "ciripcau",
            "name": "FlorTech Ciripcău Campus (Sigma Motors-sponsored)",
            "location": "Ciripcău Technopolis Okrug",
            "levels": ["BEng", "MEng", "MSc"],
            "faculties": [
                {"name": "Faculty of Automotive Engineering & Design",
                 "departments": ["Automotive Design", "Electrical Engineering (EV Systems)",
                                 "Robotics & Mechatronics"]},
            ],
        },
    ],
    "vocational_institutes": [
        {"id": "ghindesti", "name": "Școala Profesională — Ghindești Branch", "location": "Ghindești (suburb)",
         "tracks": ["Electrical Technician", "Automotive Mechanic", "Welding & Metalwork", "CNC Machining"]},
        {"id": "guracamencii", "name": "Școala Profesională — Gura Camencii Branch", "location": "Gura Camencii (suburb)",
         "tracks": ["Construction Trades", "HVAC Technician", "Industrial Maintenance"]},
    ],
}

# AgroFlor — Florești University of Agricultural Sciences and Technologies:
# grew out of the Scenario 5 investment in a Vărvăreuca agricultural college
# into a full metropole-wide university, with campuses across all 4
# municipalities and both suburbs (not the Technopolis Okrugs -- those stay
# single-company, not academic). Structural world-building like FlorTech --
# browsable, not simulated. Each campus also lists its research centers/labs
# alongside its faculties/departments.
AGROFLOR = {
    "name": "AgroFlor — Florești University of Agricultural Sciences and Technologies",
    "origin": (
        "Grew out of the investment in a Vărvăreuca agricultural college into a full "
        "metropole-wide university, with campuses across every municipality and both suburbs."
    ),
    "campuses": [
        {
            "id": "varvareuca",
            "name": "AgroFlor Vărvăreuca Campus",
            "location": "Vărvăreuca — Agricultural District",
            "levels": ["BSc", "MSc", "PhD", "Postdoc"],
            "faculties": [
                {"name": "Faculty of Agronomy & Crop Sciences",
                 "departments": ["Agronomy", "Horticulture", "Crop Engineering"]},
                {"name": "Faculty of Genetics & Biotechnology",
                 "departments": ["Genetics & Plant Breeding", "Biotechnology"]},
            ],
            "research_centers": ["Crop Genetics Research Center", "Soil & Water Sustainability Lab"],
        },
        {
            "id": "central",
            "name": "AgroFlor Central Campus",
            "location": "Florești Central — Politeh District",
            "levels": ["BSc", "MSc", "PhD", "Postdoc"],
            "faculties": [
                {"name": "Faculty of Agricultural Economics & Rural Development",
                 "departments": ["Agricultural Economics", "Sustainable Development", "Rural Planning"]},
            ],
            "research_centers": ["Agri-Economics Policy Center"],
        },
        {
            "id": "marculesti",
            "name": "AgroFlor Mărculești Campus",
            "location": "Mărculești — Aviagorodok",
            "levels": ["BEng", "BSc", "MSc"],
            "faculties": [
                {"name": "Faculty of Agricultural Machinery & Agritech",
                 "departments": ["Agricultural Machinery Engineering", "Agritech & Precision Farming"]},
            ],
            "research_centers": ["Agritech & Precision Farming Lab"],
        },
        {
            "id": "lunga",
            "name": "AgroFlor Lunga Campus",
            "location": "Lunga — Artisan Quarter",
            "levels": ["BSc", "MSc", "PhD"],
            "faculties": [
                {"name": "Faculty of Veterinary Medicine & Animal Husbandry",
                 "departments": ["Animal Husbandry", "Veterinary Medicine"]},
            ],
            "research_centers": ["Animal Health Research Lab"],
        },
        {
            "id": "ghindesti",
            "name": "AgroFlor Ghindești Campus",
            "location": "Ghindești (suburb)",
            "levels": ["BSc", "MSc"],
            "faculties": [
                {"name": "Faculty of Food Engineering & Natural Sciences",
                 "departments": ["Food Engineering", "Biology", "Chemistry"]},
            ],
            "research_centers": ["Food Quality & Safety Lab"],
        },
        {
            "id": "guracamencii",
            "name": "AgroFlor Gura Camencii Campus",
            "location": "Gura Camencii (suburb)",
            "levels": ["BSc", "MSc"],
            "faculties": [
                {"name": "Faculty of Applied Sciences",
                 "departments": ["Physics", "Informatics & Applied Mathematics in Agriculture"]},
            ],
            "research_centers": ["Agri-Informatics Lab"],
        },
    ],
}


@st.cache_data
def load_geo_data():
    with open(os.path.join(DATA_DIR, "floresti_localities.json"), encoding="utf-8") as f:
        localities = json.load(f)
    # Real OSM boundary of "Raionul Florești" (the Moldovan raion) — reused
    # here as the outer footprint for the fictional French-style "Florești
    # Prefecture" this simulation models instead of the raion system.
    with open(os.path.join(DATA_DIR, "floresti_district.geojson"), encoding="utf-8") as f:
        boundary = json.load(f)
    # Real OSM administrative boundaries (admin_level=8, "current territory")
    # for the 4 municipalities, plus their pre-merged union as one feature
    # named "Florești Metropole" — built once from the actual OSM relations,
    # not approximated at runtime.
    with open(os.path.join(DATA_DIR, "floresti_municipalities.geojson"), encoding="utf-8") as f:
        municipalities = json.load(f)
    return localities, boundary, municipalities


@st.cache_data
def load_cbd_masterplan_svg():
    with open(os.path.join(DATA_DIR, "cbd_masterplan.svg"), encoding="utf-8") as f:
        return f.read()


LOCALITIES, PREFECTURE_BOUNDARY, MUNICIPALITY_GEOJSON = load_geo_data()


def find_locality(name):
    """Look up a locality by name, preferring the 'town' entry when a village shares the name."""
    matches = [loc for loc in LOCALITIES if loc["name"] == name]
    towns = [loc for loc in matches if loc["type"] == "town"]
    return (towns or matches)[0]


@st.cache_data
def compute_metro_polygons():
    """The real current territory of each municipality, and their union as
    the overall Florești Metropole outline — both loaded from actual OSM
    administrative boundaries (admin_level=8), not approximated. Merging
    Florești + Mărculești + Vărvăreuca + Lunga is exactly this union; nothing
    else (no suburbs, no synthetic buffer) is added to keep the map's extent
    to just those 4 real territories."""
    polygons = {f["properties"]["name"]: shape(f["geometry"]).buffer(0)
                for f in MUNICIPALITY_GEOJSON["features"]}
    metro_boundary = polygons.pop("Florești Metropole")
    return polygons, metro_boundary

SCENARIOS = [
    {"title": "Florești Metropole Administration Reform",
     "options": {"A": ("Keep centralized prefecture control", {"Governance": -5, "Risk": +5}, 10),
                 "B": ("Establish Florești Metropole (mixed decentralization)",
                        {"Governance": +10, "Stability": +5}, 20)},
     "intl": "France's Ministry of the Interior offers a prefecture-partnership model."},
    {"title": "Technical University Investment in Florești",
     "options": {"A": ("Skip investment", {"Economy": -5}, 0),
                 "B": ("IT faculty only", {"Economy": +5}, 15),
                 "C": ("Full technical university", {"Economy": +10, "Governance": +5}, 25)},
     "intl": "Local employers and the EU push to expand Școala Profesională into a full "
             "technical university — the seed of what will grow into FlorTech."},
    {"title": "Digital Justice & Procurement Reform",
     "options": {"A": ("Delay reform", {"Governance": -5}, 0),
                 "B": ("Implement transparency tools", {"Governance": +10, "Risk": -5}, 15)},
     "intl": "EU praises Moldova's rule of law improvement."},
    {"title": "Budget Allocation: Green Tech Factories",
     "options": {"A": ("One per region", {"Economy": +5}, 20),
                 "B": ("Ignore sector", {"Economy": -5}, 0)},
     "intl": "UN welcomes clean tech expansion."},
    {"title": "Education: New Agricultural College in Vărvăreuca",
     "options": {"A": ("Build it, EU model", {"Economy": +5, "Stability": +5}, 25),
                 "B": ("Keep colleges as-is", {"Economy": -5}, 0)},
     "intl": "Foreign students show interest in Vărvăreuca's Agricultural District."},
]

# Layer-scoped development projects — same interactive shape as SCENARIOS
# (options with Cost + score effects), but each project lives at exactly one
# governance layer and only unlocks once that layer is active: metropole
# projects once the metropole is established, municipal/district projects
# once their municipality is inaugurated (districts don't inaugurate
# separately, they ride on their municipality's status).
METRO_PROJECTS = [
    {"id": "ring_road", "title": "Florești Ring Road",
     "options": {"A": ("Build the full ring road", {"Economy": +10, "Stability": +5}, 30),
                 "B": ("Partial bypass only", {"Economy": +5}, 15)},
     "intl": "The EU regional development fund shows interest in cross-border logistics."},
    {"id": "metro_line1", "title": "Metro Line 1",
     "options": {"A": ("Build the light-rail line", {"Economy": +8, "Governance": +5, "Stability": +5}, 35),
                 "B": ("Feasibility study only", {"Governance": +3}, 10)},
     "intl": "Investors eye Florești as a regional transit hub."},
    {"id": "rail_airport_link", "title": "Railway Station – Airport Link",
     "options": {"A": ("Build a direct rail link to Mărculești Airport", {"Economy": +10, "Risk": -3}, 25),
                 "B": ("Shuttle bus service only", {"Economy": +3}, 8)},
     "intl": "Aeroportul Internațional Mărculești pushes for better ground transit."},
]

MUNICIPALITY_PROJECTS = {
    "Florești Central": [
        {"id": "raut_plaza", "title": "Răut Plaza",
         "options": {"A": ("Full plaza redevelopment", {"Stability": +5, "Economy": +5}, 20),
                     "B": ("Basic renovation", {"Stability": +2}, 10)},
         "intl": "Residents petition for a new riverside public space."},
    ],
    "Vărvăreuca": [
        {"id": "new_avenue", "title": "New Avenue",
         "options": {"A": ("Build a new avenue toward Florești", {"Economy": +7, "Stability": +3}, 22),
                     "B": ("Minor road upgrade", {"Economy": +3}, 10)},
         "intl": "Vărvăreuca residents demand better connectivity."},
    ],
}

DISTRICT_PROJECTS = {
    ("Lunga", "Green Belt District"): [
        {"id": "community_park", "title": "Community Park",
         "options": {"A": ("Build the park", {"Stability": +5, "Governance": +2}, 12)},
         "intl": "Environmental groups praise the green-space initiative."},
    ],
    ("Lunga", "Lunga Residential District"): [
        {"id": "school_reconstruction", "title": "School Reconstruction",
         "options": {"A": ("Full reconstruction", {"Governance": +5, "Stability": +3, "Economy": +2}, 18),
                     "B": ("Partial repairs", {"Stability": +1}, 8)},
         "intl": "The Ministry of Education monitors rural school conditions."},
    ],
}

# Real-world reference points used to place resolved projects on the map --
# same coordinates as each municipality's real anchor locality (see
# floresti_localities.json), plus the real Mărculești airport's approximate
# centroid, since the app doesn't otherwise load the airport as its own
# feature (it's merged into Mărculești's territory).
_FLORESTI_PT = (47.8938318, 28.2996474)
_MARCULESTI_PT = (47.8693441, 28.2415422)
_VARVAREUCA_PT = (47.8798617, 28.3113869)
_LUNGA_PT = (47.8617078, 28.231765)
_MARCULESTI_AIRPORT_PT = (47.8597, 28.2130)

# How each resolved project is drawn on the map: a single "point" marker, or
# a "line" between two reference points for corridor-shaped infrastructure.
PROJECT_MAP_LOCATIONS = {
    "ring_road": {"type": "point", "coord": (47.9095, 28.3105)},
    "metro_line1": {"type": "point", "coord": _FLORESTI_PT},
    "rail_airport_link": {"type": "line", "points": [_FLORESTI_PT, _MARCULESTI_AIRPORT_PT]},
    "raut_plaza": {"type": "point", "coord": (47.8918, 28.2946)},
    "new_avenue": {"type": "line", "points": [_VARVAREUCA_PT, _FLORESTI_PT]},
    "community_park": {"type": "point", "coord": (_LUNGA_PT[0] + 0.0035, _LUNGA_PT[1] - 0.003)},
    "school_reconstruction": {"type": "point", "coord": (_LUNGA_PT[0] - 0.0035, _LUNGA_PT[1] + 0.003)},
}

# Where each FlorTech campus marker sits -- offset a little from its
# municipality's/okrug's own anchor point so it doesn't sit exactly on top
# of that label. Prajila/Ciripcău use their real village coordinates
# (see floresti_localities.json) since they have no separate anchor const.
_PRAJILA_PT = (47.84049, 28.2100662)
_CIRIPCAU_PT = (47.9835655, 28.3808055)
FLORTECH_CAMPUS_LOCATIONS = {
    "central": (_FLORESTI_PT[0] + 0.0035, _FLORESTI_PT[1] - 0.0035),
    "marculesti": (_MARCULESTI_PT[0] - 0.0035, _MARCULESTI_PT[1] - 0.0035),
    "varvareuca": (_VARVAREUCA_PT[0] + 0.0035, _VARVAREUCA_PT[1] - 0.0035),
    "lunga": (_LUNGA_PT[0], _LUNGA_PT[1] + 0.006),
    "prajila": (_PRAJILA_PT[0] + 0.003, _PRAJILA_PT[1] + 0.003),
    "ciripcau": (_CIRIPCAU_PT[0] + 0.003, _CIRIPCAU_PT[1] + 0.003),
}

# AgroFlor campuses use their own offsets (opposite side from FlorTech's, at
# each shared municipality) so the two universities' markers don't stack.
# Ghindești/Gura Camencii use their real suburb coordinates (see
# floresti_localities.json).
_GHINDESTI_PT = (47.8623849, 28.3870348)
_GURACAMENCII_PT = (47.8901159, 28.3553067)
AGROFLOR_CAMPUS_LOCATIONS = {
    "varvareuca": (_VARVAREUCA_PT[0] - 0.0045, _VARVAREUCA_PT[1] + 0.0045),
    "central": (_FLORESTI_PT[0] - 0.0045, _FLORESTI_PT[1] + 0.0045),
    "marculesti": (_MARCULESTI_PT[0] + 0.0045, _MARCULESTI_PT[1] + 0.0045),
    "lunga": (_LUNGA_PT[0], _LUNGA_PT[1] - 0.006),
    "ghindesti": (_GHINDESTI_PT[0] + 0.003, _GHINDESTI_PT[1] - 0.003),
    "guracamencii": (_GURACAMENCII_PT[0] + 0.003, _GURACAMENCII_PT[1] - 0.003),
}

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
    st.session_state.selected_municipality = None
    st.session_state.selected_district = None
    st.session_state.resolved_projects = {}
    st.session_state.selected_campus = None
    st.session_state.selected_agro_campus = None


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


def resolve_project(project, key, scope_label):
    """Resolve a metropole/municipal/district development project — same
    Cost + effects shape as resolve_choice, but keyed by project id so each
    one can be resolved independently of the others, from wherever in the
    Metropole -> Municipality -> District drill-down it's shown."""
    st.session_state.sim_month += 1
    if key is None:
        st.session_state.resolved_projects[project["id"]] = {"choice": None, "label": "Skipped"}
        record(f"Month {st.session_state.sim_month}: Skipped — {project['title']} ({scope_label}).")
        return
    desc, effects, cost = project["options"][key]
    if st.session_state.budget < cost:
        record(f"Month {st.session_state.sim_month}: Not enough budget for {key}) {desc} "
               f"on '{project['title']}'. Skipped.")
        return
    st.session_state.budget -= cost
    apply_effects(effects)
    st.session_state.last_intl = project["intl"]
    st.session_state.resolved_projects[project["id"]] = {"choice": key, "label": desc}
    record(f"Month {st.session_state.sim_month}: {project['title']} ({scope_label}) → {key}) {desc} "
           f"| Cost {cost} | Intl: {project['intl']} | Scores {st.session_state.scores} "
           f"| Budget {st.session_state.budget}")


def apply_random_tick():
    st.session_state.sim_month += 1
    title, effects, blurb = random.choice(RANDOM_EVENTS)
    apply_effects(effects)
    st.session_state.last_intl = blurb
    record(f"Month {st.session_state.sim_month}: 🌍 {title} — {blurb} | Scores {st.session_state.scores}")


def _zoom_for_bounds(bounds, width_px, height_px, padding=0.2):
    """Compute a static Leaflet zoom level that fits `bounds` in a
    width_px x height_px viewport. Baked in at map-construction time instead
    of relying on client-side fitBounds(), which (inside the nested Streamlit
    component iframe) can run before Leaflet has measured the container and
    silently no-op, leaving the map stuck at its initial zoom."""
    min_lon, min_lat, max_lon, max_lat = bounds
    dlon = (max_lon - min_lon) * padding
    dlat = (max_lat - min_lat) * padding
    min_lon, max_lon = min_lon - dlon, max_lon + dlon
    min_lat, max_lat = min_lat - dlat, max_lat + dlat

    def merc_y(lat):
        rad = math.radians(max(min(lat, 89.9), -89.9))
        return math.log(math.tan(math.pi / 4 + rad / 2))

    world_px = 256
    lon_diff = max(max_lon - min_lon, 1e-9)
    zoom_lon = math.log2(width_px * 360 / (lon_diff * world_px))
    lat_diff = max(abs(merc_y(max_lat) - merc_y(min_lat)), 1e-9)
    zoom_lat = math.log2(height_px * (2 * math.pi) / (lat_diff * world_px))
    return max(3, min(18, int(math.floor(min(zoom_lon, zoom_lat)))))


def build_map():
    """Real map of Florești Prefecture. Once the metropole is active, each
    municipality is drawn as its actual current territory (real OSM
    administrative boundary) — not a point or a circle — and the view is
    fit tightly to their merged extent, not the whole prefecture."""
    polygons, metro_boundary = (None, None)
    if st.session_state.metro_active:
        polygons, metro_boundary = compute_metro_polygons()

    if metro_boundary is not None and not metro_boundary.is_empty:
        min_lon, min_lat, max_lon, max_lat = metro_boundary.bounds
        # The Technopolis Okrugs sit outside the metropole's own territory
        # (that's the point of the Zelenograd model) -- widen the fitted
        # view to include them too, same as a real Moscow map that has to
        # zoom out to show Zelenograd alongside the city proper.
        for okrug in TECHNOPOLIS_OKRUGS:
            loc = find_locality(okrug["name"])
            min_lon, max_lon = min(min_lon, loc["lon"]), max(max_lon, loc["lon"])
            min_lat, max_lat = min(min_lat, loc["lat"]), max(max_lat, loc["lat"])
        center = [(min_lat + max_lat) / 2, (min_lon + max_lon) / 2]
        zoom = _zoom_for_bounds((min_lon, min_lat, max_lon, max_lat), 600, 500)
    else:
        center = [47.90, 28.35]
        zoom = 10

    m = folium.Map(location=center, zoom_start=zoom, tiles=None)
    folium.TileLayer(
        # no_labels: the labeled variant prints the base map's own real-world
        # place names (e.g. the real town of Mărculești) whichever territory
        # they geographically sit in now, which visually reads as if that
        # name were part of a *different* municipality's colored area than it
        # actually is. Our own DivIcon labels below are the only place names
        # that should appear, each guaranteed to sit inside its own polygon.
        tiles="https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png",
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

    if not metro_boundary.is_empty:
        folium.GeoJson(
            mapping(metro_boundary),
            style_function=lambda f: {"color": "#e91e8c", "weight": 3, "fillOpacity": 0},
            tooltip="Florești Metropole boundary",
        ).add_to(m)

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
                "color": color, "weight": 3,
                "fillColor": color, "fillOpacity": 0.6 if active else 0.4,
            },
            tooltip=f"{name} {'✅ inaugurated' if active else '(not yet inaugurated)'}",
        ).add_to(m)
        # Anchor the label at the real named locality (its actual OSM town/
        # village point) whenever that point actually falls inside this
        # municipality's territory -- otherwise a generic representative_point()
        # can land far from where the real place sits (e.g. deep in a large
        # rural comuna), reading as if the label were misplaced relative to
        # real maps. representative_point() (unlike centroid, which can land
        # outside a concave shape) is the fallback, and covers every part for
        # a MultiPolygon (e.g. a village plus a detached facility).
        real_pt = None
        try:
            loc = find_locality(METRO_STRUCTURE[name]["anchor"])
            candidate = Point(loc["lon"], loc["lat"])
            if poly.contains(candidate):
                real_pt = candidate
        except (IndexError, KeyError):
            pass
        if real_pt is not None:
            label(real_pt.y, real_pt.x, f"{name}{' ✅' if active else ''}", "#111111" if active else "#333333")
        else:
            parts = poly.geoms if poly.geom_type == "MultiPolygon" else [poly]
            for part in parts:
                c = part.representative_point()
                label(c.y, c.x, f"{name}{' ✅' if active else ''}", "#111111" if active else "#333333")

    # Technopolis Okrugs — shown as their own small marked territory, same
    # spirit as how a real Moscow map marks Zelenograd: a real point outside
    # the main urban mass, given a distinct look (gold, dashed) so it doesn't
    # read as a 5th ordinary municipality.
    for okrug in TECHNOPOLIS_OKRUGS:
        loc = find_locality(okrug["name"])
        folium.Circle(
            location=[loc["lat"], loc["lon"]],
            radius=900,
            color="#b8860b", weight=2, dash_array="5,5",
            fill=True, fill_color="#e3b23c", fill_opacity=0.35,
            tooltip=f"{loc['display_name']} — Technopolis Okrug (Zelenograd model) — {okrug['company']}",
        ).add_to(m)
        label(loc["lat"], loc["lon"],
              f"🏭 {loc['display_name']}<br><span style='font-weight:400;font-size:10px;'>{okrug['company']}</span>",
              "#7a5c00", size=11)

    # FlorTech campuses -- point markers, not territory (a campus isn't its
    # own governance unit). Clicking one drills into its faculties, same as
    # clicking a municipality's shape drills into its districts. Icon gets
    # an explicit size/anchor (a round badge, no CSS transform) so the
    # actual clickable hit-box lines up with the visible glyph -- without
    # icon_size, DivIcon falls back to Leaflet's 12x12 default box while the
    # transform paints the emoji outside it, so it looks clickable but isn't.
    campus_icon_html = (
        '<div style="width:28px;height:28px;border-radius:50%;background:#1d3557;'
        'display:flex;align-items:center;justify-content:center;font-size:15px;'
        'box-shadow:0 1px 4px rgba(0,0,0,.45);border:2px solid #fff;">🎓</div>'
    )
    for campus in FLORTECH["campuses"]:
        lat, lon = FLORTECH_CAMPUS_LOCATIONS[campus["id"]]
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=campus_icon_html, icon_size=(28, 28), icon_anchor=(14, 14)),
            tooltip=f"🎓 {campus['name']} — FlorTech campus",
        ).add_to(m)

    # AgroFlor campuses -- same shape as FlorTech's markers above, a
    # distinct green badge so the two universities read apart on the map.
    agro_icon_html = (
        '<div style="width:28px;height:28px;border-radius:50%;background:#2a7f43;'
        'display:flex;align-items:center;justify-content:center;font-size:15px;'
        'box-shadow:0 1px 4px rgba(0,0,0,.45);border:2px solid #fff;">🌾</div>'
    )
    for campus in AGROFLOR["campuses"]:
        lat, lon = AGROFLOR_CAMPUS_LOCATIONS[campus["id"]]
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=agro_icon_html, icon_size=(28, 28), icon_anchor=(14, 14)),
            tooltip=f"🌾 {campus['name']} — AgroFlor campus",
        ).add_to(m)

    # Resolved projects (any layer) get a marker/line on the map — only ones
    # actually decided on (not skipped), so the map reflects real choices.
    all_projects = (
        [(p, "Metropolitan") for p in METRO_PROJECTS]
        + [(p, f"{muni} municipal") for muni, plist in MUNICIPALITY_PROJECTS.items() for p in plist]
        + [(p, f"{dist} district") for (muni, dist), plist in DISTRICT_PROJECTS.items() for p in plist]
    )
    for project, scope_label in all_projects:
        resolved = st.session_state.resolved_projects.get(project["id"])
        if not resolved or resolved["choice"] is None:
            continue
        loc = PROJECT_MAP_LOCATIONS.get(project["id"])
        if loc is None:
            continue
        tooltip_text = f"🏗️ {project['title']} ({scope_label}) — {resolved['choice']}) {resolved['label']}"
        icon_html = ('<div style="font-size:20px;line-height:1;'
                     'transform:translate(-50%,-100%);filter:drop-shadow(0 1px 2px rgba(0,0,0,.5));">🏗️</div>')
        if loc["type"] == "point":
            folium.Marker(location=list(loc["coord"]), icon=folium.DivIcon(html=icon_html),
                          tooltip=tooltip_text).add_to(m)
        elif loc["type"] == "line":
            pts = loc["points"]
            folium.PolyLine(locations=[list(p) for p in pts], color="#5a3921", weight=4,
                            opacity=0.85, dash_array="8,6", tooltip=tooltip_text).add_to(m)
            mid = [(pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2]
            folium.Marker(location=mid, icon=folium.DivIcon(html=icon_html), tooltip=tooltip_text).add_to(m)

    legend_rows = "".join(
        f'<div style="display:flex;align-items:center;gap:6px;margin:2px 0;">'
        f'<span style="width:12px;height:12px;border-radius:3px;background:{MUNICIPALITY_COLORS[n]};'
        f'display:inline-block;opacity:{1 if n in st.session_state.inaugurated else 0.35};"></span>'
        f'<span style="font-size:12px;">{n} {"✅" if n in st.session_state.inaugurated else ""}</span></div>'
        for n in METRO_STRUCTURE
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


def render_project(project, scope_label, key_prefix):
    """One project's UI at whichever governance layer it's shown: its
    options as buttons (mirrors the top-level SCENARIOS buttons) before
    it's resolved, or the outcome once it is."""
    resolved = st.session_state.resolved_projects.get(project["id"])
    st.markdown(f"**{project['title']}**")
    if resolved:
        if resolved["choice"] is None:
            st.caption("⏭️ Skipped")
        else:
            st.success(f"{resolved['choice']}) {resolved['label']}")
    else:
        opt_items = list(project["options"].items())
        cols = st.columns(len(opt_items) + 1)
        for col, (key, (desc, effects, cost)) in zip(cols, opt_items):
            with col:
                if st.button(f"{key}) {desc} | Cost {cost} | {fmt_effects(effects)}",
                             key=f"{key_prefix}_{project['id']}_{key}",
                             disabled=st.session_state.budget < cost,
                             use_container_width=True):
                    resolve_project(project, key, scope_label)
                    st.rerun()
        with cols[-1]:
            if st.button("Skip", key=f"{key_prefix}_{project['id']}_skip", use_container_width=True):
                resolve_project(project, None, scope_label)
                st.rerun()


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
    st.caption("Mixed decentralization is in effect — click a municipality on the map (or below) to "
               "drill down into its districts. Suburbs stay administratively dependent on the metropole.")

map_key = "metro_map_active" if st.session_state.metro_active else "metro_map_inactive"
map_state = st_folium(build_map(), height=520, use_container_width=True, key=map_key)

# Clicking a municipality's shape on the map drills down into it, same as
# clicking its name below — folium reports the click via the tooltip text we
# already set on each polygon ("<name> ✅ inaugurated" / "<name> (not yet...)").
if st.session_state.metro_active and map_state and map_state.get("last_object_clicked_tooltip"):
    clicked_tooltip = map_state["last_object_clicked_tooltip"]
    for muni_name in METRO_STRUCTURE:
        if clicked_tooltip.startswith(muni_name) and st.session_state.selected_municipality != muni_name:
            st.session_state.selected_municipality = muni_name
            st.session_state.selected_district = None
            st.rerun()
    # Clicking a FlorTech campus marker on the map drills into it, same as
    # clicking its button below -- the marker's tooltip carries the campus
    # name, same pattern as municipality clicks above.
    for campus in FLORTECH["campuses"]:
        campus_tooltip_prefix = f"🎓 {campus['name']}"
        if clicked_tooltip.startswith(campus_tooltip_prefix) and st.session_state.selected_campus != campus["id"]:
            st.session_state.selected_campus = campus["id"]
            st.rerun()
    # Same for AgroFlor campus markers.
    for campus in AGROFLOR["campuses"]:
        agro_tooltip_prefix = f"🌾 {campus['name']}"
        if clicked_tooltip.startswith(agro_tooltip_prefix) and st.session_state.selected_agro_campus != campus["id"]:
            st.session_state.selected_agro_campus = campus["id"]
            st.rerun()

if st.session_state.metro_active:
    sel_muni = st.session_state.selected_municipality
    sel_dist = st.session_state.selected_district

    if sel_muni is None:
        # ---------- Layer 1: Metropole -> pick a municipality ----------
        st.caption("👆 Click a municipality to see its 4 districts.")
        muni_cols = st.columns(4)
        for col, name in zip(muni_cols, METRO_STRUCTURE):
            active = name in st.session_state.inaugurated
            with col:
                if st.button(f"{name} {'✅' if active else ''}", key=f"select_{name}", use_container_width=True):
                    st.session_state.selected_municipality = name
                    st.session_state.selected_district = None
                    st.rerun()

        with st.expander(f"🏘️ Suburbs ({len(SUBURBS)}) — dependent on the metropole, no local government"):
            for suburb in SUBURBS:
                loc = find_locality(suburb["name"])
                st.markdown(f"- **{loc['display_name']}** ({loc['type']})")

        with st.expander(f"🏭 Technopolis Okrugs ({len(TECHNOPOLIS_OKRUGS)}) — Zelenograd model"):
            st.caption(
                "Alongside the French-style prefecture, the metropole borrows a second model from "
                "Moscow: a detached, single-industry administrative okrug, after Zelenograd — Moscow's "
                "own physically separate microelectronics okrug. These two villages sit outside the "
                "metropole's own territory but are administratively sponsored by it, each built around "
                "one flagship company rather than ordinary municipal government."
            )
            for okrug in TECHNOPOLIS_OKRUGS:
                loc = find_locality(okrug["name"])
                st.markdown(
                    f"**{loc['display_name']}** ({loc['type']}) — {okrug['company']}  \n"
                    f"*{okrug['sector']}.* {okrug['note']}"
                )
                products = COMPANY_PRODUCTS.get(okrug["company"], [])
                with st.expander(f"🔧 {okrug['company']} — product line ({len(products)})"):
                    for p in products:
                        st.markdown(f"- **{p['model']}** — {p['category']} · {p['spec']}")

        st.markdown("#### 🏗️ Metropolitan Projects")
        for project in METRO_PROJECTS:
            render_project(project, "Metropolitan", "metro_project")

    else:
        info = METRO_STRUCTURE[sel_muni]
        active = sel_muni in st.session_state.inaugurated
        anchor = find_locality(info["anchor"])

        if sel_dist is None:
            # ---------- Layer 2: Municipality -> pick a district ----------
            if st.button("← Back to Metropole", key="back_to_metro"):
                st.session_state.selected_municipality = None
                st.rerun()
            st.markdown(f"### {sel_muni} {'✅ inaugurated' if active else ''}")
            st.caption(f"Anchor: {anchor['display_name']}")

            st.write("👆 Click a district for details:")
            dist_cols = st.columns(4)
            for col, d in zip(dist_cols, info["districts"]):
                with col:
                    if st.button(d, key=f"select_district_{sel_muni}_{d}", use_container_width=True):
                        st.session_state.selected_district = d
                        st.rerun()

            if active:
                st.success("Inaugurated")
            else:
                if st.button(f"Inaugurate ({INAUGURATION_COST})", key=f"inaugurate_{sel_muni}",
                              disabled=st.session_state.budget < INAUGURATION_COST):
                    inaugurate_municipality(sel_muni)
                    st.rerun()

            muni_projects = MUNICIPALITY_PROJECTS.get(sel_muni, [])
            if muni_projects:
                st.markdown("#### 🏗️ Municipal Projects")
                if active:
                    for project in muni_projects:
                        render_project(project, f"{sel_muni} municipal", "muni_project")
                else:
                    st.caption(f"Inaugurate {sel_muni} to unlock its municipal projects.")

            if sel_muni == "Florești Central":
                with st.expander("📐 View CBD Masterplan — concept site plan for Răut Plaza's district"):
                    st.caption(
                        "A mixed-use business district proposed for the riverside land between Centrul "
                        "Civic and the Răut, built around the Metro Line 1 station and Răut Plaza as its "
                        "civic anchor. Concept only — not an adopted plan."
                    )
                    st.markdown(load_cbd_masterplan_svg(), unsafe_allow_html=True)
        else:
            # ---------- Layer 3: District detail ----------
            if st.button(f"← Back to {sel_muni}", key="back_to_muni"):
                st.session_state.selected_district = None
                st.rerun()
            st.markdown(f"### {sel_dist}")
            st.caption(f"District of **{sel_muni}**, Florești Metropole.")
            if active:
                st.info("This district shares in its municipality's local government, "
                        "inaugurated as part of the mixed-decentralization reform.")
            else:
                st.warning(f"{sel_muni} hasn't been inaugurated yet — inaugurate it to activate "
                           "local government here, including this district.")
                if st.button(f"Inaugurate {sel_muni} ({INAUGURATION_COST})", key=f"inaugurate_from_district_{sel_muni}",
                              disabled=st.session_state.budget < INAUGURATION_COST):
                    inaugurate_municipality(sel_muni)
                    st.rerun()

            dist_projects = DISTRICT_PROJECTS.get((sel_muni, sel_dist), [])
            if dist_projects:
                st.markdown("#### 🏗️ District Projects")
                if active:
                    for project in dist_projects:
                        render_project(project, f"{sel_dist} district", "district_project")
                else:
                    st.caption(f"Inaugurate {sel_muni} to unlock projects in this district.")

# ---------- FlorTech University ----------
st.subheader("🎓 FlorTech — Florești University of Technology")
if not st.session_state.metro_active:
    st.info("FlorTech's campuses come online once the metropole is established "
            "(Scenario 1, option B).")
else:
    st.caption(FLORTECH["origin"])
    sel_campus_id = st.session_state.selected_campus

    if sel_campus_id is None:
        st.write("👆 Click a campus for its faculties, departments, and programs:")
        campus_cols = st.columns(3)
        for i, campus in enumerate(FLORTECH["campuses"]):
            with campus_cols[i % 3]:
                if st.button(campus["name"], key=f"select_campus_{campus['id']}", use_container_width=True):
                    st.session_state.selected_campus = campus["id"]
                    st.rerun()

        with st.expander(
            f"🛠️ Vocational Institutes ({len(FLORTECH['vocational_institutes'])}) — "
            "Școala Profesională legacy tracks, kept alongside FlorTech"
        ):
            for inst in FLORTECH["vocational_institutes"]:
                st.markdown(f"**{inst['name']}** — {inst['location']}  \n{', '.join(inst['tracks'])}")
    else:
        campus = next(c for c in FLORTECH["campuses"] if c["id"] == sel_campus_id)
        if st.button("← Back to FlorTech", key="back_to_flortech"):
            st.session_state.selected_campus = None
            st.rerun()
        st.markdown(f"### {campus['name']}")
        st.caption(f"{campus['location']} · Degree levels: {', '.join(campus['levels'])}")
        for fac in campus["faculties"]:
            st.markdown(f"#### {fac['name']}")
            for dept in fac["departments"]:
                st.markdown(f"- **{dept}** — {', '.join(campus['levels'])}")

# ---------- AgroFlor University ----------
st.subheader("🌾 AgroFlor — Florești University of Agricultural Sciences and Technologies")
if not st.session_state.metro_active:
    st.info("AgroFlor's campuses come online once the metropole is established "
            "(Scenario 1, option B).")
else:
    st.caption(AGROFLOR["origin"])
    sel_agro_id = st.session_state.selected_agro_campus

    if sel_agro_id is None:
        st.write("👆 Click a campus for its faculties, departments, research centers, and programs:")
        agro_cols = st.columns(3)
        for i, campus in enumerate(AGROFLOR["campuses"]):
            with agro_cols[i % 3]:
                if st.button(campus["name"], key=f"select_agro_campus_{campus['id']}", use_container_width=True):
                    st.session_state.selected_agro_campus = campus["id"]
                    st.rerun()
    else:
        campus = next(c for c in AGROFLOR["campuses"] if c["id"] == sel_agro_id)
        if st.button("← Back to AgroFlor", key="back_to_agroflor"):
            st.session_state.selected_agro_campus = None
            st.rerun()
        st.markdown(f"### {campus['name']}")
        st.caption(f"{campus['location']} · Degree levels: {', '.join(campus['levels'])}")
        for fac in campus["faculties"]:
            st.markdown(f"#### {fac['name']}")
            for dept in fac["departments"]:
                st.markdown(f"- **{dept}** — {', '.join(campus['levels'])}")
        st.markdown("#### 🔬 Research Centers & Labs")
        for center in campus["research_centers"]:
            st.markdown(f"- {center}")

# ---------- Real-time clock loop ----------
# While auto-play is on, the app sleeps for one tick then reruns itself,
# firing a random world event each time — this is what keeps the
# simulation moving in real time without any extra polling/JS.
if st.session_state.autoplay:
    time.sleep(tick_interval)
    apply_random_tick()
    st.rerun()
