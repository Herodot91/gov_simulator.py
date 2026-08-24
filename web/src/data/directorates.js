// The app is built for real local-government users at each tier -- the
// metropolitan council, the prefecture, each municipal council, each
// district office -- to explore policy and project decisions the way
// their own administration is actually organized: into directorates
// (state/metro tier) and departments (municipal/district tier). Purely
// descriptive world-building, same non-interactive shape as the
// Technopolis Okrugs/FlorTech/AgroFlor/transit network -- no cost, no
// score effects.
// The prefecture is a real decision-making authority too, not just a
// directorates list -- its own policies, in effect regardless of whether
// the metropole has been established (same interactive shape as the
// METRO/MUNICIPALITY/DISTRICT_PROJECTS in projects.js).
export const PREFECTURE_POLICIES = [
  {
    id: "property_tax_reform",
    title: "Property Tax Reform",
    options: {
      A: ["Progressive property tax", { Governance: +5, Economy: +3 }, 10],
      B: ["Flat-rate property tax", { Economy: +5, Stability: -2 }, 5],
    },
    intl: "Ratepayers' associations watch the prefecture's tax-policy choice closely.",
  },
  {
    id: "egovernment",
    title: "State Digital Services Modernization",
    options: {
      A: ["Full e-government rollout", { Governance: +8 }, 20],
      B: ["Partial digitization", { Governance: +3 }, 8],
    },
    intl: "The Civil Registry directorate's paper backlog draws EU digitalization interest.",
  },
  {
    id: "civil_protection",
    title: "Civil Protection Budget",
    options: {
      A: ["Expand civil protection & emergency services", { Risk: -5, Stability: +3 }, 15],
      B: ["Maintain current staffing levels", {}, 0],
    },
    intl: "Regional emergency-response reviews recommend investment.",
  },
];

// Two real villages, both outside the metropole and the Technopolis
// Okrugs, whose territory has grown into a small town within the
// prefecture -- each with its own town council and interactive policies,
// structurally alongside the metropole (with its Technopolis Okrugs and
// suburbs) as a third kind of settlement the prefecture governs.
export const PREFECTURE_TOWNS = [
  {
    id: "cunicea",
    name: "Cunicea",
    radius: 1400,
    note:
      "A real village east of the metropole, its territory significantly expanded into a small " +
      "town within the prefecture, with its own town council. Not mono-industrial, unlike the " +
      "Technopolis Okrugs -- several factories across different sectors.",
    council: [
      { name: "Department of Local Administration", mandate: "Town council staff, civil records, local permits." },
      { name: "Department of Public Finance", mandate: "Local budget, taxation, procurement." },
    ],
  },
  {
    id: "raduleni",
    name: "Răduleni",
    radius: 1400,
    note:
      "A real village north of the metropole, its territory significantly expanded into a small " +
      "town within the prefecture, with its own town council. Not mono-industrial, unlike the " +
      "Technopolis Okrugs -- several factories across different sectors.",
    council: [
      { name: "Department of Local Administration", mandate: "Town council staff, civil records, local permits." },
      { name: "Department of Public Finance", mandate: "Local budget, taxation, procurement." },
    ],
  },
];

export const TOWN_POLICIES = {
  cunicea: [
    {
      id: "cunicea_infra",
      title: "Cunicea Town Infrastructure Investment",
      options: {
        A: ["Upgrade water & road infrastructure", { Economy: +4, Stability: +2 }, 12],
        B: ["Minor repairs only", { Economy: +1 }, 4],
      },
      intl: "Cunicea's town council petitions the prefecture for infrastructure funding.",
    },
  ],
  raduleni: [
    {
      id: "raduleni_infra",
      title: "Răduleni Town Infrastructure Investment",
      options: {
        A: ["Upgrade water & road infrastructure", { Economy: +4, Stability: +2 }, 12],
        B: ["Minor repairs only", { Economy: +1 }, 4],
      },
      intl: "Răduleni's town council petitions the prefecture for infrastructure funding.",
    },
  ],
};

