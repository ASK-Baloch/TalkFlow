export const ALL_DISPOSITIONS = [
  "A",
  "CLBK",
  "DAIR",
  "DAIR 2",
  "DC",
  "DNC",
  "DNQ",
  "HP",
  "INITIATED",
  "NI",
  "NP",
  "RAXFER",
  "RI",
  "SALE",
  "SALE Failed",
];

export const INITIAL_SELECTED_DISPOSITIONS = [
  "DNC",
  "DNQ",
  "CLBK",
  "SALE",
  "DAIR",
  "RAXFER",
  "NP",
];

export const LIMIT_OPTIONS = ["1,000", "5,000", "10,000", "25,000", "50,000", "100,000"];
export const TYPE_OPTIONS = ["All", "HI", "MED", "MVA", "Inbound", "Outbound"];
export const DIALER_OPTIONS = [
  "All",
  "ViciDial Primary",
  "ViciDial Secondary",
  "Dialer 01",
  "Dialer 02",
];
export const SERVER_OPTIONS = [
  "All",
  "US-East-1 (Primary)",
  "US-West-2 (Backup)",
  "Server 01",
  "Server 02",
];

export const DATE_PRESETS = [
  { label: "Last 24 hours", subtext: "Sep 9, 2026 22:05 — Sep 10, 2026 22:05" },
  { label: "Today", subtext: "Sep 10, 2026 00:00 — Sep 10, 2026 23:59" },
  { label: "Yesterday", subtext: "Sep 9, 2026 00:00 — Sep 9, 2026 23:59" },
  { label: "Last 7 days", subtext: "Sep 3, 2026 00:00 — Sep 10, 2026 22:05" },
  { label: "Last 30 days", subtext: "Aug 11, 2026 00:00 — Sep 10, 2026 22:05" },
];