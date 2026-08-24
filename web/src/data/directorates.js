// The app is built for real local-government users at each tier -- the
// metropolitan council, the prefecture, each municipal council, each
// district office -- to explore policy and project decisions the way
// their own administration is actually organized: into directorates
// (state/metro tier) and departments (municipal/district tier). Purely
// descriptive world-building, same non-interactive shape as the
// Technopolis Okrugs/FlorTech/AgroFlor/transit network -- no cost, no
// score effects.
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