// Factories across the metropole, the suburbs, and the Prefecture Towns --
// structural world-building, browsable via the Industries & Schools
// Dashboard (click a location to see its factories, their products, and
// their sector). Florești and Cunicea both also host precision-materials/
// electronics factories; Cunicea and Răduleni each supply components to
// one of the Technopolis Okrugs' own flagship companies, making them
// genuinely multi-industry, not mono-industrial like the Okrugs themselves.
export const FACTORIES = {
  "Florești Central": [
    { name: "ProMilk", sector: "Dairy & Food Processing", products: ["Pasteurized milk", "Yogurt", "Butter", "Cheese"] },
    { name: "FlorPan", sector: "Bakery & Food Processing", products: ["Bread", "Pastries", "Packaged baked goods"] },
    { name: "Alfa-Nistru Group", sector: "Food Processing", products: ["Packaged foods", "Confectionery", "Preserves"] },
    {
      name: "Florești Precision Components",
      sector: "Precision Materials & Electronics",
      products: ["Precision-machined parts", "Circuit assemblies", "Sensor housings"],
    },
    {
      name: "Florești HPP (HydroTechnique Ltd.)",
      sector: "Hydroelectric Power",
      products: ["Electricity generation", "Grid supply to Florești Central", "Răut river flow regulation"],
    },
  ],
  "Cunicea": [
    {
      name: "Cunicea AutoParts",
      sector: "Automotive Components (Sigma Motors supplier)",
      products: ["EV battery housings", "Chassis components", "Interior trim assemblies"],
    },
    {
      name: "Cunicea Precision Electronics",
      sector: "Precision Materials & Electronics",
      products: ["Printed circuit boards", "Sensor modules", "Wiring harnesses"],
    },
  ],
  "Răduleni": [
    {
      name: "Răduleni Heavy Components",
      sector: "Industrial Components (PHI supplier)",
      products: ["Hydraulic cylinders", "Gearbox housings", "Structural steel weldments"],
    },
  ],
  "Gura Căinarului": [
    { name: "Gura Căinarului Beverage Works", sector: "Beverages", products: ["Bottled water", "Soft drinks", "Fruit juices"] },
  ],
  "Gura Camencii": [
    { name: "Gura Camencii Bread Factory", sector: "Bakery", products: ["Bread", "Bread rolls", "Crackers"] },
  ],
  "Ghindești": [
    { name: "Ghindești Beer Factory", sector: "Brewing", products: ["Lager", "Craft ale", "Non-alcoholic beer"] },
    {
      name: "Ghindești Zahăr S.A.",
      sector: "Sugar Processing",
      products: ["Refined sugar", "Sugar beet pulp (animal feed)", "Molasses"],
    },
  ],
};

// Schools across the metropole and the Prefecture Towns -- "current"
// (locally-rooted) schools per municipality/town, plus a handful of
// fictional international schools reflecting the metropole's cosmopolitan,
// industrial/tech-hub character. Giorgetto Giugiaro (the real automotive
// designer's namesake) sits at Ciripcău deliberately, next to Sigma Motors.
export const SCHOOLS = {
  "Florești Central": [
    "Liceul Teoretic Ștefan cel Mare",
    "Școala Profesională din Florești",
    "Tokugawa International Japanese School",
    "Abdi İpekçi Türk Lisesi",
    "Fuad Seniora School",
    "Liceo Español Don Quijote",
    "Liceo Classico Italiano Giuseppe Verdi",
  ],
  "Mărculești": ["Liceul Teoretic Mărculești"],
  "Vărvăreuca": ["Liceul Agricol Vărvăreuca"],
  "Lunga": ["Școala de Arte și Meserii Lunga"],
  "Ghindești": ["Școala Profesională — Ghindești Branch"],
  "Gura Camencii": ["Școala Profesională — Gura Camencii Branch"],
  "Cunicea": ["Liceul Teoretic Cunicea"],
  "Răduleni": ["Liceul Teoretic Răduleni"],
  "Ciripcău": ["Liceo Tecnico Giorgetto Giugiaro"],
};

