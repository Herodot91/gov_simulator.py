// FlorTech — Florești University of Technology: a mass development that
// grows the real Școala Profesională din Florești (kept alongside, as
// vocational institutes) into a full university, with campuses spread
// across the metropole's municipalities, its suburbs, and the two
// Technopolis Okrugs. Structural world-building like the okrugs -- browsable,
// not simulated.
export const FLORTECH = {
  name: "FlorTech — Florești University of Technology",
  origin:
    "Grown out of the real Școala Profesională din Florești, whose vocational programs continue " +
    "alongside the new university rather than being replaced by it.",
  campuses: [
    {
      id: "central",
      name: "FlorTech Central Campus",
      location: "Florești Central — Politeh District",
      levels: ["BEng", "BSc", "MEng", "MSc", "PhD", "Postdoc"],
      faculties: [
        {
          name: "Faculty of Electrical, Electronics & Telecommunications",
          departments: ["Electrical Engineering", "Electronics & Microelectronics", "Telecommunications", "Programming & Cybersecurity"],
        },
        {
          name: "Faculty of Civil Engineering, Architecture & Urban Planning",
          departments: ["Construction Engineering", "Architecture", "Urban Planning"],
        },
        {
          name: "Faculty of Engineering Economics & Management",
          departments: ["Engineering Economics"],
        },
      ],
    },
    {
      id: "marculesti",
      name: "FlorTech Mărculești Campus",
      location: "Mărculești — Aviagorodok",
      levels: ["BEng", "BSc", "MEng", "MSc"],
      faculties: [
        {
          name: "Faculty of Transportation & Automation Engineering",
          departments: ["Transportation Engineering", "Automation & Computer Engineering"],
        },
      ],
    },
    {
      id: "varvareuca",
      name: "FlorTech Vărvăreuca Campus",
      location: "Vărvăreuca — Agricultural District",
      levels: ["BEng", "BSc", "MSc"],
      faculties: [
        {
          name: "Faculty of Natural Sciences & Process Engineering",
          departments: ["Applied Natural Sciences in Engineering", "Food Engineering"],
        },
      ],
    },
    {
      id: "lunga",
      name: "FlorTech Lunga Campus",
      location: "Lunga — Artisan Quarter",
      levels: ["BEng", "BSc", "MSc"],
      faculties: [
        {
          name: "Faculty of Design",
          departments: ["Industrial Design", "Interior Design", "Textile Engineering & Design"],
        },
      ],
    },
    {
      id: "prajila",
      name: "FlorTech Prajila Campus (PHI-sponsored)",
      location: "Prajila Technopolis Okrug",
      levels: ["BEng", "MEng", "MSc"],
      faculties: [
        {
          name: "Faculty of Mechanical & Heavy Industry Engineering",
          departments: ["Mechanical Engineering", "Industrial Engineering", "Construction Engineering", "Mining Engineering (incl. Oil & Gas)", "Robotics & Mechatronics"],
        },
      ],
    },
    {
      id: "ciripcau",
      name: "FlorTech Ciripcău Campus (Sigma Motors-sponsored)",
      location: "Ciripcău Technopolis Okrug",
      levels: ["BEng", "MEng", "MSc"],
      faculties: [
        {
          name: "Faculty of Automotive Engineering & Design",
          departments: ["Automotive Design", "Electrical Engineering (EV Systems)", "Robotics & Mechatronics"],
        },
      ],
    },
  ],
  vocationalInstitutes: [
    {
      id: "ghindesti",
      name: "Școala Profesională — Ghindești Branch",
      location: "Ghindești (suburb)",
      tracks: ["Electrical Technician", "Automotive Mechanic", "Welding & Metalwork", "CNC Machining"],
    },
    {
      id: "guracamencii",
      name: "Școala Profesională — Gura Camencii Branch",
      location: "Gura Camencii (suburb)",
      tracks: ["Construction Trades", "HVAC Technician", "Industrial Maintenance"],
    },
  ],
};

// Where each campus marker sits on the map -- offset a little from its
// municipality's/okrug's own anchor point so it doesn't sit exactly on top
// of that label. Same reference points as web/src/data/projects.js
// (Prajila/Ciripcău use their real village coordinates -- see
// public/data/floresti_localities.json).
const FLORESTI_PT = [47.8938318, 28.2996474];
const MARCULESTI_PT = [47.8693441, 28.2415422];
const VARVAREUCA_PT = [47.8798617, 28.3113869];
const LUNGA_PT = [47.8617078, 28.231765];
const PRAJILA_PT = [47.84049, 28.2100662];
const CIRIPCAU_PT = [47.9835655, 28.3808055];

export const FLORTECH_CAMPUS_LOCATIONS = {
  central: [FLORESTI_PT[0] + 0.0035, FLORESTI_PT[1] - 0.0035],
  marculesti: [MARCULESTI_PT[0] - 0.0035, MARCULESTI_PT[1] - 0.0035],
  varvareuca: [VARVAREUCA_PT[0] + 0.0035, VARVAREUCA_PT[1] - 0.0035],
  lunga: [LUNGA_PT[0], LUNGA_PT[1] + 0.006],
  prajila: [PRAJILA_PT[0] + 0.003, PRAJILA_PT[1] + 0.003],
  ciripcau: [CIRIPCAU_PT[0] + 0.003, CIRIPCAU_PT[1] + 0.003],
};
