# app.py (real-time)
import os
import re
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
from shapely.geometry import shape, mapping, Point, box

st.set_page_config(page_title="North East Simulator", layout="wide")

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
SUBURBS = [{"name": "Ghindești"}, {"name": "Gura Camencii"}, {"name": "Gura Căinarului"}]
MUNICIPALITY_COLORS = {"Florești Central": "#4cc9f0", "Mărculești": "#8338ec",
                        "Vărvăreuca": "#8ab17d", "Lunga": "#e76f51"}
INAUGURATION_COST = 15

# The app is built for real local-government users at each tier -- the
# metropolitan council, the prefecture, each municipal council, each
# district office -- to explore policy and project decisions the way
# their own administration is actually organized: into directorates
# (state/metro tier) and departments (municipal/district tier). Purely
# descriptive world-building, same non-interactive shape as the
# Technopolis Okrugs/FlorTech/AgroFlor/transit network -- no cost, no
# score effects.
PREFECTURE_DIRECTORATES = [
    {"name": "Directorate of Public Order & Civil Protection",
     "mandate": "Policing coordination, emergency services, civil protection planning."},
    {"name": "Directorate of State Finance & Treasury Oversight",
     "mandate": "State budget transfers, treasury oversight, fiscal compliance."},
    {"name": "Directorate of Public Administration & Legal Affairs",
     "mandate": "Legal oversight of local acts, administrative litigation, the prefect's own staff."},
    {"name": "Directorate of Civil Registry & Documents",
     "mandate": "Civil status records, identity documents, notarial oversight."},
]
METRO_COUNCIL_DIRECTORATES = [
    {"name": "Directorate of Urban Planning & Territorial Development",
     "mandate": "Metropolitan masterplans (incl. the Florești Central CBD), zoning coordination across municipalities."},
    {"name": "Directorate of Transport & Infrastructure",
     "mandate": "Trams, BRT, and commuter rail network planning; roads spanning more than one municipality."},
    {"name": "Directorate of Economic Development & Investment",
     "mandate": "Investment promotion, the Technopolis Okrugs relationship, business permitting."},
    {"name": "Directorate of Environment & Sustainability",
     "mandate": "Green tech policy, waste management, environmental compliance."},
    {"name": "Directorate of Education & Culture",
     "mandate": "FlorTech and AgroFlor liaison, schools, cultural programming."},
    {"name": "Directorate of Health & Social Assistance",
     "mandate": "Public health coordination, social services across municipalities."},
]
# Each municipality's own two generic departments (finance, public
# services) plus one thematic department tied to its established identity.
MUNICIPALITY_DEPARTMENTS = {
    "Florești Central": [
        {"name": "Department of Urban Development & CBD Management",
         "mandate": "Central Business District oversight, Răut Plaza and civic-core development."},
        {"name": "Department of Municipal Finance", "mandate": "Local budget, taxation, procurement."},
        {"name": "Department of Public Services", "mandate": "Waste collection, water/sewer, municipal maintenance."},
    ],
    "Mărculești": [
        {"name": "Department of Transport & Airport Liaison",
         "mandate": "Coordination with Mărculești International Airport, ground transit."},
        {"name": "Department of Municipal Finance", "mandate": "Local budget, taxation, procurement."},
        {"name": "Department of Public Services", "mandate": "Waste collection, water/sewer, municipal maintenance."},
    ],
    "Vărvăreuca": [
        {"name": "Department of Agriculture & Rural Development",
         "mandate": "Farmland management, AgroFlor liaison, rural infrastructure."},
        {"name": "Department of Municipal Finance", "mandate": "Local budget, taxation, procurement."},
        {"name": "Department of Public Services", "mandate": "Waste collection, water/sewer, municipal maintenance."},
    ],
    "Lunga": [
        {"name": "Department of Local Economy & Crafts",
         "mandate": "Artisan Quarter support, local markets, small-business permitting."},
        {"name": "Department of Municipal Finance", "mandate": "Local budget, taxation, procurement."},
        {"name": "Department of Public Services", "mandate": "Waste collection, water/sewer, municipal maintenance."},
    ],
}


def district_office(municipality, district):
    """Districts sit below the municipal tier -- one lightweight civic
    office each, rather than a full directorate roster of their own."""
    return {
        "name": f"{district} Civic Office",
        "mandate": f"First-line public services liaison to the {municipality} Municipal Council — "
                   "local permits, records, and citizen requests.",
    }

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

# Each Technopolis Okrug gets its own real interactive policy, same
# Cost + effects shape as Town Policies -- keyed by the okrug's own
# "name", same convention as FACTORIES/SCHOOLS below.
TECHNOPOLIS_POLICIES = {
    "Prajila": [
        {"id": "prajila_expansion", "title": "Prajila Heavy Industry — Production Line Expansion",
         "options": {
             "A": ["Expand PHI's heavy machinery production line", {"Economy": +6, "Governance": +2}, 18],
             "B": ["Maintain current production capacity", {}, 0],
         },
         "intl": "PHI's export contracts draw regional investor interest."},
    ],
    "Ciripcău": [
        {"id": "ciripcau_expansion", "title": "Sigma Motors — EV Production Line Expansion",
         "options": {
             "A": ["Expand Sigma Motors' EV production line", {"Economy": +6, "Governance": +2}, 18],
             "B": ["Maintain current production capacity", {}, 0],
         },
         "intl": "Sigma Motors' EV lineup draws EU green-tech attention."},
    ],
}

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


# ---------- Rabnirez Metropole (Rîbnița + Rezina) ----------
# A second fictional metropole, alongside Florești, in the same "North East
# Simulator" -- real geography (Overpass API-sourced OSM points: Rîbnița,
# Rezina, their real named quarters, and the real Rezina-Rîbnița bridge)
# under the same governance scheme as Florești: a French-style Prefecture
# (here uniting Rîbnița raion and Rezina raion into one, "Rabnirez") with a
# Metropole carved out inside it using the same Istanbul-ilçe/Budapest-
# kerület mixed decentralization. A speculative cross-Nistru thought
# experiment, explicitly not a real position on Transnistria's status.
@st.cache_data
def load_rabnirez_localities():
    with open(os.path.join(DATA_DIR, "rabnirez_localities.json"), encoding="utf-8") as f:
        return json.load(f)


RABNIREZ_LOCALITIES = load_rabnirez_localities()


def find_rabnirez_locality(name):
    matches = [loc for loc in RABNIREZ_LOCALITIES if loc["name"] == name]
    return matches[0]


RABNIREZ_METRO_STRUCTURE = {
    "Rîbnița": {
        "anchor": "Rîbnița",
        "districts": ["Centru (Rîbnița)", "Pușkina (Rîbnița)", "Sahkamen (Rîbnița)", "Verșigora (Rîbnița)"],
    },
    "Rezina": {
        "anchor": "Rezina",
        "districts": ["Centru (Rezina)", "Rezina Vale", "Cartierul Pietrarilor", "Cartierul Văii Nistrului"],
    },
}
RABNIREZ_SUBURBS = [{"name": "Iubileinîi (Rîbnița)"}, {"name": "Valcenko (Rîbnița)"}]

# Both towns' real cement industry, and Rîbnița's real steel/metallurgical
# plant -- fictionalized company names on real real-world facts, same
# "real geography, fictional institutions" pattern as Florești's own
# factories (e.g. PHI, Sigma Motors). Structural world-building for now
# (map markers only) -- a full Industry tab for Rabnirez is a later stage.
RABNIREZ_FACTORIES = {
    "Rîbnița": [
        {"name": "Nistru Metalurgic", "sector": "Steel & Metallurgy",
         "products": ["Steel billets", "Rebar", "Rolled steel sheet"]},
        {"name": "Rîbnița Ciment Nord", "sector": "Cement & Building Materials",
         "products": ["Portland cement", "Construction aggregates"]},
    ],
    "Rezina": [
        {"name": "Rezina CimentGrup", "sector": "Cement & Building Materials",
         "products": ["Portland cement", "Ready-mix concrete", "Limestone aggregate"]},
    ],
}


@st.cache_data
def load_rabnirez_geo_data():
    with open(os.path.join(DATA_DIR, "rabnirez_district.geojson"), encoding="utf-8") as f:
        boundary = json.load(f)
    with open(os.path.join(DATA_DIR, "rabnirez_municipalities.geojson"), encoding="utf-8") as f:
        municipalities = json.load(f)
    return boundary, municipalities


RABNIREZ_BOUNDARY, RABNIREZ_MUNICIPALITY_GEOJSON = load_rabnirez_geo_data()


def compute_rabnirez_metro_polygons():
    """Same approach as compute_metro_polygons(): real current territory of
    Rîbnița and Rezina (both admin_level=8 OSM boundaries), and their union
    as the Rabnirez Metropole outline -- both merged once via shapely from
    real Nominatim-sourced boundaries, not approximated at runtime."""
    polygons = {f["properties"]["name"]: shape(f["geometry"]).buffer(0)
                for f in RABNIREZ_MUNICIPALITY_GEOJSON["features"]}
    metro_boundary = polygons.pop("Rabnirez Metropole")
    return polygons, metro_boundary


def compute_rabnirez_district_polygons(muni_name, muni_polygon):
    """Same 2x2 quadrant-split approximation compute_district_polygons()
    uses for Florești -- Rabnirez's districts aren't real cadastral units
    either."""
    minx, miny, maxx, maxy = muni_polygon.bounds
    midx, midy = (minx + maxx) / 2, (miny + maxy) / 2
    quadrants = [box(minx, midy, midx, maxy), box(midx, midy, maxx, maxy),
                 box(minx, miny, midx, midy), box(midx, miny, maxx, midy)]
    result = {}
    for name, quad in zip(RABNIREZ_METRO_STRUCTURE[muni_name]["districts"], quadrants):
        clipped = muni_polygon.intersection(quad)
        if clipped.is_empty:
            continue
        if clipped.geom_type == "MultiPolygon":
            clipped = max(clipped.geoms, key=lambda g: g.area)
        result[name] = clipped
    return result


