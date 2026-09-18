// Default Integration Systems according to PRD & TalkFlow Specification §29.3 Architecture
export const INITIAL_INTEGRATIONS = [
  {
    id: "integ-1",
    name: "VICIdial Outbound Dialer REST API",
    category: "Dialer & Telephony",
    description:
      "Bi-directional lead status synchronization, list loading, and DNC suppression list updates.",
    status: "connected", // connected, disconnected, testing
    endpoint: "https://sbmed9.morpheus.cx/api/v1/dialer",
    lastSync: "Just now",
    syncSuccessRate: "100%",
  },
  {
    id: "integ-2",
    name: "SmartBrains BPO CRM Connector",
    category: "CRM Systems",
    description:
      "Push qualified Medicare lead data, caller recordings, transcript summaries, and verifier handoffs.",
    status: "connected",
    endpoint: "https://crm.smartbrainsbpo.com/api/medicare/leads",
    lastSync: "2 mins ago",
    syncSuccessRate: "99.8%",
  },
  {
    id: "integ-3",
    name: "Asterisk PBX SIP Trunking Gateway",
    category: "Voice Layer",
    description:
      "Outbound caller ID pool rotation, carrier trunk bridging, and inbound DID routing.",
    status: "connected",
    endpoint: "sip:trunk.smartbrains.telephony",
    lastSync: "Just now",
    syncSuccessRate: "99.9%",
  },
  {
    id: "integ-4",
    name: "EsperBots Telemetry Engine",
    category: "Reporting & Analytics",
    description:
      "Real-time call outcome telemetry, disposition analytics, and bot performance tracking API.",
    status: "connected",
    endpoint: "https://reporting.esperbots.com/api/dashboards",
    lastSync: "1 min ago",
    syncSuccessRate: "100%",
  },
  {
    id: "integ-5",
    name: "Lead Vendor Ingestion Webhook",
    category: "Lead Ingestion",
    description:
      "REST API & Webhook endpoint for automated Medicare lead imports from certified vendors.",
    status: "connected",
    endpoint: "https://api.talkflow.cx/v1/leads/import",
    lastSync: "5 mins ago",
    syncSuccessRate: "99.5%",
  },
  {
    id: "integ-6",
    name: "Salesforce / HubSpot CRM Relay",
    category: "CRM Systems",
    description:
      "Enterprise CRM connector for automated policy status updates and customer profile enrichment.",
    status: "connected",
    endpoint: "https://api.salesforce.com/services/data/v58.0",
    lastSync: "10 mins ago",
    syncSuccessRate: "99.2%",
  },
];

// Webhook Endpoints (PRD Section 9 & 10)
export const INITIAL_WEBHOOKS = [
  {
    id: "wh-1",
    name: "Medicare Lead Qualified Webhook",
    url: "https://crm.smartbrainsbpo.com/webhooks/medicare-qualified",
    events: ["lead.qualified", "verifier.transferred"],
    secret: "whsec_9812739a81b273...",
    status: "active",
    lastDelivery: "200 OK (24ms)",
    lastTriggered: "1 min ago",
  },
  {
    id: "wh-2",
    name: "Call Outcome & Recording Callback",
    url: "https://reporting.esperbots.com/api/webhooks/call-ended",
    events: ["call.ended", "recording.available", "disposition.updated"],
    secret: "whsec_1209381a7b6c5...",
    status: "active",
    lastDelivery: "200 OK (18ms)",
    lastTriggered: "3 mins ago",
  },
  {
    id: "wh-3",
    name: "Compliance & Opt-Out Event Stream",
    url: "https://compliance.smartbrainsbpo.com/api/opt-outs",
    events: ["consent.captured", "dnc.added", "opt_out.requested"],
    secret: "whsec_7781293a90b12...",
    status: "active",
    lastDelivery: "200 OK (15ms)",
    lastTriggered: "12 mins ago",
  },
];

// API Keys (PRD Section 8 & 9)
export const INITIAL_API_KEYS = [
  {
    id: "key-1",
    name: "ViciDial Production Sync Key",
    prefix: "sb_live_9812...",
    role: "Master Admin",
    created: "Jun 10, 2026",
    lastUsed: "Just now",
  },
  {
    id: "key-2",
    name: "Lead Vendor Automated Ingestion Key",
    prefix: "sb_live_4412...",
    role: "Lead Import Only",
    created: "Jun 12, 2026",
    lastUsed: "5 mins ago",
  },
];