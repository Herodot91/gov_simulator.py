export const SCENARIOS = [
  {
    title: "Florești Metropole Administration Reform",
    options: {
      A: ["Keep centralized prefecture control", { Governance: -5, Risk: +5 }, 10],
      B: ["Establish Florești Metropole (mixed decentralization)", { Governance: +10, Stability: +5 }, 20],
    },
    intl: "France's Ministry of the Interior offers a prefecture-partnership model.",
  },
  {
    title: "Create Technical University in Bender",
    options: {
      A: ["Skip investment", { Economy: -5 }, 0],
      B: ["IT faculty only", { Economy: +5 }, 15],
      C: ["Full technical university", { Economy: +10, Governance: +5 }, 25],
    },
    intl: "Russia warns against outside influence.",
  },
  {
    title: "Digital Justice & Procurement Reform",
    options: {
      A: ["Delay reform", { Governance: -5 }, 0],
      B: ["Implement transparency tools", { Governance: +10, Risk: -5 }, 15],
    },
    intl: "EU praises Moldova's rule of law improvement.",
  },
  {
    title: "Budget Allocation: Green Tech Factories",
    options: {
      A: ["One per region", { Economy: +5 }, 20],
      B: ["Ignore sector", { Economy: -5 }, 0],
    },
    intl: "UN welcomes clean tech expansion.",
  },
  {
    title: "Education: New Agricultural Universities",
    options: {
      A: ["EU model in Taul, Karmanovo", { Economy: +5, Stability: +5 }, 25],
      B: ["Keep colleges as-is", { Economy: -5 }, 0],
    },
    intl: "Foreign students show interest in Moldova.",
  },
];

// Ambient events that fire on their own once the clock is live, independent of
// the scripted policy decisions above — this is what makes the world keep
// moving in real time even while the player is deliberating.
export const RANDOM_EVENTS = [
  ["Foreign Direct Investment Surge", { Economy: +3 }, "Investors from the EU pour capital into Florești."],
  ["Border Smuggling Incident", { Risk: +4, Stability: -2 }, "Customs intercepts a smuggling ring; public trust shaken."],
  ["Anti-Corruption Audit Released", { Governance: +3, Risk: -2 }, "An independent audit boosts transparency confidence."],
  ["Energy Price Spike", { Economy: -4, Stability: -1 }, "Regional energy costs surge, straining households."],
  ["Diaspora Remittance Boom", { Economy: +2, Stability: +1 }, "The diaspora sends record remittances home."],
  ["Protest Over Public Services", { Stability: -3, Governance: -1 }, "Citizens rally over slow service delivery."],
  ["EU Grant Approved", { Economy: +4, Governance: +2 }, "Brussels approves a new development grant."],
  ["Cyberattack on Government Systems", { Risk: +5, Governance: -3 }, "A cyberattack disrupts digital services."],
  ["Bumper Harvest", { Economy: +3, Stability: +2 }, "Agricultural output exceeds expectations."],
  ["Regional Tension Escalates", { Risk: +3, Stability: -2 }, "Cross-border tensions raise local anxiety."],
];

export const BASE_SCORES = { Governance: 50, Economy: 50, Stability: 50, Risk: 50 };