def build_rabnirez_map():
    """Real map of Rabnirez Prefecture -- merged Rîbnița+Rezina raion
    boundary (dashed outline), the merged Rabnirez Metropole territory
    (highlighted outline), and each municipality drawn as its actual real
    OSM territory, clickable the same way Florești's map works. Roads,
    transit, and other layers are later stages -- this is Prefecture +
    Metropole + Municipality/District only."""
    polygons, metro_boundary = compute_rabnirez_metro_polygons()
    min_lon, min_lat, max_lon, max_lat = metro_boundary.bounds
    center = [(min_lat + max_lat) / 2, (min_lon + max_lon) / 2]
    zoom = _zoom_for_bounds((min_lon, min_lat, max_lon, max_lat), 600, 500)

    m = folium.Map(location=center, zoom_start=zoom, tiles=None)
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
             'contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name="Streets",
    ).add_to(m)
    folium.GeoJson(
        RABNIREZ_BOUNDARY,
        name="Rabnirez Prefecture boundary",
        style_function=lambda f: {"color": "#333333", "weight": 2, "dashArray": "6,4", "fillOpacity": 0},
        tooltip="Rabnirez Prefecture boundary (Rîbnița raion + Rezina raion, merged)",
    ).add_to(m)
    folium.GeoJson(
        mapping(metro_boundary),
        style_function=lambda f: {"color": "#e91e8c", "weight": 3, "fillOpacity": 0},
        tooltip="Rabnirez Metropole boundary",
    ).add_to(m)

    def rr_label(lat, lon, text, color, size=12, weight=700):
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=(
                f'<div style="font-size:{size}px;font-weight:{weight};color:{color};'
                f'text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff;white-space:nowrap;'
                f'transform:translate(-50%,-50%);">{text}</div>'
            )),
            tooltip=re.sub("<[^>]+>", " ", text).strip(),
        ).add_to(m)

    rr_colors = {"Rîbnița": "#8338ec", "Rezina": "#3a86ff"}
    for name in RABNIREZ_METRO_STRUCTURE:
        poly = polygons.get(name)
        if poly is None or poly.is_empty:
            continue
        color = rr_colors[name]
        folium.GeoJson(
            mapping(poly),
            style_function=lambda f, color=color: {
                "color": color, "weight": 3, "fillColor": color, "fillOpacity": 0.45,
            },
            tooltip=name,
        ).add_to(m)
        real_pt = find_rabnirez_locality(name)
        rr_label(real_pt["lat"], real_pt["lon"], name, "#111111")

        sel_muni = st.session_state.rr_selected_municipality
        if sel_muni == name:
            rr_dist_colors = ["#e63946", "#2a9d8f", "#e9c46a", "#457b9d"]
            for i, (dname, dpoly) in enumerate(compute_rabnirez_district_polygons(name, poly).items()):
                dcolor = rr_dist_colors[i % len(rr_dist_colors)]
                folium.GeoJson(
                    mapping(dpoly),
                    style_function=lambda f, dcolor=dcolor: {
                        "color": dcolor, "weight": 2, "fillColor": dcolor, "fillOpacity": 0.5,
                    },
                    tooltip=dname,
                ).add_to(m)
                c = dpoly.representative_point()
                rr_label(c.y, c.x, dname, dcolor, size=10, weight=600)

    bridge = find_rabnirez_locality("Rezina-Rîbnița Bridge")
    folium.Marker(
        location=[bridge["lat"], bridge["lon"]],
        icon=folium.DivIcon(html=(
            '<div style="font-size:20px;line-height:1;transform:translate(-50%,-100%);'
            'filter:drop-shadow(0 1px 2px rgba(0,0,0,.5));">🌉</div>'
        )),
        tooltip="Podul Rezina-Rîbnița — the real bridge across the Nistru connecting both municipalities",
    ).add_to(m)

    for muni_name, factories in RABNIREZ_FACTORIES.items():
        anchor = find_rabnirez_locality(muni_name)
        for i, factory in enumerate(factories):
            folium.Marker(
                location=[anchor["lat"] + 0.006 + i * 0.004, anchor["lon"] + 0.006],
                icon=folium.DivIcon(html=(
                    '<div style="font-size:18px;line-height:1;transform:translate(-50%,-100%);'
                    'filter:drop-shadow(0 1px 2px rgba(0,0,0,.5));">🏭</div>'
                )),
                tooltip=f"{factory['name']} — {factory['sector']} ({muni_name})",
            ).add_to(m)

    return m


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


def compute_district_polygons(muni_name, muni_polygon):
    """Approximate district sub-boundaries by splitting the municipality's
    real territory into a 2x2 grid (NW/NE/SW/SE quadrants) and assigning
    its 4 named districts to them in list order. Florești's districts
    aren't real cadastral units (invented for this sim, like the districts
    themselves), so this is a legible approximation, not a survey -- same
    "concept, not an adopted plan" spirit as the CBD masterplan."""
    minx, miny, maxx, maxy = muni_polygon.bounds
    midx, midy = (minx + maxx) / 2, (miny + maxy) / 2
    quadrants = [box(minx, midy, midx, maxy), box(midx, midy, maxx, maxy),
                 box(minx, miny, midx, midy), box(midx, miny, maxx, midy)]
    result = {}
    for name, quad in zip(METRO_STRUCTURE[muni_name]["districts"], quadrants):
        clipped = muni_polygon.intersection(quad)
        if clipped.is_empty:
            continue
        if clipped.geom_type == "MultiPolygon":
            # Keep district geometry as a single Polygon -- a MultiPolygon
            # feature here trips a bug in streamlit-folium's click-tracking
            # JS (getTooltip().getContent() throws on some multi-part
            # features), which silently breaks click detection for the
            # *whole* map, not just this layer. The largest piece is a fine
            # approximation anyway, same spirit as the quadrant split itself.
            clipped = max(clipped.geoms, key=lambda g: g.area)
        result[name] = clipped
    return result

SCENARIOS = [
    {"id": "metro_reform", "title": "Florești Metropole Administration Reform",
     "options": {"A": ("Keep centralized prefecture control", {"Governance": -5, "Risk": +5}, 10),
                 "B": ("Establish Florești Metropole (mixed decentralization)",
                        {"Governance": +10, "Stability": +5}, 20)},
     "intl": "France's Ministry of the Interior offers a prefecture-partnership model."},
    {"id": "flortech_investment", "title": "Technical University Investment in Florești",
     "options": {"A": ("Skip investment", {"Economy": -5}, 0),
                 "B": ("IT faculty only", {"Economy": +5}, 15),
                 "C": ("Full technical university", {"Economy": +10, "Governance": +5}, 25)},
     "intl": "Local employers and the EU push to expand Școala Profesională into a full "
             "technical university — the seed of what will grow into FlorTech."},
    {"id": "digital_justice", "title": "Digital Justice & Procurement Reform",
     "options": {"A": ("Delay reform", {"Governance": -5}, 0),
                 "B": ("Implement transparency tools", {"Governance": +10, "Risk": -5}, 15)},
     "intl": "EU praises Moldova's rule of law improvement."},
    {"id": "green_tech", "title": "Budget Allocation: Green Tech Factories",
     "options": {"A": ("One per region", {"Economy": +5}, 20),
                 "B": ("Ignore sector", {"Economy": -5}, 0)},
     "intl": "UN welcomes clean tech expansion."},
    {"id": "agroflor_investment", "title": "Education: New Agricultural College in Vărvăreuca",
     "options": {"A": ("Build it, EU model", {"Economy": +5, "Stability": +5}, 25),
                 "B": ("Keep colleges as-is", {"Economy": -5}, 0)},
     "intl": "Foreign students show interest in Vărvăreuca's Agricultural District."},
]

# The prefecture is a real decision-making authority too, not just a
# directorates list -- its own policies, in effect regardless of whether
# the metropole has been established (same interactive shape as the
# METRO/MUNICIPALITY/DISTRICT_PROJECTS below).
PREFECTURE_POLICIES = [
    {"id": "property_tax_reform", "title": "Property Tax Reform",
     "options": {"A": ("Progressive property tax", {"Governance": +5, "Economy": +3}, 10),
                 "B": ("Flat-rate property tax", {"Economy": +5, "Stability": -2}, 5)},
     "intl": "Ratepayers' associations watch the prefecture's tax-policy choice closely."},
    {"id": "egovernment", "title": "State Digital Services Modernization",
     "options": {"A": ("Full e-government rollout", {"Governance": +8}, 20),
                 "B": ("Partial digitization", {"Governance": +3}, 8)},
     "intl": "The Civil Registry directorate's paper backlog draws EU digitalization interest."},
    {"id": "civil_protection", "title": "Civil Protection Budget",
     "options": {"A": ("Expand civil protection & emergency services", {"Risk": -5, "Stability": +3}, 15),
                 "B": ("Maintain current staffing levels", {}, 0)},
     "intl": "Regional emergency-response reviews recommend investment."},
    {"id": "florlink_fleet", "title": "FlorLink Fleet Expansion",
     "options": {"A": ("Add more coach/bus slots at Autogara Metropolitană", {"Economy": +4, "Stability": +2}, 14),
                 "B": ("Keep the current schedule", {}, 0)},
     "intl": "Commuters from Cunicea and Răduleni push for more frequent FlorLink service."},
]

