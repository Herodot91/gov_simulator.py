// Public transit network -- structural world-building like the Technopolis
// Okrugs/FlorTech/AgroFlor: no cost, no score effects, always shown on the
// map once the metropole is active. The metro system runs on trams, not
// heavy rail, and stays inside the 4 municipalities -- unlike the BRT and
// commuter lines, it doesn't reach the suburbs. A BRT corridor
// (biogas/electric buses) covers what trams don't; two commuter rail lines
// reach past the metropole's own territory to Gura Căinarului and to the
// Prajila Technopolis Okrug.
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
// Tram M2's own points: a stop on Florești Central's own northern boundary,
// and the Coach Terminal on Vărvăreuca's Heritage Quarter boundary (also
// where the Metropolitan Ring Road passes -- see ROAD_NETWORK below). M2
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
};

export const TRANSIT_LINES = [
  {
    id: "tram_m1",
    name: "Tram M1",
    mode: "tram",
    color: "#c0392b",
    stops: ["Vărvăreuca", "Florești Central", "Lunga", "Mărculești"],
  },
  {
    id: "tram_m2",
    name: "Tram M2",
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
    id: "commuter_c1",
    name: "Commuter C1",
    mode: "commuter",
    color: "#2c3e50",
    stops: ["Ghindești", "Florești Central", "Lunga", "Mărculești Airport", "Gura Căinarului"],
  },
  {
    id: "commuter_c2",
    name: "Commuter C2",
    mode: "commuter",
    color: "#34495e",
    stops: ["Gura Camencii", "Florești Central", "Lunga", "Prajila"],
  },
];

// Line styling by mode: trams (the metro system) run solid, BRT dashed
// (it's a bus corridor, not rail), commuter rail dash-dotted.
export const TRANSIT_MODE_STYLE = {
  tram: { weight: 5, dashArray: null },
  brt: { weight: 4, dashArray: "10 6" },
  commuter: { weight: 4, dashArray: "2 6" },
};

// Stops served by 2+ transit lines -- where trams interchange with each
// other, the BRT line, and the commuter lines.
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

// Two major roads, shown on the map as committed infrastructure (not a
// METRO_PROJECTS decision to resolve) -- the Metropolitan Ring Road stays
// outside the municipalities' own built territory, tracing the metro's
// southern periphery close to Vărvăreuca's Heritage Quarter and Forestry
// District (its own two southernmost districts) rather than cutting through
// the metropole itself, on its way from Ghindești to Gura Căinarului. The
// Technopolis Expressway links the two Technopolis Okrugs via the airport.
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
