// Public transit network -- structural world-building like the Technopolis
// Okrugs/FlorTech/AgroFlor: no cost, no score effects, always shown on the
// map once the metropole is active. Rail runs in two tiers -- the metro
// system (Metro, heavier/longer-haul) and trams (Tram, short/local) --
// alongside road transit in three tiers of its own: BRT (limited-stop,
// commuter-equivalent reach), plain biogas/electric bus (local, no
// dedicated lane), and regional rail out to the prefecture's own small
// towns (see directorates.js's PREFECTURE_TOWNS).
const FLORESTI_PT = [47.8938318, 28.2996474];
const VARVAREUCA_PT = [47.8798617, 28.3113869];
const LUNGA_PT = [47.8617078, 28.231765];
const MARCULESTI_PT = [47.8693441, 28.2415422];
const MARCULESTI_AIRPORT_PT = [47.8597, 28.213];
const GHINDESTI_PT = [47.8623849, 28.3870348];
const GURACAMENCII_PT = [47.8901159, 28.3553067];
const PRAJILA_PT = [47.84049, 28.2100662];
const CIRIPCAU_PT = [47.9865655, 28.3838055];
const GURA_CAINARULUI_PT = [47.8627915, 28.1831829];
// Real villages, both outside the metropole and the Technopolis Okrugs,
// whose territory has grown into a small town within the prefecture -- see
// directorates.js's PREFECTURE_TOWNS. "Răduleni" uses the real Rădulenii
// Noi locality's own coordinates (preferred over Rădulenii Vechi).
const CUNICEA_PT = [47.9139733, 28.6456445];
const RADULENI_PT = [47.9567436, 28.247045];
// Tram T1's own points: a stop on Florești Central's own northern boundary,
// and the Coach Terminal on Vărvăreuca's Heritage Quarter boundary (also
// where the Metropolitan Ring Road passes -- see ROAD_NETWORK below). T1
// runs strictly between these two municipal boundaries, not into either
// municipality's own core.
const FLORESTI_NORTH_PT = [47.8998, 28.2996];
const COACH_TERMINAL_PT = [47.87, 28.3235];
const SOUTH_LUNGA_BYPASS_PT = [47.848, 28.245];
const VARVAREUCA_FORESTRY_BYPASS_PT = [47.863, 28.301];

export const STOP_COORDS = {
  "Ghindești": GHINDESTI_PT,
  "Florești Central": FLORESTI_PT,
  "Florești Central North": FLORESTI_NORTH_PT,
  "Vărvăreuca": VARVAREUCA_PT,
  "Lunga": LUNGA_PT,
  "Mărculești": MARCULESTI_PT,
  "Mărculești Airport": MARCULESTI_AIRPORT_PT,
  "Gura Camencii": GURACAMENCII_PT,
  "Gura Căinarului": GURA_CAINARULUI_PT,
  "Prajila": PRAJILA_PT,
  "Coach Terminal": COACH_TERMINAL_PT,
  "Cunicea": CUNICEA_PT,
  "Răduleni": RADULENI_PT,
};

// The real street/avenue each stop sits on -- proposed, not surveyed (same
// "concept, not an adopted plan" spirit as the CBD masterplan), but grounded
// in each stop's own already-established district/theming.
export const STOP_STREETS = {
  "Ghindești": "Strada Nucilor",
  "Florești Central": "Bulevardul Unirii, Centrul Civic",
  "Florești Central North": "Strada Ștefan cel Mare",
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
};

export const TRANSIT_LINES = [
  {
    id: "metro_m1",
    name: "Metro M1",
    mode: "metro",
    color: "#1a237e",
    stops: ["Vărvăreuca", "Florești Central", "Lunga", "Mărculești"],
  },
  {
    id: "tram_t1",
    name: "Tram T1",
    mode: "tram",
    color: "#8e44ad",
    stops: ["Coach Terminal", "Florești Central North"],
  },
  {
    id: "brt1",
    name: "BRT 1 (biogas/electric)",
    mode: "brt",
    color: "#16a085",
    stops: ["Gura Camencii", "Florești Central", "Mărculești Airport"],
  },
  {
    id: "brt2",
    name: "BRT 2 (biogas/electric)",
    mode: "brt",
    color: "#2980b9",
    stops: ["Ghindești", "Florești Central", "Lunga", "Mărculești Airport", "Gura Căinarului"],
  },
  {
    id: "brt3",
    name: "BRT 3 (biogas/electric)",
    mode: "brt",
    color: "#27ae60",
    stops: ["Gura Camencii", "Florești Central", "Lunga", "Prajila"],
  },
  {
    id: "bus_b1",
    name: "Bus B1 (biogas/electric)",
    mode: "bus",
    color: "#7f8c8d",
    stops: ["Florești Central", "Ghindești"],
  },
  {
    id: "regional_r1",
    name: "Regional Rail R1",
    mode: "regional_rail",
    color: "#7b3f00",
    stops: ["Florești Central", "Cunicea"],
  },
  {
    id: "regional_r2",
    name: "Regional Rail R2",
    mode: "regional_rail",
    color: "#5c4033",
    stops: ["Florești Central", "Răduleni"],
  },
];

