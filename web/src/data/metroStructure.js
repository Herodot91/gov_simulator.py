// Governance model: mixed decentralization (Istanbul + Budapest hybrid) — a
// metropolitan tier over 4 municipalities (each with real local government and
// its own sub-districts, like Istanbul's ilçe / Budapest's kerület), plus
// dependent suburbs with no independent government of their own.
export const METRO_STRUCTURE = {
  "Florești Central": {
    anchor: "Florești",
    districts: ["Centrul Civic", "Central Market District", "Răut Riverside District", "Politeh"],
  },
  "Mărculești": {
    anchor: "Mărculești",
    districts: ["Airport District", "Aviagorodok", "Industrial District", "Mărculești Residential District"],
  },
  "Vărvăreuca": {
    anchor: "Vărvăreuca",
    districts: ["Vărvăreuca Residential District", "Agricultural District", "Forestry District", "Heritage Quarter"],
  },
  "Lunga": {
    anchor: "Lunga",
    districts: ["Lunga Residential District", "Orchard District", "Green Belt District", "Artisan Quarter"],
  },
};

export const SUBURBS = [{ name: "Ghindești" }, { name: "Gura Camencii" }];

export const MUNICIPALITY_COLORS = {
  "Florești Central": "#4cc9f0",
  "Mărculești": "#8338ec",
  "Vărvăreuca": "#8ab17d",
  "Lunga": "#e76f51",
};

export const INAUGURATION_COST = 15;

// A second, non-interactive governance layer sitting alongside the French
// prefecture model: a Moscow-style detached satellite okrug, after
// Zelenograd (Moscow's own physically separate single-industry
// administrative okrug). Real villages, well outside the metropole's own
// territory, each sponsored as a single-company technopolis rather than
// folded into ordinary municipal structure. Structural world-building, not
// a scenario -- no cost, no score effects, nothing to click through.
export const TECHNOPOLIS_OKRUGS = [
  {
    name: "Prajila",
    company: "PHI — Prajila Heavy Industry",
    sector: "Heavy machinery & construction equipment",
    note: "An alternative to Hitachi, Caterpillar, Komatsu, and Hyundai's construction arm.",
  },
  {
    name: "Ciripcău",
    company: "Sigma Motors",
    sector: "Hybrid & electric vehicles",
    note: "Coupé, hatchback, and urban SUV lines built for the domestic and regional market.",
  },
];