# Two real villages, both outside the metropole and the Technopolis Okrugs,
# whose territory has grown into a small town within the prefecture --
# each with its own town council and interactive policies, structurally
# alongside the metropole (with its Technopolis Okrugs and suburbs) as a
# third kind of settlement the prefecture governs. Coordinates looked up
# from STOP_COORDS at render time (defined further down), same lazy
# pattern TECHNOPOLIS_OKRUGS uses with find_locality().
PREFECTURE_TOWNS = [
    {"id": "cunicea", "name": "Cunicea", "radius": 1400,
     "note": "A real village east of the metropole, its territory significantly expanded into a "
             "small town within the prefecture, with its own town council. Not mono-industrial, "
             "unlike the Technopolis Okrugs -- several factories across different sectors.",
     "council": [
         {"name": "Department of Local Administration", "mandate": "Town council staff, civil records, local permits."},
         {"name": "Department of Public Finance", "mandate": "Local budget, taxation, procurement."},
     ]},
    {"id": "raduleni", "name": "Răduleni", "radius": 1400,
     "note": "A real village north of the metropole, its territory significantly expanded into a "
             "small town within the prefecture, with its own town council. Not mono-industrial, "
             "unlike the Technopolis Okrugs -- several factories across different sectors.",
     "council": [
         {"name": "Department of Local Administration", "mandate": "Town council staff, civil records, local permits."},
         {"name": "Department of Public Finance", "mandate": "Local budget, taxation, procurement."},
     ]},
]
TOWN_POLICIES = {
    "cunicea": [
        {"id": "cunicea_infra", "title": "Cunicea Town Infrastructure Investment",
         "options": {"A": ("Upgrade water & road infrastructure", {"Economy": +4, "Stability": +2}, 12),
                     "B": ("Minor repairs only", {"Economy": +1}, 4)},
         "intl": "Cunicea's town council petitions the prefecture for infrastructure funding."},
    ],
    "raduleni": [
        {"id": "raduleni_infra", "title": "Răduleni Town Infrastructure Investment",
         "options": {"A": ("Upgrade water & road infrastructure", {"Economy": +4, "Stability": +2}, 12),
                     "B": ("Minor repairs only", {"Economy": +1}, 4)},
         "intl": "Răduleni's town council petitions the prefecture for infrastructure funding."},
    ],
}

# Factories across the metropole, the suburbs, and the Prefecture Towns --
# structural world-building, browsable via the Industries & Schools
# Dashboard below (click a location to see its factories, their products,
# and their sector). Florești and Cunicea both also host precision-
# materials/electronics factories; Cunicea and Răduleni each supply
# components to one of the Technopolis Okrugs' own flagship companies,
# making them genuinely multi-industry, not mono-industrial like the
# Okrugs themselves.
FACTORIES = {
    "Florești Central": [
        {"name": "ProMilk", "sector": "Dairy & Food Processing",
         "products": ["Pasteurized milk", "Yogurt", "Butter", "Cheese"]},
        {"name": "FlorPan", "sector": "Bakery & Food Processing",
         "products": ["Bread", "Pastries", "Packaged baked goods"]},
        {"name": "Alfa-Nistru Group", "sector": "Food Processing",
         "products": ["Packaged foods", "Confectionery", "Preserves"]},
        {"name": "Florești Precision Components", "sector": "Precision Materials & Electronics",
         "products": ["Precision-machined parts", "Circuit assemblies", "Sensor housings"]},
        {"name": "Florești HPP (HydroTechnique Ltd.)", "sector": "Hydroelectric Power",
         "products": ["Electricity generation", "Grid supply to Florești Central", "Răut river flow regulation"]},
    ],
    "Cunicea": [
        {"name": "Cunicea AutoParts", "sector": "Automotive Components (Sigma Motors supplier)",
         "products": ["EV battery housings", "Chassis components", "Interior trim assemblies"]},
        {"name": "Cunicea Precision Electronics", "sector": "Precision Materials & Electronics",
         "products": ["Printed circuit boards", "Sensor modules", "Wiring harnesses"]},
    ],
    "Răduleni": [
        {"name": "Răduleni Heavy Components", "sector": "Industrial Components (PHI supplier)",
         "products": ["Hydraulic cylinders", "Gearbox housings", "Structural steel weldments"]},
    ],
    "Gura Căinarului": [
        {"name": "Gura Căinarului Beverage Works", "sector": "Beverages",
         "products": ["Bottled water", "Soft drinks", "Fruit juices"]},
    ],
    "Gura Camencii": [
        {"name": "Gura Camencii Bread Factory", "sector": "Bakery",
         "products": ["Bread", "Bread rolls", "Crackers"]},
    ],
    "Ghindești": [
        {"name": "Ghindești Beer Factory", "sector": "Brewing",
         "products": ["Lager", "Craft ale", "Non-alcoholic beer"]},
        {"name": "Ghindești Zahăr S.A.", "sector": "Sugar Processing",
         "products": ["Refined sugar", "Sugar beet pulp (animal feed)", "Molasses"]},
    ],
}

# Schools across the metropole and the Prefecture Towns -- "current"
# (locally-rooted) schools per municipality/town, plus a handful of
# fictional international schools spread one per location across the whole
# metropole (not all stacked in Florești Central) reflecting its cosmopolitan,
# industrial/tech-hub character. Giorgetto Giugiaro (the real automotive
# designer's namesake) sits at Ciripcău deliberately, next to Sigma Motors.
SCHOOLS = {
    "Florești Central": [
        "Liceul Teoretic Ștefan cel Mare",
        "Școala Profesională din Florești",
        "Fuad Seniora School",
    ],
    "Mărculești": ["Liceul Teoretic Mărculești", "Tokugawa International Japanese School"],
    "Vărvăreuca": ["Liceul Agricol Vărvăreuca", "Liceo Español Don Quijote"],
    "Lunga": ["Școala de Arte și Meserii Lunga", "Liceo Classico Italiano Giuseppe Verdi"],
    "Ghindești": ["Școala Profesională — Ghindești Branch", "Abdi İpekçi Türk Lisesi"],
    "Gura Camencii": ["Școala Profesională — Gura Camencii Branch"],
    "Gura Căinarului": ["Școala Profesională — Gura Căinarului Branch"],
    "Cunicea": ["Liceul Teoretic Cunicea"],
    "Răduleni": ["Liceul Teoretic Răduleni"],
    "Ciripcău": ["Liceo Tecnico Giorgetto Giugiaro"],
}

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

