// Layer-scoped development projects — same interactive shape as SCENARIOS
// (options with Cost + score effects), but each project lives at exactly one
// governance layer and only unlocks once that layer is active: metropole
// projects once the metropole is established, municipal/district projects
// once their municipality is inaugurated (districts don't inaugurate
// separately, they ride on their municipality's status).
export const METRO_PROJECTS = [
  {
    id: "ring_road",
    title: "Florești Ring Road",
    options: {
      A: ["Build the full ring road", { Economy: +10, Stability: +5 }, 30],
      B: ["Partial bypass only", { Economy: +5 }, 15],
    },
    intl: "The EU regional development fund shows interest in cross-border logistics.",
  },
  {
    id: "metro_line1",
    title: "Metro Line 1",
    options: {
      A: ["Build the light-rail line", { Economy: +8, Governance: +5, Stability: +5 }, 35],
      B: ["Feasibility study only", { Governance: +3 }, 10],
    },
    intl: "Investors eye Florești as a regional transit hub.",
  },
  {
    id: "rail_airport_link",
    title: "Railway Station – Airport Link",
    options: {
      A: ["Build a direct rail link to Mărculești Airport", { Economy: +10, Risk: -3 }, 25],
      B: ["Shuttle bus service only", { Economy: +3 }, 8],
    },
    intl: "Aeroportul Internațional Mărculești pushes for better ground transit.",
  },
];

export const MUNICIPALITY_PROJECTS = {
  "Florești Central": [
    {
      id: "raut_plaza",
      title: "Răut Plaza",
      options: {
        A: ["Full plaza redevelopment", { Stability: +5, Economy: +5 }, 20],
        B: ["Basic renovation", { Stability: +2 }, 10],
      },
      intl: "Residents petition for a new riverside public space.",
    },
  ],
  "Vărvăreuca": [
    {
      id: "new_avenue",
      title: "New Avenue",
      options: {
        A: ["Build a new avenue toward Florești", { Economy: +7, Stability: +3 }, 22],
        B: ["Minor road upgrade", { Economy: +3 }, 10],
      },
      intl: "Vărvăreuca residents demand better connectivity.",
    },
  ],
};

// Keyed by "Municipality::District" (JS objects can't key on arrays/tuples).
export const DISTRICT_PROJECTS = {
  "Lunga::Green Belt District": [
    {
      id: "community_park",
      title: "Community Park",
      options: {
        A: ["Build the park", { Stability: +5, Governance: +2 }, 12],
      },
      intl: "Environmental groups praise the green-space initiative.",
    },
  ],
  "Lunga::Lunga Residential District": [
    {
      id: "school_reconstruction",
      title: "School Reconstruction",
      options: {
        A: ["Full reconstruction", { Governance: +5, Stability: +3, Economy: +2 }, 18],
        B: ["Partial repairs", { Stability: +1 }, 8],
      },
      intl: "The Ministry of Education monitors rural school conditions.",
    },
  ],
};

export function districtProjectKey(municipality, district) {
  return `${municipality}::${district}`;
}

// Each Technopolis Okrug gets its own real interactive policy, same
// Cost + effects shape as Town Policies -- keyed by the okrug's own
// "name", same convention as FACTORIES/SCHOOLS in directorates.js.
export const TECHNOPOLIS_POLICIES = {
  Prajila: [
    {
      id: "prajila_expansion",
      title: "Prajila Heavy Industry — Production Line Expansion",
      options: {
        A: ["Expand PHI's heavy machinery production line", { Economy: +6, Governance: +2 }, 18],
        B: ["Maintain current production capacity", {}, 0],
      },
      intl: "PHI's export contracts draw regional investor interest.",
    },
  ],
  "Ciripcău": [
    {
      id: "ciripcau_expansion",
      title: "Sigma Motors — EV Production Line Expansion",
      options: {
        A: ["Expand Sigma Motors' EV production line", { Economy: +6, Governance: +2 }, 18],
        B: ["Maintain current production capacity", {}, 0],
      },
      intl: "Sigma Motors' EV lineup draws EU green-tech attention.",
    },
  ],
};

// Real-world reference points used to place resolved projects on the map --
// same coordinates as each municipality's real anchor locality (see
// floresti_localities.json), plus the real Mărculești airport's approximate
// centroid, since the app doesn't otherwise load the airport as its own
// feature (it's merged into Mărculești's territory).
const FLORESTI_PT = [47.8938318, 28.2996474];
const VARVAREUCA_PT = [47.8798617, 28.3113869];
const LUNGA_PT = [47.8617078, 28.231765];
const MARCULESTI_AIRPORT_PT = [47.8597, 28.213];

// How each resolved project is drawn on the map: a single "point" marker, or
// a "line" between two reference points for corridor-shaped infrastructure.
export const PROJECT_MAP_LOCATIONS = {
  ring_road: { type: "point", coord: [47.9095, 28.3105] },
  metro_line1: { type: "point", coord: FLORESTI_PT },
  rail_airport_link: { type: "line", points: [FLORESTI_PT, MARCULESTI_AIRPORT_PT] },
  raut_plaza: { type: "point", coord: [47.8918, 28.2946] },
  new_avenue: { type: "line", points: [VARVAREUCA_PT, FLORESTI_PT] },
  community_park: { type: "point", coord: [LUNGA_PT[0] + 0.0035, LUNGA_PT[1] - 0.003] },
  school_reconstruction: { type: "point", coord: [LUNGA_PT[0] - 0.0035, LUNGA_PT[1] + 0.003] },
};

// Flattened list of every project with its display scope label, used both by
// the map (to draw resolved ones) and anywhere else that needs "all projects".
export function allProjectsWithScope() {
  const out = METRO_PROJECTS.map((p) => [p, "Metropolitan"]);
  for (const [muni, list] of Object.entries(MUNICIPALITY_PROJECTS)) {
    for (const p of list) out.push([p, `${muni} municipal`]);
  }
  for (const [key, list] of Object.entries(DISTRICT_PROJECTS)) {
    const dist = key.split("::")[1];
    for (const p of list) out.push([p, `${dist} district`]);
  }
  return out;
}
