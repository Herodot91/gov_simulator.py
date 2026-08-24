// Each Technopolis Okrug's flagship company has a browsable product line --
// real-shaped catalogs (named models, a category, a one-line spec), not
// just the company name.
export const COMPANY_PRODUCTS = {
  "PHI — Prajila Heavy Industry": [
    { model: "PHI EX200", category: "Hydraulic Excavator", spec: "20-tonne class, 120 kW" },
    { model: "PHI EX450", category: "Hydraulic Excavator", spec: "45-tonne class, 260 kW" },
    { model: "PHI WL180", category: "Wheel Loader", spec: "3.0 m³ bucket, 130 kW" },
    { model: "PHI D8T", category: "Crawler Dozer", spec: "310 kW, semi-U blade" },
    { model: "PHI MG3000", category: "Motor Grader", spec: "3.7 m moldboard, 165 kW" },
    { model: "PHI CR650", category: "Crawler Crane", spec: "65-tonne lift capacity" },
    { model: "PHI RT100", category: "Rough-Terrain Crane", spec: "100-tonne lift capacity" },
    { model: "PHI HD400", category: "Rigid Dump Truck", spec: "40-tonne payload" },
    { model: "PHI ADT300", category: "Articulated Dump Truck", spec: "30-tonne payload, 6x6" },
    { model: "PHI SK150", category: "Skid-Steer Loader", spec: "1,500 kg rated operating capacity" },
  ],
  "Sigma Motors": [
    { model: "Sigma Vela", category: "Coupé", spec: "Electric, 420 km range, 0–100 km/h in 5.4s" },
    { model: "Sigma Brio", category: "Hatchback", spec: "Hybrid, 4.2 L/100km combined" },
    { model: "Sigma Brio-e", category: "Hatchback", spec: "Electric, 340 km range" },
    { model: "Sigma Terra", category: "Urban SUV", spec: "Electric, 460 km range, AWD" },
    { model: "Sigma Terra Hybrid", category: "Urban SUV", spec: "Plug-in hybrid, 65 km EV range" },
  ],
};