# Public transit network -- structural world-building like the Technopolis
# Okrugs/FlorTech/AgroFlor above: no cost, no score effects, always shown
# on the map once the metropole is active. The metro system runs on trams,
# not heavy rail, and stays inside the 4 municipalities -- unlike the BRT
# and commuter lines, it doesn't reach the suburbs. A BRT corridor
# (biogas/electric buses) covers what trams don't; two commuter rail lines
# reach past the metropole's own territory to Gura Căinarului and to the
# Prajila Technopolis Okrug.
_GURA_CAINARULUI_PT = (47.8627915, 28.1831829)
# Real villages, both outside the metropole and the Technopolis Okrugs,
# whose territory has grown into a small town within the prefecture -- see
# PREFECTURE_TOWNS below. "Răduleni" uses the real Rădulenii Noi locality's
# own coordinates (preferred over Rădulenii Vechi).
_CUNICEA_PT = (47.9139733, 28.6456445)
_RADULENI_PT = (47.9567436, 28.247045)
# Tram T1's own points: a stop on Florești Central's own northern boundary,
# and the Coach Terminal on Vărvăreuca's Heritage Quarter boundary (also
# where the Metropolitan Ring Road passes -- see ROAD_NETWORK below). T1
# runs strictly between these two municipal boundaries, not into either
# municipality's own core.
_FLORESTI_NORTH_PT = (47.8998, 28.2996)
_COACH_TERMINAL_PT = (47.8700, 28.3235)
# Centrul Civic's own point -- reused below as CIVIC_DISTRICT_PT for the
# 🏛️ map marker, and here as a Tram T1 stop.
_CENTRUL_CIVIC_PT = (_FLORESTI_PT[0] + 0.003, _FLORESTI_PT[1] - 0.003)
STOP_COORDS = {
    "Ghindești": _GHINDESTI_PT,
    "Florești Central": _FLORESTI_PT,
    "Florești Central North": _FLORESTI_NORTH_PT,
    "Centrul Civic": _CENTRUL_CIVIC_PT,
    "Vărvăreuca": _VARVAREUCA_PT,
    "Lunga": _LUNGA_PT,
    "Mărculești": _MARCULESTI_PT,
    "Mărculești Airport": _MARCULESTI_AIRPORT_PT,
    "Gura Camencii": _GURACAMENCII_PT,
    "Gura Căinarului": _GURA_CAINARULUI_PT,
    "Prajila": _PRAJILA_PT,
    "Ciripcău": _CIRIPCAU_PT,
    "Coach Terminal": _COACH_TERMINAL_PT,
    "Cunicea": _CUNICEA_PT,
    "Răduleni": _RADULENI_PT,
}
# The real street/avenue each stop sits on -- proposed, not surveyed (same
# "concept, not an adopted plan" spirit as the CBD masterplan), but grounded
# in each stop's own already-established district/theming.
STOP_STREETS = {
    "Ghindești": "Strada Nucilor",
    "Florești Central": "Gara Florești, Bulevardul Unirii",
    "Florești Central North": "Strada Ștefan cel Mare",
    "Centrul Civic": "Piața Prefecturii",
    "Vărvăreuca": "Strada Recoltei, Agricultural District",
    "Lunga": "Strada Meșterilor, Artisan Quarter",
    "Mărculești": "Șoseaua Aviatorilor, Aviagorodok",
    "Mărculești Airport": "Aleea Aeroportului",
    "Gura Camencii": "Drumul Camencii",
    "Gura Căinarului": "Drumul Căinarului",
    "Prajila": "Strada Uzinei PHI",
    "Ciripcău": "Technopolis Expressway, Sigma Motors Okrug",
    "Coach Terminal": "Autogara Metropolitană, Heritage Quarter boundary",
    "South Lunga Bypass": "Drumul de Centură Sud",
    "Vărvăreuca Forestry Bypass": "Drumul Ocolitor, Forestry District boundary",
    "Cunicea": "Gara Cunicea, Regional Expressway",
    "Răduleni": "Gara Răduleni, Regional Expressway",
}
# Rail runs as two tiers -- the metro system (Metro, heavier/longer-haul,
# a couple of stations each) and trams (Tram, short/local) -- alongside
# road transit in three tiers of its own: BRT (limited-stop, commuter-
# equivalent reach), plain biogas/electric bus (local, no dedicated lane),
# and regional rail out to the prefecture's own small towns (see
# PREFECTURE_TOWNS below). BRT/bus/tram lines run denser stop spacing than
# metro. Gara Florești (the "Florești Central" stop) is the hub where
# every mode meets -- both metro lines, the tram, all 3 BRT lines, the
# bus, and both regional rail lines.
TRANSIT_LINES = [
    {"id": "metro_m1", "name": "Metro M1", "mode": "metro", "color": "#1a237e",
     "stops": ["Vărvăreuca", "Florești Central", "Lunga", "Mărculești"]},
    {"id": "metro_m2", "name": "Metro M2", "mode": "metro", "color": "#283593",
     "stops": ["Coach Terminal", "Florești Central", "Florești Central North"]},
    {"id": "tram_t1", "name": "Tram T1", "mode": "tram", "color": "#8e44ad",
     "stops": ["Florești Central", "Centrul Civic"]},
    {"id": "brt1", "name": "BRT 1 (biogas/electric)", "mode": "brt", "color": "#16a085",
     "stops": ["Gura Camencii", "Florești Central", "Mărculești Airport", "Ciripcău"]},
    {"id": "brt2", "name": "BRT 2 (biogas/electric)", "mode": "brt", "color": "#2980b9",
     "stops": ["Ghindești", "Florești Central", "Lunga", "Mărculești Airport", "Gura Căinarului"]},
    {"id": "brt3", "name": "BRT 3 (biogas/electric)", "mode": "brt", "color": "#27ae60",
     "stops": ["Gura Camencii", "Florești Central", "Lunga", "Prajila"]},
    {"id": "bus_b1", "name": "Bus B1 (biogas/electric)", "mode": "bus", "color": "#7f8c8d",
     "stops": ["Florești Central", "Ghindești", "Gura Camencii"]},
    {"id": "regional_r1", "name": "Regional Rail R1", "mode": "regional_rail", "color": "#7b3f00",
     "stops": ["Florești Central", "Cunicea"]},
    {"id": "regional_r2", "name": "Regional Rail R2", "mode": "regional_rail", "color": "#5c4033",
     "stops": ["Florești Central", "Răduleni"]},
]
# Line styling by mode: metro solid+thick, trams solid+thinner, BRT dashed
# (a bus corridor, not rail), plain buses finely dotted, regional rail
# dash-dotted.
TRANSIT_MODE_STYLE = {
    "metro": {"weight": 6, "dash_array": None},
    "tram": {"weight": 4, "dash_array": None},
    "brt": {"weight": 4, "dash_array": "10,6"},
    "bus": {"weight": 3, "dash_array": "2,4"},
    "regional_rail": {"weight": 4, "dash_array": "2,6"},
}
TRANSIT_MODE_LABELS = {
    "metro": "🚇 Metro", "tram": "🚋 Tram", "brt": "🚌 BRT",
    "bus": "🚍 Bus", "regional_rail": "🚆 Regional Rail",
}

# Two operators, one per governance tier that actually runs transit --
# mirrors the app's own two-tier transit planning (Metropolitan Council
# Directorate of Transport & Infrastructure vs. the Prefecture): MetroFlor
# runs everything that stays within the metropole itself, FlorLink connects
# Florești to the Prefecture Towns and beyond.
TRANSIT_OPERATORS = [
    {"id": "metroflor", "name": "MetroFlor", "level": "Metropolitan",
     "note": "The Metropolitan Council's own transit operator -- every mode that stays within the "
             "metropole itself: the metro, the tram, the BRT lines, and the biogas/electric bus "
             "network. BRT 3 reaches Prajila and BRT 1 reaches Ciripcău, so MetroFlor covers both "
             "Technopolis Okrugs too, not just the 4 municipalities.",
     "line_ids": ["metro_m1", "metro_m2", "tram_t1", "brt1", "brt2", "brt3", "bus_b1"]},
    {"id": "florlink", "name": "FlorLink", "level": "Prefecture",
     "note": "The Prefecture's own operator, connecting Florești to Cunicea and Răduleni by regional "
             "rail and running the Autogara Metropolitană's (Coach Terminal) intercity coach services -- "
             "reaching beyond the metropole's own network, the way MetroFlor doesn't. Cunicea and "
             "Răduleni each run their own local public transport (electric buses, trams, or "
             "trolleybuses) beyond that FlorLink connection -- neither MetroFlor nor FlorLink operate "
             "inside the towns themselves.",
     "line_ids": ["regional_r1", "regional_r2"]},
]


def transit_interchanges():
    """Stops served by 2+ transit lines -- where trams interchange with
    each other, the BRT line, and the commuter lines."""
    by_stop = {}
    for line in TRANSIT_LINES:
        for stop in line["stops"]:
            by_stop.setdefault(stop, []).append(line["name"])
    return {stop: lines for stop, lines in by_stop.items() if len(lines) >= 2}


def transit_route_label(line):
    """'A (street) → B (street) → C (street)' -- the named-street route
    description, not just the bare stop list."""
    return " → ".join(f"{s} ({STOP_STREETS.get(s, s)})" for s in line["stops"])


# Two major roads, shown on the map as committed infrastructure (not a
# METRO_PROJECTS decision to resolve) -- the Metropolitan Ring Road stays
# outside the municipalities' own built territory, tracing the metro's
# southern periphery close to Vărvăreuca's Heritage Quarter and Forestry
# District (its own two southernmost districts) rather than cutting through
# the metropole itself, on its way from Ghindești to Gura Căinarului. The
# Technopolis Expressway links the two Technopolis Okrugs via the airport.
_SOUTH_LUNGA_BYPASS_PT = (47.8480, 28.2450)
_VARVAREUCA_FORESTRY_BYPASS_PT = (47.8630, 28.3010)
ROAD_NETWORK = [
    {"id": "ring_road_metro", "name": "Metropolitan Ring Road", "kind": "ring_road",
     "color": "#6c757d",
     "route": [
         ("Ghindești", _GHINDESTI_PT),
         ("Coach Terminal", _COACH_TERMINAL_PT),
         ("Vărvăreuca Forestry Bypass", _VARVAREUCA_FORESTRY_BYPASS_PT),
         ("South Lunga Bypass", _SOUTH_LUNGA_BYPASS_PT),
         ("Mărculești Airport", _MARCULESTI_AIRPORT_PT),
         ("Gura Căinarului", _GURA_CAINARULUI_PT),
     ]},
    {"id": "technopolis_expressway", "name": "Technopolis Expressway", "kind": "expressway",
     "color": "#d97706",
     "route": [
         ("Prajila", _PRAJILA_PT),
         ("Mărculești Airport", _MARCULESTI_AIRPORT_PT),
         ("Ciripcău", _CIRIPCAU_PT),
     ]},
    {"id": "regional_expressway", "name": "Regional Expressway (Cunicea–Răduleni)", "kind": "expressway",
     "color": "#b45309",
     "route": [
         ("Cunicea", _CUNICEA_PT),
         ("Răduleni", _RADULENI_PT),
         ("Ghindești", _GHINDESTI_PT),
     ]},
]
ROAD_KIND_STYLE = {
    "ring_road": {"weight": 5, "dash_array": None},
    "expressway": {"weight": 5, "dash_array": "1,6"},
}

# The Civic District -- Centrul Civic (the "Civic Center"), the first of
# Florești Central's 4 districts (see METRO_STRUCTURE and
# compute_district_polygons' NW/NE/SW/SE quadrant order) -- is where the
# Metropolitan Council, the Florești Prefecture, and their directorates are
# headquartered. Positioned inside that district's own NW quadrant rather
# than at the municipality's plain center, so it reads as sitting inside
# Centrul Civic once that quadrant is drawn. Structural world-building,
# ties the Directorates section to an actual place on the map.
CIVIC_DISTRICT_PT = _CENTRUL_CIVIC_PT

# The CBD masterplan's own footprint (see load_cbd_masterplan_svg() and the
# expander in Florești Central's municipal view) -- shown on the map itself
# as a zone, not just linked from an expander. The riverside land between
# Centrul Civic and the Răut, around the Metro Line 1 station and Răut Plaza.
CBD_ZONE_BOUNDS = (47.8893, 28.2918, 47.8935, 28.2965)  # (min_lat, min_lon, max_lat, max_lon)

