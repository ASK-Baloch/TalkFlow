export const ROUTE_NAMES = {
  DASHBOARD: "dashboard",
  CAMPAIGNS: "campaigns",
  SCRIPTS: "scripts",
  SYSTEM: "system",
  INTEGRATIONS: "integrations",
  ANALYTICS: "analytics",
  REPORTS: "analytics",
  RECORDING: "recording",
  AUDIT_LOGS: "audit_logs",
  USERS: "users",
  SETTINGS: "settings",
  LOGIN: "login",
};

export const STATUS_OPTIONS = {
  ACTIVE: "active",
  INACTIVE: "inactive",
  PAUSED: "paused",
  DRAFT: "draft",
  PENDING_REVIEW: "pending_review",
  ARCHIVED: "archived",
};

export const CAMPAIGN_STATUSES = [
  { value: "all", label: "All Statuses" },
  { value: "active", label: "Active" },
  { value: "paused", label: "Paused" },
  { value: "draft", label: "Draft" },
];

export const DISPOSITION_TYPES = [
  "SALE",
  "CLBK",
  "DNC",
  "DNQ",
  "NI",
  "NP",
  "RAXFER",
  "A",
  "DAIR",
  "DC",
  "HP",
  "RI",
];

export const DEFAULT_PAGINATION_LIMIT = 10000;