// Line styling by mode: metro solid+thick, trams solid+thinner, BRT dashed
// (a bus corridor, not rail), plain buses finely dotted, regional rail
// dash-dotted.
export const TRANSIT_MODE_STYLE = {
  metro: { weight: 6, dashArray: null },
  tram: { weight: 4, dashArray: null },
  brt: { weight: 4, dashArray: "10 6" },
  bus: { weight: 3, dashArray: "2 4" },
  regional_rail: { weight: 4, dashArray: "2 6" },
};

export const TRANSIT_MODE_LABELS = {
  metro: "🚇 Metro",
  tram: "🚋 Tram",
  brt: "🚌 BRT",
  bus: "🚍 Bus",
  regional_rail: "🚆 Regional Rail",
};

// Stops served by 2+ transit lines -- where metro/trams interchange with
// each other, the BRT lines, buses, and regional rail.
export function transitInterchanges() {
  const byStop = {};
  for (const line of TRANSIT_LINES) {
    for (const stop of line.stops) {
      if (!byStop[stop]) byStop[stop] = [];
      byStop[stop].push(line.name);
    }
  }
  return Object.fromEntries(Object.entries(byStop).filter(([, lines]) => lines.length >= 2));
}

// "A (street) → B (street) → C (street)" -- the named-street route
// description, not just the bare stop list.
export function transitRouteLabel(line) {
  return line.stops.map((s) => `${s} (${STOP_STREETS[s] || s})`).join(" → ");
}

// Three major roads, shown on the map as committed infrastructure (not a
// METRO_PROJECTS decision to resolve) -- the Metropolitan Ring Road stays
// outside the municipalities' own built territory, tracing the metro's
// southern periphery close to Vărvăreuca's Heritage Quarter and Forestry
// District (its own two southernmost districts) rather than cutting through
// the metropole itself, on its way from Ghindești to Gura Căinarului. The
// Technopolis Expressway links the two Technopolis Okrugs via the airport.
// The Regional Expressway links the two Prefecture Towns to the Ring Road
// at Ghindești.
export const ROAD_NETWORK = [
  {
    id: "ring_road_metro",
    name: "Metropolitan Ring Road",
    kind: "ring_road",
    color: "#6c757d",
    route: [
      ["Ghindești", GHINDESTI_PT],
      ["Coach Terminal", COACH_TERMINAL_PT],
      ["Vărvăreuca Forestry Bypass", VARVAREUCA_FORESTRY_BYPASS_PT],
      ["South Lunga Bypass", SOUTH_LUNGA_BYPASS_PT],
      ["Mărculești Airport", MARCULESTI_AIRPORT_PT],
      ["Gura Căinarului", GURA_CAINARULUI_PT],
    ],
  },
  {
    id: "technopolis_expressway",
    name: "Technopolis Expressway",
    kind: "expressway",
    color: "#d97706",
    route: [
      ["Prajila", PRAJILA_PT],
      ["Mărculești Airport", MARCULESTI_AIRPORT_PT],
      ["Ciripcău", CIRIPCAU_PT],
    ],
  },
  {
    id: "regional_expressway",
    name: "Regional Expressway (Cunicea–Răduleni)",
    kind: "expressway",
    color: "#b45309",
    route: [
      ["Cunicea", CUNICEA_PT],
      ["Răduleni", RADULENI_PT],
      ["Ghindești", GHINDESTI_PT],
    ],
  },
];

export const ROAD_KIND_STYLE = {
  ring_road: { weight: 5, dashArray: null },
  expressway: { weight: 5, dashArray: "1 6" },
};

export function roadRouteLabel(road) {
  return road.route.map(([name]) => `${name} (${STOP_STREETS[name] || name})`).join(" → ");
}

// The Civic District -- Centrul Civic (the "Civic Center"), the first of
// Florești Central's 4 districts (see metroStructure.js and
// computeDistrictGeometries' NW/NE/SW/SE quadrant order) -- is where the
// Metropolitan Council, the Florești Prefecture, and their directorates are
// headquartered. Positioned inside that district's own NW quadrant rather
// than at the municipality's plain center, so it reads as sitting inside
// Centrul Civic once that quadrant is drawn. Structural world-building,
// ties the Directorates panels to an actual place on the map.
export const CIVIC_DISTRICT_PT = [FLORESTI_PT[0] + 0.003, FLORESTI_PT[1] - 0.003];

// The CBD masterplan's own footprint (see CbdMasterplan.jsx and the
// expander in Florești Central's municipal view) -- shown on the map itself
// as a zone, not just linked from an expander. The riverside land between
// Centrul Civic and the Răut, around the Metro Line 1 station and Răut
// Plaza. [south-west corner, north-east corner], Leaflet lat/lon order.
export const CBD_ZONE_BOUNDS = [
  [47.8893, 28.2918],
  [47.8935, 28.2965],
];