export const PREFECTURE_DIRECTORATES = [
  {
    name: "Directorate of Public Order & Civil Protection",
    mandate: "Policing coordination, emergency services, civil protection planning.",
  },
  {
    name: "Directorate of State Finance & Treasury Oversight",
    mandate: "State budget transfers, treasury oversight, fiscal compliance.",
  },
  {
    name: "Directorate of Public Administration & Legal Affairs",
    mandate: "Legal oversight of local acts, administrative litigation, the prefect's own staff.",
  },
  {
    name: "Directorate of Civil Registry & Documents",
    mandate: "Civil status records, identity documents, notarial oversight.",
  },
];

export const METRO_COUNCIL_DIRECTORATES = [
  {
    name: "Directorate of Urban Planning & Territorial Development",
    mandate: "Metropolitan masterplans (incl. the Florești Central CBD), zoning coordination across municipalities.",
  },
  {
    name: "Directorate of Transport & Infrastructure",
    mandate: "Trams, BRT, and commuter rail network planning; roads spanning more than one municipality.",
  },
  {
    name: "Directorate of Economic Development & Investment",
    mandate: "Investment promotion, the Technopolis Okrugs relationship, business permitting.",
  },
  {
    name: "Directorate of Environment & Sustainability",
    mandate: "Green tech policy, waste management, environmental compliance.",
  },
  {
    name: "Directorate of Education & Culture",
    mandate: "FlorTech and AgroFlor liaison, schools, cultural programming.",
  },
  {
    name: "Directorate of Health & Social Assistance",
    mandate: "Public health coordination, social services across municipalities.",
  },
];

// Each municipality's own two generic departments (finance, public
// services) plus one thematic department tied to its established identity.
export const MUNICIPALITY_DEPARTMENTS = {
  "Florești Central": [
    {
      name: "Department of Urban Development & CBD Management",
      mandate: "Central Business District oversight, Răut Plaza and civic-core development.",
    },
    { name: "Department of Municipal Finance", mandate: "Local budget, taxation, procurement." },
    { name: "Department of Public Services", mandate: "Waste collection, water/sewer, municipal maintenance." },
  ],
  "Mărculești": [
    {
      name: "Department of Transport & Airport Liaison",
      mandate: "Coordination with Mărculești International Airport, ground transit.",
    },
    { name: "Department of Municipal Finance", mandate: "Local budget, taxation, procurement." },
    { name: "Department of Public Services", mandate: "Waste collection, water/sewer, municipal maintenance." },
  ],
  "Vărvăreuca": [
    {
      name: "Department of Agriculture & Rural Development",
      mandate: "Farmland management, AgroFlor liaison, rural infrastructure.",
    },
    { name: "Department of Municipal Finance", mandate: "Local budget, taxation, procurement." },
    { name: "Department of Public Services", mandate: "Waste collection, water/sewer, municipal maintenance." },
  ],
  Lunga: [
    {
      name: "Department of Local Economy & Crafts",
      mandate: "Artisan Quarter support, local markets, small-business permitting.",
    },
    { name: "Department of Municipal Finance", mandate: "Local budget, taxation, procurement." },
    { name: "Department of Public Services", mandate: "Waste collection, water/sewer, municipal maintenance." },
  ],
};

// Districts sit below the municipal tier -- one lightweight civic office
// each, rather than a full directorate roster of their own.
export function districtOffice(municipality, district) {
  return {
    name: `${district} Civic Office`,
    mandate:
      `First-line public services liaison to the ${municipality} Municipal Council — ` +
      "local permits, records, and citizen requests.",
  };
}
