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

export const SUBURBS = [{ name: "Ghindești" }, { name: "Gura Camencii" }, { name: "Prajila" }];

export const MUNICIPALITY_COLORS = {
  "Florești Central": "#4cc9f0",
  "Mărculești": "#8338ec",
  "Vărvăreuca": "#8ab17d",
  "Lunga": "#e76f51",
};

export const INAUGURATION_COST = 15;