# Florești's own hydroelectric power plant, on the Răut river just downstream
# of the CBD riverside land, managed by HydroTechnique Ltd. -- structural
# world-building, same "not a simulation choice" status as the Coach
# Terminal/Airport signs above.
_HPP_PT = (47.8862, 28.2938)


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
    st.session_state.rr_selected_municipality = None
    st.session_state.rr_selected_district = None
    st.session_state.resolved_projects = {}
    st.session_state.resolved_scenarios = {}
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
        st.session_state.resolved_scenarios[scenario["id"]] = {"choice": None, "label": "Skipped"}
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
    st.session_state.resolved_scenarios[scenario["id"]] = {"choice": key, "label": desc}
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
        # The commuter rail lines reach past the okrugs too (Gura Căinarului,
        # west of Prajila) -- widen further to keep the whole transit network
        # in view.
        for lat, lon in STOP_COORDS.values():
            min_lon, max_lon = min(min_lon, lon), max(max_lon, lon)
            min_lat, max_lat = min(min_lat, lat), max(max_lat, lat)
        # The ring road dips south of Lunga, past the built-up stops above.
        for road in ROAD_NETWORK:
            for _, (lat, lon) in road["route"]:
                min_lon, max_lon = min(min_lon, lon), max(max_lon, lon)
                min_lat, max_lat = min(min_lat, lat), max(max_lat, lat)
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
        # Every marker on the map needs a bound tooltip -- one without any
        # (as these decorative labels had) trips a streamlit-folium
        # click-tracking bug (getTooltip().getContent() throws on a layer
        # with no tooltip), which silently breaks click detection for the
        # *whole* map, not just this layer.
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=(
                f'<div style="font-size:{size}px;font-weight:{weight};color:{color};'
                f'text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff;white-space:nowrap;'
                f'transform:translate(-50%,-50%);">{text}</div>'
            )),
            tooltip=re.sub("<[^>]+>", " ", text).strip(),
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

    # Once a municipality is selected, split its territory into its 4
    # districts (approximate quadrants -- see compute_district_polygons)
    # so zooming into a municipality shows its own sub-structure, not just
    # a flat color fill. Clicking a district's region drills into it, same
    # as clicking a municipality's shape drills into its districts.
    sel_muni = st.session_state.get("selected_municipality")
    if sel_muni and polygons.get(sel_muni) is not None and not polygons[sel_muni].is_empty:
        dist_colors = ["#e63946", "#2a9d8f", "#e9c46a", "#457b9d"]
        for i, (dname, dpoly) in enumerate(compute_district_polygons(sel_muni, polygons[sel_muni]).items()):
            dcolor = dist_colors[i % len(dist_colors)]
            folium.GeoJson(
                mapping(dpoly),
                style_function=lambda f, c=dcolor: {
                    "color": c, "weight": 2, "dashArray": "4,3", "fillColor": c, "fillOpacity": 0.15,
                },
                tooltip=f"{dname} — district of {sel_muni}",
            ).add_to(m)
            parts = dpoly.geoms if dpoly.geom_type == "MultiPolygon" else [dpoly]
            for part in parts:
                c = part.representative_point()
                label(c.y, c.x, dname, dcolor, size=10, weight=600)

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

    # Public transit network -- trams (the metro system), a BRT corridor,
    # and two commuter rail lines. Always shown once the metropole is
    # active, no click interaction (structural, not a project to resolve).
    for line in TRANSIT_LINES:
        style = TRANSIT_MODE_STYLE[line["mode"]]
        points = [STOP_COORDS[s] for s in line["stops"]]
        folium.PolyLine(
            locations=[list(p) for p in points],
            color=line["color"], weight=style["weight"], opacity=0.85,
            dash_array=style["dash_array"],
            tooltip=f"{line['name']} ({line['mode'].upper()}): {transit_route_label(line)}",
        ).add_to(m)

    # Major roads -- committed infrastructure, not a project to decide on.
    for road in ROAD_NETWORK:
        style = ROAD_KIND_STYLE[road["kind"]]
        route_label = " → ".join(f"{name} ({STOP_STREETS.get(name, name)})" for name, _ in road["route"])
        folium.PolyLine(
            locations=[list(pt) for _, pt in road["route"]],
            color=road["color"], weight=style["weight"], opacity=0.75,
            dash_array=style["dash_array"],
            tooltip=f"{road['name']}: {route_label}",
        ).add_to(m)

    # Coach Terminal -- Tram T1's terminus, on the Metropolitan Ring Road at
    # Vărvăreuca's Heritage Quarter boundary.
    folium.Marker(
        location=list(_COACH_TERMINAL_PT),
        icon=folium.DivIcon(html=(
            '<div style="font-size:20px;line-height:1;transform:translate(-50%,-100%);'
            'filter:drop-shadow(0 1px 2px rgba(0,0,0,.5));">🚌</div>'
        )),
        tooltip="Autogara Metropolitană — Coach Terminal, Tram T1 terminus, on the Metropolitan Ring Road "
                "at Vărvăreuca's Heritage Quarter boundary",
    ).add_to(m)

    # Mărculești–Florești International Airport -- its own sign, same
    # treatment as the Coach Terminal.
    folium.Marker(
        location=list(_MARCULESTI_AIRPORT_PT),
        icon=folium.DivIcon(html=(
            '<div style="font-size:20px;line-height:1;transform:translate(-50%,-100%);'
            'filter:drop-shadow(0 1px 2px rgba(0,0,0,.5));">✈️</div>'
        )),
        tooltip="Mărculești–Florești International Airport",
    ).add_to(m)

    # Florești HPP -- the hydroelectric power plant on the Răut river,
    # managed by HydroTechnique Ltd., same sign treatment as the Coach
    # Terminal/Airport.
    folium.Marker(
        location=list(_HPP_PT),
        icon=folium.DivIcon(html=(
            '<div style="font-size:20px;line-height:1;transform:translate(-50%,-100%);'
            'filter:drop-shadow(0 1px 2px rgba(0,0,0,.5));">⚡</div>'
        )),
        tooltip="Florești HPP — hydroelectric power plant on the Răut river, managed by HydroTechnique Ltd.",
    ).add_to(m)

    # The Civic District (Centrul Civic, Florești Central) -- seat of the
    # Metropolitan Council, the Florești Prefecture, and their directorates.
    folium.Marker(
        location=list(CIVIC_DISTRICT_PT),
        icon=folium.DivIcon(html=(
            '<div style="font-size:20px;line-height:1;transform:translate(-50%,-100%);'
            'filter:drop-shadow(0 1px 2px rgba(0,0,0,.5));">🏛️</div>'
        )),
        tooltip="Centrul Civic — seat of the Metropolitan Council, the Florești Prefecture, and their directorates",
    ).add_to(m)

    # Prefecture Towns -- Cunicea and Răduleni, real villages outside the
    # metropole and the Technopolis Okrugs, grown into small towns with
    # their own town council, directly under the prefecture. A larger
    # green territory circle (vs. the Technopolis Okrugs' gold one) --
    # these towns are bigger and multi-industry, not mono-industrial.
    for town in PREFECTURE_TOWNS:
        lat, lon = STOP_COORDS[town["name"]]
        factories = FACTORIES.get(town["name"], [])
        folium.Circle(
            location=[lat, lon],
            radius=town["radius"],
            color="#2e7d32", weight=2, dash_array="5,5",
            fill=True, fill_color="#66bb6a", fill_opacity=0.25,
            tooltip=f"{town['name']} — Prefecture Town, {len(factories)} factories, own town council",
        ).add_to(m)
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=(
                '<div style="font-size:20px;line-height:1;transform:translate(-50%,-100%);'
                'filter:drop-shadow(0 1px 2px rgba(0,0,0,.5));">🏘️</div>'
            )),
            tooltip=f"{town['name']} — Prefecture Town, own town council",
        ).add_to(m)

    # CBD masterplan footprint -- shown as a zone on the map itself, not
    # just linked from Florești Central's municipal-view expander below.
    cbd_min_lat, cbd_min_lon, cbd_max_lat, cbd_max_lon = CBD_ZONE_BOUNDS
    folium.Rectangle(
        bounds=[[cbd_min_lat, cbd_min_lon], [cbd_max_lat, cbd_max_lon]],
        color="#1d4ed8", weight=2, dash_array="6,4", fill=True, fill_color="#60a5fa", fill_opacity=0.2,
        tooltip="📐 Proposed CBD — concept masterplan for the riverside land between Centrul Civic and the Răut",
    ).add_to(m)

    interchange_icon_html = (
        '<div style="width:16px;height:16px;border-radius:50%;background:#fff;'
        'border:3px solid #222;box-shadow:0 1px 3px rgba(0,0,0,.5);"></div>'
    )
    for stop, lines in transit_interchanges().items():
        lat, lon = STOP_COORDS[stop]
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=interchange_icon_html, icon_size=(16, 16), icon_anchor=(8, 8)),
            tooltip=f"⇄ {stop} interchange — {', '.join(lines)}",
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
st.title("North East Simulator")
st.caption(
    "A governance-simulation covering two fictional metropoles in the same real North-East Moldova "
    "corridor: **Florești Metropole** (below) and **Rabnirez Metropole** — Rîbnița and Rezina, a "
    "speculative cross-Nistru reunification thought experiment, not a real policy position."
)

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
    it's resolved, or the result -- effects graph + explanation -- once
    it is."""
    resolved = st.session_state.resolved_projects.get(project["id"])
    st.markdown(f"**{project['title']}**")
    if resolved:
        if resolved["choice"] is None:
            st.caption("⏭️ Skipped")
        else:
            st.success(f"{resolved['choice']}) {resolved['label']}")
            _, effects, _ = project["options"][resolved["choice"]]
            if effects:
                st.bar_chart(pd.DataFrame({"Effect": effects}))
            st.caption(f"🌐 {project['intl']}")
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


def render_project_readonly(project):
    """A project/policy's status with no buttons -- used in the
    Decentralization Structure tab, which explains the governance
    hierarchy and points to the Policy Simulation tab to actually decide
    anything, rather than resolving decisions itself."""
    resolved = st.session_state.resolved_projects.get(project["id"])
    if resolved is None:
        st.markdown(f"- **{project['title']}** — not yet decided *(see the Policy Simulation tab)*")
    elif resolved["choice"] is None:
        st.markdown(f"- **{project['title']}** — ⏭️ Skipped")
    else:
        st.markdown(f"- **{project['title']}** — ✅ {resolved['choice']}) {resolved['label']}")


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

# ---------- Florești Metropole: tabbed menu ----------
# One flat scrolling page got chaotic once every governance layer, dashboard,
# and reference section piled up in sequence. Split into a proper menu
# instead: Decentralization Structure (the governance hierarchy itself,
# click-to-drill-down plus its policy/project levers), Directorates (every
# tier's org chart, flat), Map (the full interactive map on its own), Industry
# (factories + Technopolis Okrugs' product lines and their own policy),
# Schools (K-12/lycee only), Universities (FlorTech/AgroFlor -- these report
# to the national Ministry of Education, not the Prefecture's own decentralized
# education directorate, so they get their own tab rather than sitting under
# Schools), Transportation (transit + roads + operators), and Policy
# Simulation (every governance level's real policies, reachable directly by
# picking a level, instead of navigating each one's own natural section).
# Streamlit still executes every tab's code on each rerun -- tabs only
# hide/show already-rendered output client-side -- so state shared across
# tabs (map clicks driving the structure tab's drill-down, a policy resolved
# from the simulation tab showing up at its natural level too, etc.) stays
# consistent regardless of which tab is currently visible.
st.subheader("🏙️ Florești Metropole")
(tab_structure, tab_directorates, tab_map, tab_industry, tab_schools,
 tab_universities, tab_transport, tab_policy_sim) = st.tabs([
    "🏛️ Decentralization Structure", "🏢 Directorates", "🗺️ Map",
    "🏭 Industry", "📚 Schools", "🎓 Universities", "🚌 Transportation",
    "📈 Policy Simulation",
])

# ---------- Map tab ----------
with tab_map:
    st.caption(
        "The metropole's full territory, transit network, roads, and key sites. Click a municipality, "
        "district, or campus marker to drill into it -- see the Decentralization Structure and Schools "
        "tabs for the result."
    )
    map_key = "metro_map_active" if st.session_state.metro_active else "metro_map_inactive"
    map_state = st_folium(build_map(), height=560, use_container_width=True, key=map_key)

def _closest_marker_within(lat, lon, coords_by_id, tolerance=0.004):
    """Nearest id in a {id: (lat, lon)} dict, if within tolerance (~400m) --
    used to figure out which marker a map click landed on."""
    best_id, best_dist = None, tolerance
    for marker_id, (mlat, mlon) in coords_by_id.items():
        dist = ((lat - mlat) ** 2 + (lon - mlon) ** 2) ** 0.5
        if dist < best_dist:
            best_id, best_dist = marker_id, dist
    return best_id


# Clicking a municipality's shape, a district's quadrant, or a campus marker
# drills into it, same as clicking its name/button in the Decentralization
# Structure/Schools tabs. streamlit-folium's last_object_clicked_tooltip is
# unreliable for GeoJson polygon layers (it comes back None even though the
# layer has a bound tooltip -- a streamlit-folium quirk, not specific to this
# app's layers), so click detection instead uses last_object_clicked (the
# real lat/lng clicked) and does its own point-in-polygon / nearest-marker
# matching, same geometry the map itself was built from. This runs every
# rerun regardless of which tab is visible, since Streamlit tabs don't skip
# execution -- they only hide/show already-rendered output.
if st.session_state.metro_active and map_state and map_state.get("last_object_clicked"):
    click = map_state["last_object_clicked"]
    click_pt = Point(click["lng"], click["lat"])
    polygons, _ = compute_metro_polygons()

    campus_id = _closest_marker_within(click["lat"], click["lng"], FLORTECH_CAMPUS_LOCATIONS)
    if campus_id and st.session_state.selected_campus != campus_id:
        st.session_state.selected_campus = campus_id
        st.rerun()

    agro_campus_id = _closest_marker_within(click["lat"], click["lng"], AGROFLOR_CAMPUS_LOCATIONS)
    if agro_campus_id and st.session_state.selected_agro_campus != agro_campus_id:
        st.session_state.selected_agro_campus = agro_campus_id
        st.rerun()

    sel_muni_click = st.session_state.selected_municipality
    if sel_muni_click and polygons.get(sel_muni_click) is not None:
        for dname, dpoly in compute_district_polygons(sel_muni_click, polygons[sel_muni_click]).items():
            if dpoly.contains(click_pt) and st.session_state.selected_district != dname:
                st.session_state.selected_district = dname
                st.rerun()
    else:
        for muni_name, poly in polygons.items():
            if poly.contains(click_pt) and st.session_state.selected_municipality != muni_name:
                st.session_state.selected_municipality = muni_name
                st.session_state.selected_district = None
                st.rerun()

# ---------- Decentralization Structure tab ----------
with tab_structure:
    st.markdown(
        "Florești's governance is explained top to bottom, Prefecture down to Municipality/District/"
        "Town, as **three borrowed models layered on top of each other** rather than one uniform "
        "system:"
    )
    st.markdown(
        "1. 🇫🇷 **Prefecture** — the outer tier, a real French-style *deconcentrated* state "
        "administration (a reframing of Raionul Florești). Always in effect, whether or not the "
        "metropole below has been established.\n"
        "2. 🏙️ **Metropole** — carved out *within* the Prefecture, this tier is genuinely **mixed "
        "decentralization**, combining three different real-world models at once:\n"
        "   - 🇹🇷 **Istanbul's ilçe** + 🇭🇺 **Budapest's kerület** — the metropolitan tier itself, "
        "governing 4 **Municipalities**, each inaugurated separately and each split into its own 4 "
        "**Districts** (16 total).\n"
        "   - 🇷🇺 **Moscow's Zelenograd** — the **Technopolis Okrugs** (Prajila, Ciripcău), detached "
        "single-industry okrugs administratively sponsored by the metropole rather than ordinary "
        "municipalities.\n"
        "   - **Suburbs** stay administratively dependent on the metropole, with no local government "
        "of their own.\n"
        "3. 🏘️ **Prefecture Towns** — Cunicea and Răduleni sit *alongside* the Metropole, not under "
        "it: real French-model small towns directly under the Prefecture, each with its own town "
        "council."
    )
    if not st.session_state.metro_active:
        st.info("Choose **B) Establish Florești Metropole** in Scenario 1 to activate the Metropole "
                "tier described above.")
    else:
        st.caption("Click a municipality below (or on the Map tab) to drill down into its districts. "
                   "See the Directorates tab for every tier's own org chart, and the Policy Simulation "
                   "tab to actually decide any of the policies mentioned below.")

    st.markdown("#### 🏛️ Prefecture Policies")
    for policy in PREFECTURE_POLICIES:
        render_project_readonly(policy)

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
                    "one flagship company rather than ordinary municipal government. See the Industry tab "
                    "for each okrug's full product line."
                )
                for okrug in TECHNOPOLIS_OKRUGS:
                    loc = find_locality(okrug["name"])
                    st.markdown(f"**{loc['display_name']}** ({loc['type']}) — {okrug['company']} · {okrug['sector']}")

            resolved_scenarios = st.session_state.resolved_scenarios
            if resolved_scenarios:
                with st.expander(f"📋 Current Policies ({len(resolved_scenarios)} decided)"):
                    for s in SCENARIOS:
                        r = resolved_scenarios.get(s["id"])
                        if not r:
                            continue
                        if r["choice"] is None:
                            st.markdown(f"- **{s['title']}** — ⏭️ Skipped")
                        else:
                            st.markdown(f"- **{s['title']}** — {r['choice']}) {r['label']}")

            st.markdown("#### 🏗️ Metropolitan Projects")
            for project in METRO_PROJECTS:
                render_project_readonly(project)

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
                st.caption(f"Anchor: {anchor['display_name']} · see the Directorates tab for this "
                           "municipality's own departments.")

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
                            render_project_readonly(project)
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
                st.caption(f"District of **{sel_muni}**, Florești Metropole · see the Directorates tab "
                           "for this district's own civic office.")
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
                            render_project_readonly(project)
                    else:
                        st.caption(f"Inaugurate {sel_muni} to unlock projects in this district.")

    # Prefecture Towns -- a third branch under the Prefecture, alongside the
    # Metropole (with its Suburbs and Technopolis Okrugs) above: same
    # governance scheme top to bottom -- Prefecture, then the Metropole
    # (drill down into its municipalities/districts by clicking), then the
    # Prefecture's two towns.
    st.markdown("#### 🏘️ Prefecture Towns")
    st.caption(
        "Beside the metropole (with its Technopolis Okrugs and suburbs), two real villages have grown "
        "into small towns directly under the prefecture, each with its own town council and policies -- "
        "connected to Florești by regional rail, and to the Metropolitan Ring Road by a regional expressway."
    )
    for town in PREFECTURE_TOWNS:
        st.markdown(f"**{town['name']}** — {town['note']}")
        for policy in TOWN_POLICIES[town["id"]]:
            render_project_readonly(policy)

# ---------- Directorates tab ----------
# Every governance tier's own directorates/departments/civic offices, in
# one consolidated view -- the drill-down in the Decentralization Structure
# tab points here rather than repeating each tier's org chart inline.
with tab_directorates:
    st.caption(
        "Every governance tier's own directorates/departments/civic offices, in one place -- purely "
        "descriptive, no cost or score effects."
    )
    with st.expander(f"🏛️ Florești Prefecture — Directorates ({len(PREFECTURE_DIRECTORATES)})"):
        st.caption(
            "The French-style prefecture's own deconcentrated state administration, in effect "
            "regardless of whether the metropole has been established — the state tier the metropole "
            "is carved out of."
        )
        for d in PREFECTURE_DIRECTORATES:
            st.markdown(f"- **{d['name']}** — {d['mandate']}")
    for town in PREFECTURE_TOWNS:
        with st.expander(f"🏘️ {town['name']} Town Council ({len(town['council'])})"):
            for d in town["council"]:
                st.markdown(f"- **{d['name']}** — {d['mandate']}")

    if st.session_state.metro_active:
        with st.expander(f"🏢 Metropolitan Council — Directorates ({len(METRO_COUNCIL_DIRECTORATES)})"):
            for d in METRO_COUNCIL_DIRECTORATES:
                st.markdown(f"- **{d['name']}** — {d['mandate']}")
        for muni_name, info in METRO_STRUCTURE.items():
            depts = MUNICIPALITY_DEPARTMENTS[muni_name]
            with st.expander(f"🏢 {muni_name} — {len(depts)} departments, {len(info['districts'])} district offices"):
                for d in depts:
                    st.markdown(f"- **{d['name']}** — {d['mandate']}")
                st.markdown("**District Civic Offices**")
                for dist in info["districts"]:
                    office = district_office(muni_name, dist)
                    st.markdown(f"- {office['name']}")
    else:
        st.caption("Establish the metropole (Scenario 1, option B) to see the Metropolitan Council and "
                   "each municipality's own departments and district civic offices here too.")

# ---------- Industry tab ----------
# Technopolis Okrugs' full product lines (the Decentralization Structure tab
# only names them administratively) plus every location's factories.
with tab_industry:
    st.caption(
        "Every Technopolis Okrug's flagship company, product line, and its own real production-line "
        "policy, plus every location's own factories (name, sector, products) -- factories are purely "
        "descriptive, but each okrug's own policy is a real Cost + effects decision like any other "
        "governance level's (see also the Policy Simulation tab)."
    )
    st.markdown("#### 🏭 Technopolis Okrugs")
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
        for policy in TECHNOPOLIS_POLICIES.get(okrug["name"], []):
            render_project(policy, f"{loc['display_name']} Technopolis Okrug", "okrug_policy")

    def _factory_expander(name):
        factories = FACTORIES.get(name, [])
        if not factories:
            return
        with st.expander(f"{name} — {len(factories)} factories"):
            for f in factories:
                st.markdown(f"- **{f['name']}** — *{f['sector']}.* {', '.join(f['products'])}")

    st.markdown("#### 🏭 Factories")
    st.markdown("**Beside the metropole**")
    for name in ["Cunicea", "Răduleni"]:
        _factory_expander(name)
    if st.session_state.metro_active:
        st.markdown("**Within the metropole**")
        for name in list(METRO_STRUCTURE) + [s["name"] for s in SUBURBS] + ["Ciripcău"]:
            _factory_expander(name)
    else:
        st.caption("Establish the metropole (Scenario 1, option B) to see factories across the "
                   "municipalities, suburbs, and Ciripcău too.")

# ---------- Schools tab ----------
# Every location's own K-12/lycee schools -- the universities (FlorTech,
# AgroFlor) get their own separate tab, since they're not part of this same
# tier: they answer to the national Ministry of Education, not the
# Prefecture's own decentralized education directorate.
with tab_schools:
    def _school_expander(name):
        schools = SCHOOLS.get(name, [])
        if not schools:
            return
        with st.expander(f"{name} — {len(schools)} schools"):
            for s in schools:
                st.markdown(f"- {s}")

    st.caption(
        "Every location's own K-12/lycee schools, browsable in one place -- purely descriptive, no "
        "cost or score effects. See the Universities tab for FlorTech and AgroFlor."
    )
    st.markdown("**Beside the metropole**")
    for name in ["Cunicea", "Răduleni"]:
        _school_expander(name)
    if st.session_state.metro_active:
        st.markdown("**Within the metropole**")
        for name in list(METRO_STRUCTURE) + [s["name"] for s in SUBURBS] + ["Ciripcău"]:
            _school_expander(name)
    else:
        st.caption("Establish the metropole (Scenario 1, option B) to see schools across the "
                   "municipalities, suburbs, and Ciripcău too.")

# ---------- Universities tab ----------
# FlorTech and AgroFlor -- unlike K-12/lycee schools (a Prefecture/municipal
# education-directorate concern), Moldova's real universities report
# directly to the national Ministry of Education, so these two get their
# own tab rather than sitting under Schools.
with tab_universities:
    st.caption(
        "FlorTech and AgroFlor answer to the national Ministry of Education directly, not the "
        "Prefecture's own education directorate -- their campuses, programs, labs, and other "
        "infrastructure, browsable here separately from the K-12/lycee schools in the Schools tab."
    )
    st.markdown("#### 🎓 FlorTech — Florești University of Technology")
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

    st.markdown("#### 🌾 AgroFlor — Florești University of Agricultural Sciences and Technologies")
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

# ---------- Transportation tab ----------
# Transit lines/interchanges and roads/key sites, plus the two operators that
# run them: MetroFlor (the Metropolitan Council's own operator, everything
# that stays within the metropole) and FlorLink (the Prefecture's own
# operator, connecting Florești to the Prefecture Towns and beyond).
with tab_transport:
    st.markdown("#### 🚍 Operators")
    for op in TRANSIT_OPERATORS:
        op_lines = [l for l in TRANSIT_LINES if l["id"] in op["line_ids"]]
        with st.expander(f"{op['name']} — {op['level']} operator ({len(op_lines)} lines)"):
            st.caption(op["note"])
            for line in op_lines:
                st.markdown(f"- **{line['name']}** — {TRANSIT_MODE_LABELS[line['mode']]}")

    with st.expander(f"🚊 Public Transit Network ({len(TRANSIT_LINES)} lines)"):
        st.caption(
            "**Gara Florești** (the Florești Central stop) is the hub where every mode meets. Rail "
            "runs in two tiers: **Metro M1** is the backbone spanning all 4 municipalities; "
            "**Metro M2** crosses it there, running Coach Terminal ↔ Gara Florești ↔ Florești "
            "Central North. **Tram T1** is a short local shuttle from Gara Florești out to Centrul "
            "Civic. Road transit runs in three tiers, each with denser stops than the rail lines: "
            "**BRT** lines reach further out at commuter-rail-equivalent speed and don't stop as "
            "often; plain **biogas/electric buses** cover local routes with no dedicated lane; "
            "**regional rail** reaches the prefecture's own small towns (Cunicea, Răduleni). Routes "
            "below are proposed street-level alignments, not a surveyed plan."
        )
        for line in TRANSIT_LINES:
            st.markdown(f"**{line['name']}** — {TRANSIT_MODE_LABELS[line['mode']]}  \n{transit_route_label(line)}")
        st.markdown("**⇄ Interchanges**")
        for stop, lines in transit_interchanges().items():
            st.markdown(f"- **{stop}** — {', '.join(lines)}")

    with st.expander(f"🛣️ Roads & Key Sites ({len(ROAD_NETWORK)} roads)"):
        st.caption(
            "Committed infrastructure shown on the Map tab, not a METRO_PROJECTS decision to resolve. "
            "The Ring Road stays outside the municipalities' own built territory, tracing the metro's "
            "southern periphery close to Vărvăreuca's Heritage Quarter and Forestry District rather "
            "than cutting through the metropole itself."
        )
        for road in ROAD_NETWORK:
            route_label = " → ".join(f"{name} ({STOP_STREETS.get(name, name)})" for name, _ in road["route"])
            st.markdown(f"**{road['name']}**  \n{route_label}")
        st.markdown(
            "**🚌 Autogara Metropolitană (Coach Terminal)** — on Vărvăreuca's Heritage Quarter "
            "boundary, on the Metropolitan Ring Road, Tram T1's terminus and a FlorLink coach hub."
        )
        st.markdown(
            "**✈️ Mărculești–Florești International Airport** — its own sign on the map, same "
            "treatment as the Coach Terminal."
        )
        st.markdown(
            "**🏛️ Centrul Civic (Civic Center)** — Florești Central's own civic district, seat "
            "of the Metropolitan Council, the Florești Prefecture, and their directorates."
        )
        st.markdown(
            "**🏘️ Cunicea & Răduleni** — Prefecture Towns, each with its own 🏘️ sign on the map, "
            "reached by FlorLink regional rail and the Regional Expressway (which joins the "
            "Metropolitan Ring Road at Ghindești)."
        )
        st.markdown(
            "**📐 Proposed CBD** — the riverside zone shown on the map between Centrul Civic and "
            "the Răut; see the full concept masterplan in Florești Central's own municipal view."
        )
        st.markdown(
            "**⚡ Florești HPP** — the hydroelectric power plant on the Răut river, just downstream "
            "of the CBD riverside land, managed by HydroTechnique Ltd. (see the Industry tab)."
        )

# ---------- Policy Simulation tab ----------
# One selector reaching every governance level's own real policies/projects
# directly, instead of navigating to each level's own natural section --
# Prefecture, Metropole, Municipality, District, Town, and Technopolis all
# have their own real Cost + effects decisions. Resolving one here uses the
# exact same render_project()/resolved_projects mechanism as everywhere
# else in the app (keyed by the project's own id, not by which UI rendered
# it), so it's a real decision, not a preview -- it shows up at that
# level's own natural section too, and vice versa.
with tab_policy_sim:
    st.markdown("#### 📊 Where the metropole stands right now")
    sim_fig, sim_ax = plt.subplots(figsize=(8, 3.2))
    sim_metrics = ["Governance", "Economy", "Stability", "Risk"]
    sim_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    sim_values = [st.session_state.scores[m] for m in sim_metrics]
    sim_ax.barh(sim_metrics, sim_values, color=sim_colors)
    sim_ax.set_xlim(0, 100)
    sim_ax.set_xlabel("Score (0-100)")
    sim_ax.invert_yaxis()
    for i, v in enumerate(sim_values):
        sim_ax.text(v + 1, i, str(v), va="center")
    st.pyplot(sim_fig)
    st.caption(
        "**In plain language:** Governance is how effective and trusted the administration is. "
        "Economy is the strength of local business and jobs. Stability is public order and calm. "
        "Risk is the chance of a crisis -- for Risk, lower is better; for the other three, higher is "
        "better. Every policy below moves one or more of these four numbers."
    )

    st.caption(
        "Pick a governance level to jump straight to its own real policies/projects -- the same "
        "Cost + effects decisions available at that level's own section elsewhere in the app. "
        "Resolving one here is a real decision: it spends budget and shows up at that level's own "
        "section too. Once resolved, each card shows the effects it applied (graph) and its own "
        "explanation."
    )
    policy_sim_level = st.radio(
        "Governance level",
        ["Prefecture", "Metropole", "Municipality", "District", "Town", "Technopolis"],
        horizontal=True, key="policy_sim_level",
    )

    if policy_sim_level == "Prefecture":
        for policy in PREFECTURE_POLICIES:
            render_project(policy, "Prefecture", "policysim_prefecture")

    elif policy_sim_level == "Metropole":
        if not st.session_state.metro_active:
            st.info("Establish the metropole (Scenario 1, option B) to see Metropolitan Projects.")
        else:
            for project in METRO_PROJECTS:
                render_project(project, "Metropolitan", "policysim_metro")

    elif policy_sim_level == "Municipality":
        if not st.session_state.metro_active:
            st.info("Establish the metropole (Scenario 1, option B) first.")
        else:
            ps_muni = st.selectbox("Municipality", list(METRO_STRUCTURE), key="policy_sim_muni")
            ps_projects = MUNICIPALITY_PROJECTS.get(ps_muni, [])
            ps_active = ps_muni in st.session_state.inaugurated
            if not ps_projects:
                st.caption(f"{ps_muni} has no municipal projects defined.")
            elif not ps_active:
                st.caption(f"Inaugurate {ps_muni} (from its own municipal view, in the "
                           "Decentralization Structure tab) to unlock its projects.")
            else:
                for project in ps_projects:
                    render_project(project, f"{ps_muni} municipal", "policysim_muni")

    elif policy_sim_level == "District":
        if not st.session_state.metro_active:
            st.info("Establish the metropole (Scenario 1, option B) first.")
        else:
            ps_dist_muni = st.selectbox("Municipality", list(METRO_STRUCTURE), key="policy_sim_dist_muni")
            ps_dist = st.selectbox("District", METRO_STRUCTURE[ps_dist_muni]["districts"], key="policy_sim_dist")
            ps_dist_projects = DISTRICT_PROJECTS.get((ps_dist_muni, ps_dist), [])
            ps_dist_active = ps_dist_muni in st.session_state.inaugurated
            if not ps_dist_projects:
                st.caption(f"{ps_dist} has no district projects defined.")
            elif not ps_dist_active:
                st.caption(f"Inaugurate {ps_dist_muni} to unlock projects in {ps_dist}.")
            else:
                for project in ps_dist_projects:
                    render_project(project, f"{ps_dist} district", "policysim_dist")

    elif policy_sim_level == "Town":
        ps_town_name = st.selectbox(
            "Prefecture Town", [t["name"] for t in PREFECTURE_TOWNS], key="policy_sim_town"
        )
        ps_town = next(t for t in PREFECTURE_TOWNS if t["name"] == ps_town_name)
        for policy in TOWN_POLICIES[ps_town["id"]]:
            render_project(policy, f"{ps_town['name']} Town Council", "policysim_town")

    else:  # Technopolis
        ps_okrug_name = st.selectbox(
            "Technopolis Okrug", [o["name"] for o in TECHNOPOLIS_OKRUGS], key="policy_sim_okrug"
        )
        for policy in TECHNOPOLIS_POLICIES.get(ps_okrug_name, []):
            render_project(policy, f"{ps_okrug_name} Technopolis Okrug", "policysim_okrug")

# ---------- Rabnirez Metropole (stage 1: structure + drill-down only) ----------
# A second region in the same North East Simulator, alongside Florești
# Metropole above -- real geography (Overpass-sourced), same governance
# scheme (French Prefecture -> Istanbul/Budapest mixed-decentralization
# Metropole -> Municipality -> District), sharing the same global
# budget/scores as everything else in the app. Always explorable, not
# gated behind a scenario choice -- map, industry, schools, transit, and
# its own Policy Simulation entry are later stages, not yet built here.
st.divider()
st.subheader("🌉 Rabnirez Metropole")
st.markdown(
    "A speculative cross-Nistru thought experiment, not a real position on Transnistria's status: "
    "**Rîbnița** (east bank) and **Rezina** (west bank), real towns on opposite sides of the Nistru "
    "river and connected by the real Rezina–Rîbnița Bridge, imagined here as sharing one governance "
    "scheme, explained top to bottom the same way as Florești:"
)
st.markdown(
    "1. 🇫🇷 **Rabnirez Prefecture** — a French-style deconcentrated administration, uniting Rîbnița "
    "raion and Rezina raion into one prefecture instead of two, the same reframing Florești Prefecture "
    "applies to Raionul Florești.\n"
    "2. 🏙️ **Rabnirez Metropole** — carved out within the prefecture, the same **mixed "
    "decentralization** as Florești: 🇹🇷 Istanbul's ilçe + 🇭🇺 Budapest's kerület, governing 2 "
    "**Municipalities** — Rîbnița and Rezina — each split into its own 4 **Districts**.\n"
    "3. 🌉 **Rezina–Rîbnița Bridge** — the real bridge across the Nistru, the metropole's own shared "
    "landmark connecting both municipalities, the way the Coach Terminal or Metro do for Florești.\n"
    "4. 🏭 Both towns are strategically industrial: Rîbnița hosts a steel/metallurgical plant and its "
    "own cement works, Rezina its own major cement works -- marked on the map below."
)

rr_map_state = st_folium(build_rabnirez_map(), height=480, use_container_width=True, key="rabnirez_map")

if rr_map_state and rr_map_state.get("last_object_clicked"):
    rr_click = rr_map_state["last_object_clicked"]
    rr_click_pt = Point(rr_click["lng"], rr_click["lat"])
    rr_polygons, _ = compute_rabnirez_metro_polygons()

    rr_sel_muni_click = st.session_state.rr_selected_municipality
    if rr_sel_muni_click and rr_polygons.get(rr_sel_muni_click) is not None:
        for rr_dname, rr_dpoly in compute_rabnirez_district_polygons(
            rr_sel_muni_click, rr_polygons[rr_sel_muni_click]
        ).items():
            if rr_dpoly.contains(rr_click_pt) and st.session_state.rr_selected_district != rr_dname:
                st.session_state.rr_selected_district = rr_dname
                st.rerun()
    else:
        for rr_muni_name, rr_poly in rr_polygons.items():
            if rr_poly.contains(rr_click_pt) and st.session_state.rr_selected_municipality != rr_muni_name:
                st.session_state.rr_selected_municipality = rr_muni_name
                st.session_state.rr_selected_district = None
                st.rerun()

rr_sel_muni = st.session_state.rr_selected_municipality
rr_sel_dist = st.session_state.rr_selected_district

if rr_sel_muni is None:
    st.caption("👆 Click a municipality on the map (or below) to see its 4 districts.")
    rr_muni_cols = st.columns(2)
    for col, name in zip(rr_muni_cols, RABNIREZ_METRO_STRUCTURE):
        with col:
            if st.button(name, key=f"rr_select_{name}", use_container_width=True):
                st.session_state.rr_selected_municipality = name
                st.session_state.rr_selected_district = None
                st.rerun()

    with st.expander(f"🏘️ Suburbs ({len(RABNIREZ_SUBURBS)}) — dependent on the metropole, no local government"):
        for suburb in RABNIREZ_SUBURBS:
            loc = find_rabnirez_locality(suburb["name"])
            st.markdown(f"- **{loc['display_name']}** ({loc['type']})")

elif rr_sel_dist is None:
    rr_info = RABNIREZ_METRO_STRUCTURE[rr_sel_muni]
    rr_anchor = find_rabnirez_locality(rr_info["anchor"])
    if st.button("← Back to Rabnirez Metropole", key="rr_back_to_metro"):
        st.session_state.rr_selected_municipality = None
        st.rerun()
    st.markdown(f"### {rr_sel_muni}")
    st.caption(f"Anchor: {rr_anchor['display_name']}")
    st.write("👆 Click a district for details:")
    rr_dist_cols = st.columns(4)
    for col, d in zip(rr_dist_cols, rr_info["districts"]):
        with col:
            if st.button(d, key=f"rr_select_district_{rr_sel_muni}_{d}", use_container_width=True):
                st.session_state.rr_selected_district = d
                st.rerun()

    rr_factories = RABNIREZ_FACTORIES.get(rr_sel_muni, [])
    if rr_factories:
        with st.expander(f"🏭 Factories ({len(rr_factories)})"):
            for f in rr_factories:
                st.markdown(f"- **{f['name']}** — *{f['sector']}.* {', '.join(f['products'])}")

else:
    if st.button(f"← Back to {rr_sel_muni}", key="rr_back_to_muni"):
        st.session_state.rr_selected_district = None
        st.rerun()
    st.markdown(f"### {rr_sel_dist}")
    st.caption(f"District of **{rr_sel_muni}**, Rabnirez Metropole.")

# ---------- Real-time clock loop ----------
# While auto-play is on, the app sleeps for one tick then reruns itself,
# firing a random world event each time — this is what keeps the
# simulation moving in real time without any extra polling/JS.
if st.session_state.autoplay:
    time.sleep(tick_interval)
    apply_random_tick()
    st.rerun()
