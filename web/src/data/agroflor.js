// AgroFlor — Florești University of Agricultural Sciences and Technologies:
// grew out of Scenario 5's investment in a Vărvăreuca agricultural college
// into a full metropole-wide university, with campuses across all 4
// municipalities and both suburbs (not the Technopolis Okrugs -- those stay
// single-company, not academic). Structural world-building like FlorTech --
// browsable, not simulated. Each campus also lists its research centers/labs
// alongside its faculties/departments.
export const AGROFLOR = {
  name: "AgroFlor — Florești University of Agricultural Sciences and Technologies",
  origin:
    "Grew out of the investment in a Vărvăreuca agricultural college into a full " +
    "metropole-wide university, with campuses across every municipality and both suburbs.",
  campuses: [
    {
      id: "varvareuca",
      name: "AgroFlor Vărvăreuca Campus",
      location: "Vărvăreuca — Agricultural District",
      levels: ["BSc", "MSc", "PhD", "Postdoc"],
      faculties: [
        {
          name: "Faculty of Agronomy & Crop Sciences",
          departments: ["Agronomy", "Horticulture", "Crop Engineering"],
        },
        {
          name: "Faculty of Genetics & Biotechnology",
          departments: ["Genetics & Plant Breeding", "Biotechnology"],
        },
      ],
      researchCenters: ["Crop Genetics Research Center", "Soil & Water Sustainability Lab"],
    },
    {
      id: "central",
      name: "AgroFlor Central Campus",
      location: "Florești Central — Politeh District",
      levels: ["BSc", "MSc", "PhD", "Postdoc"],
      faculties: [
        {
          name: "Faculty of Agricultural Economics & Rural Development",
          departments: ["Agricultural Economics", "Sustainable Development", "Rural Planning"],
        },
      ],
      researchCenters: ["Agri-Economics Policy Center"],
    },
    {
      id: "marculesti",
      name: "AgroFlor Mărculești Campus",
      location: "Mărculești — Aviagorodok",
      levels: ["BEng", "BSc", "MSc"],
      faculties: [
        {
          name: "Faculty of Agricultural Machinery & Agritech",
          departments: ["Agricultural Machinery Engineering", "Agritech & Precision Farming"],
        },
      ],
      researchCenters: ["Agritech & Precision Farming Lab"],
    },
    {
      id: "lunga",
      name: "AgroFlor Lunga Campus",
      location: "Lunga — Artisan Quarter",
      levels: ["BSc", "MSc", "PhD"],
      faculties: [
        {
          name: "Faculty of Veterinary Medicine & Animal Husbandry",
          departments: ["Animal Husbandry", "Veterinary Medicine"],
        },
      ],
      researchCenters: ["Animal Health Research Lab"],
    },
    {
      id: "ghindesti",
      name: "AgroFlor Ghindești Campus",
      location: "Ghindești (suburb)",
      levels: ["BSc", "MSc"],
      faculties: [
        {
          name: "Faculty of Food Engineering & Natural Sciences",
          departments: ["Food Engineering", "Biology", "Chemistry"],
        },
      ],
      researchCenters: ["Food Quality & Safety Lab"],
    },
    {
      id: "guracamencii",
      name: "AgroFlor Gura Camencii Campus",
      location: "Gura Camencii (suburb)",
      levels: ["BSc", "MSc"],
      faculties: [
        {
          name: "Faculty of Applied Sciences",
          departments: ["Physics", "Informatics & Applied Mathematics in Agriculture"],
        },
      ],
      researchCenters: ["Agri-Informatics Lab"],
    },
  ],
};

// AgroFlor campuses use their own offsets (opposite side from FlorTech's, at
// each shared municipality) so the two universities' markers don't stack.
// Ghindești/Gura Camencii use their real suburb coordinates (see
// public/data/floresti_localities.json).
const FLORESTI_PT = [47.8938318, 28.2996474];
const MARCULESTI_PT = [47.8693441, 28.2415422];
const VARVAREUCA_PT = [47.8798617, 28.3113869];
const LUNGA_PT = [47.8617078, 28.231765];
const GHINDESTI_PT = [47.8623849, 28.3870348];
const GURACAMENCII_PT = [47.8901159, 28.3553067];

export const AGROFLOR_CAMPUS_LOCATIONS = {
  varvareuca: [VARVAREUCA_PT[0] - 0.0045, VARVAREUCA_PT[1] + 0.0045],
  central: [FLORESTI_PT[0] - 0.0045, FLORESTI_PT[1] + 0.0045],
  marculesti: [MARCULESTI_PT[0] + 0.0045, MARCULESTI_PT[1] + 0.0045],
  lunga: [LUNGA_PT[0], LUNGA_PT[1] - 0.006],
  ghindesti: [GHINDESTI_PT[0] + 0.003, GHINDESTI_PT[1] - 0.003],
  guracamencii: [GURACAMENCII_PT[0] + 0.003, GURACAMENCII_PT[1] - 0.003],
};
