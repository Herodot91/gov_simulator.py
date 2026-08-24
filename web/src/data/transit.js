// Public transit network -- structural world-building like the Technopolis
// Okrugs/FlorTech/AgroFlor: no cost, no score effects, always shown on the
// map once the metropole is active. The metro system runs on trams, not
// heavy rail; a BRT corridor (biogas/electric buses) covers what trams
// don't; two commuter rail lines reach past the metropole's own territory
// to Gura Căinarului and to the Prajila Technopolis Okrug.
const FLORESTI_PT = [47.8938318, 28.2996474];
const VARVAREUCA_PT = [47.8798617, 28.3113869];
const LUNGA_PT = [47.8617078, 28.231765];
const MARCULESTI_PT = [47.8693441, 28.2415422];
const MARCULESTI_AIRPORT_PT = [47.8597, 28.213];
const GHINDESTI_PT = [47.8623849, 28.3870348];
const GURACAMENCII_PT = [47.8901159, 28.3553067];
const PRAJILA_PT = [47.84049, 28.2100662];
const GURA_CAINARULUI_PT = [47.8627915, 28.1831829];

export const STOP_COORDS = {
  "Ghindești": GHINDESTI_PT,
  "Florești Central": FLORESTI_PT,
  "Vărvăreuca": VARVAREUCA_PT,
  "Lunga": LUNGA_PT,
  "Mărculești": MARCULESTI_PT,
  "Mărculești Airport": MARCULESTI_AIRPORT_PT,
  "Gura Camencii": GURACAMENCII_PT,
  "Gura Căinarului": GURA_CAINARULUI_PT,
  "Prajila": PRAJILA_PT,
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
    stops: ["Ghindești", "Florești Central", "Vărvăreuca"],
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
