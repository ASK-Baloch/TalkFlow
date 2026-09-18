"use client";

import React, { useState } from "react";
import {
  Plug,
  Plus,
  Search,
  CheckCircle2,
  AlertCircle,
  Clock,
  Key,
  Webhook,
  Database,
  Server,
  RefreshCw,
  Send,
  Sliders,
  Copy,
  Check,
  X,
  ExternalLink,
  ShieldCheck,
  Trash2,
  Activity,
  ChevronRight,
} from "lucide-react";
import {
  INITIAL_INTEGRATIONS,
  INITIAL_WEBHOOKS,
  INITIAL_API_KEYS,
} from "@/data";

export default function IntegrationsView({ initialAction, onActionChange }) {
  const [integrations, setIntegrations] = useState(INITIAL_INTEGRATIONS);
  const [webhooks, setWebhooks] = useState(INITIAL_WEBHOOKS);
  const [apiKeys, setApiKeys] = useState(INITIAL_API_KEYS);

  const [copiedKeyId, setCopiedKeyId] = useState(null);

  // Modals
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);
  const [selectedInteg, setSelectedInteg] = useState(null);

  const [isTestModalOpen, setIsTestModalOpen] = useState(false);
  const [testWebhook, setTestWebhook] = useState(null);
  const [testResponse, setTestResponse] = useState(null);
  const [isTesting, setIsTesting] = useState(false);

  const [isKeyModalOpen, setIsKeyModalOpen] = useState(initialAction === "new");

  // Re-open the modal if initialAction changes to "new" after mount
  // (adjusting state during render instead of in an effect).
  const [prevInitialAction, setPrevInitialAction] = useState(initialAction);
  if (initialAction !== prevInitialAction) {
    setPrevInitialAction(initialAction);
    if (initialAction === "new") {
      setIsKeyModalOpen(true);
    }
  }

  const handleOpenKeyModal = () => {
    setIsKeyModalOpen(true);
    if (onActionChange) onActionChange("new");
  };

  const handleCloseKeyModal = () => {
    setIsKeyModalOpen(false);
    if (onActionChange) onActionChange(null);
  };

  const [newKeyName, setNewKeyName] = useState("");
  const [newKeyRole, setNewKeyRole] = useState("Lead Import Only");

  // Toggle Integration Status
  const toggleIntegration = (id) => {
    setIntegrations((prev) =>
      prev.map((item) =>
        item.id === id
          ? {
              ...item,
              status: item.status === "connected" ? "disconnected" : "connected",
            }
          : item
      )
    );
  };

  // Copy Secret / API Key
  const handleCopy = (text, id) => {
    navigator.clipboard?.writeText(text);
    setCopiedKeyId(id);
    setTimeout(() => setCopiedKeyId(null), 2000);
  };

  // Run Test Webhook Payload (PRD Section 10)
  const handleRunTestWebhook = (wh) => {
    setTestWebhook(wh);
    setTestResponse(null);
    setIsTestModalOpen(true);
  };

  const executeWebhookTest = () => {
    setIsTesting(true);
    setTimeout(() => {
      setIsTesting(false);
      setTestResponse({
        status: 200,
        statusText: "OK",
        latency: "22ms",
        payload: {
          event: "lead.qualified",
          timestamp: new Date().toISOString(),
          campaign: "Med Fronter",
          leadId: "4232558801",
          disposition: "SALE",
          verifier: "Adriana",
          recordingUrl:
            "https://sbmed9.morpheus.cx/recordings/2026/09/10/call-9812.mp3",
        },
      });
    }, 800);
  };

  // Create API Key (PRD Section 8)
  const handleCreateApiKey = (e) => {
    e.preventDefault();
    if (!newKeyName.trim()) return;

    const created = {
      id: `key-${Date.now()}`,
      name: newKeyName.trim(),
      prefix: `sb_live_${Math.floor(1000 + Math.random() * 9000)}...`,
      role: newKeyRole,
      created: "Just now",
      lastUsed: "Never",
    };

    setApiKeys((prev) => [created, ...prev]);
    setNewKeyName("");
    handleCloseKeyModal();
  };

  return (
    <div className="flex flex-col gap-6 p-4 sm:p-6 text-neutral-900 dark:text-neutral-100 font-sans min-h-screen bg-neutral-50 dark:bg-[#050505] transition-colors duration-200">
      {/* 1. Header & PRD Subtitle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-200 dark:border-neutral-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-white tracking-tight">
              Integrations & Webhook Management
            </h1>
            <span className="rounded-full bg-blue-100 dark:bg-blue-600/20 border border-blue-300 dark:border-blue-500/40 px-2.5 py-0.5 text-[10px] font-bold text-blue-700 dark:text-blue-400">
              PRD Section 9 & 10
            </span>
          </div>
          <p className="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
            Connect ViciDial API, SmartBrains CRM (FR-13), lead vendor endpoints, and real-time webhook callback streams.
          </p>
        </div>

        {/* Action Button */}
        <button
          type="button"
          onClick={handleOpenKeyModal}
          className="inline-flex items-center gap-1.5 rounded-md bg-blue-600 px-4 py-2 text-xs font-bold text-white shadow-sm transition-colors hover:bg-blue-700"
        >
          <Key className="h-4 w-4" />
          <span>Create API Key</span>
        </button>
      </div>

      {/* 2. Overview KPI Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs">
          <div className="flex items-center justify-between text-xs font-semibold text-neutral-500 dark:text-neutral-400">
            <span>Connected Systems</span>
            <Plug className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div className="text-2xl font-extrabold text-neutral-900 dark:text-white mt-1">
            {integrations.filter((i) => i.status === "connected").length} / {integrations.length}
          </div>
          <div className="text-[10px] text-neutral-500 mt-1">
            ViciDial, CRM, Telemetry active
          </div>
        </div>

        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs">
          <div className="flex items-center justify-between text-xs font-semibold text-neutral-500 dark:text-neutral-400">
            <span>Active Webhook Streams</span>
            <Webhook className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          </div>
          <div className="text-2xl font-extrabold text-purple-600 dark:text-purple-400 mt-1">
            {webhooks.length} Active
          </div>
          <div className="text-[10px] text-neutral-500 mt-1">
            Event-triggered callbacks
          </div>
        </div>

        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs">
          <div className="flex items-center justify-between text-xs font-semibold text-neutral-500 dark:text-neutral-400">
            <span>24h Delivery Success</span>
            <Activity className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1">
            99.8%
          </div>
          <div className="text-[10px] text-neutral-500 mt-1">
            Auto-retry policy active
          </div>
        </div>

        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs">
          <div className="flex items-center justify-between text-xs font-semibold text-neutral-500 dark:text-neutral-400">
            <span>Active API Keys</span>
            <Key className="h-4 w-4 text-amber-600 dark:text-amber-400" />
          </div>
          <div className="text-2xl font-extrabold text-amber-600 dark:text-amber-400 mt-1">
            {apiKeys.length} Keys
          </div>
          <div className="text-[10px] text-neutral-500 mt-1">
            Role-restricted access
          </div>
        </div>
      </div>

      {/* 3. Integration Cards Grid */}
      <div>
        <h2 className="text-sm font-bold text-neutral-900 dark:text-white mb-3 flex items-center gap-2">
          <Server className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          <span>Telephony, CRM & Analytics Integrations (PRD Section 9)</span>
        </h2>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {integrations.map((item) => (
            <div
              key={item.id}
              className={`rounded-xl border p-5 shadow-xs transition-colors flex flex-col justify-between ${
                item.status === "connected"
                  ? "border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d]"
                  : "border-neutral-200 dark:border-neutral-800/60 bg-neutral-50 dark:bg-[#0a0a0c] opacity-80"
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[10px] font-bold tracking-wider text-neutral-500 dark:text-neutral-400 uppercase">
                    {item.category}
                  </span>
                  {item.status === "connected" ? (
                    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 dark:bg-emerald-500/10 border border-emerald-300 dark:border-emerald-500/30 px-2 py-0.5 text-[10px] font-bold text-emerald-700 dark:text-emerald-400">
                      <CheckCircle2 className="h-3 w-3" /> Connected
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 rounded-full bg-neutral-200 dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-700 px-2 py-0.5 text-[10px] font-bold text-neutral-600 dark:text-neutral-400">
                      Disconnected
                    </span>
                  )}
                </div>

                <h3 className="text-base font-bold text-neutral-900 dark:text-white">{item.name}</h3>
                <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-1 line-clamp-2">
                  {item.description}
                </p>

                <div className="mt-4 rounded-md border border-neutral-200 dark:border-neutral-800 bg-neutral-100 dark:bg-[#161618] p-2 font-mono text-[11px] text-neutral-800 dark:text-neutral-300 truncate">
                  {item.endpoint}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-neutral-200 dark:border-neutral-800/80 flex items-center justify-between text-xs">
                <span className="text-[11px] text-neutral-500">
                  Last Sync: <strong className="text-neutral-700 dark:text-neutral-300">{item.lastSync}</strong>
                </span>
                <button
                  type="button"
                  onClick={() => toggleIntegration(item.id)}
                  className={`rounded-md px-3 py-1 text-xs font-bold transition-colors ${
                    item.status === "connected"
                      ? "border border-neutral-300 dark:border-neutral-700 bg-neutral-100 dark:bg-neutral-900 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-800 hover:text-neutral-900 dark:hover:text-white"
                      : "bg-blue-600 text-white hover:bg-blue-700"
                  }`}
                >
                  {item.status === "connected" ? "Disconnect" : "Connect"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 4. Real-time Webhook Callbacks Table */}
      <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <div>
            <h2 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <Webhook className="h-4 w-4 text-purple-600 dark:text-purple-400" />
              <span>Real-Time Webhook Callback Subscriptions (PRD Section 10)</span>
            </h2>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">
              Event notifications pushed automatically when leads qualify or verifiers take handoffs.
            </p>
          </div>
        </div>

        <div className="w-full overflow-x-auto rounded-lg border border-neutral-200 dark:border-neutral-800">
          <table className="w-full min-w-[900px] border-collapse text-xs text-left">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-800 bg-neutral-100 dark:bg-neutral-950 text-neutral-600 dark:text-neutral-400 font-bold uppercase tracking-wider text-[11px]">
                <th className="px-4 py-3">Webhook Name</th>
                <th className="px-4 py-3">Endpoint URL</th>
                <th className="px-4 py-3">Subscribed Events</th>
                <th className="px-4 py-3 text-center">Status</th>
                <th className="px-4 py-3 text-center">Last Delivery</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/70 bg-white dark:bg-[#0d0d0d]">
              {webhooks.map((wh) => (
                <tr key={wh.id} className="transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900/50">
                  <td className="px-4 py-3.5 font-bold text-neutral-900 dark:text-white">{wh.name}</td>
                  <td className="px-4 py-3.5 font-mono text-neutral-600 dark:text-neutral-300 max-w-[220px] truncate">
                    {wh.url}
                  </td>
                  <td className="px-4 py-3.5">
                    <div className="flex flex-wrap gap-1">
                      {wh.events.map((ev) => (
                        <span
                          key={ev}
                          className="rounded-md bg-purple-100 dark:bg-purple-950/60 border border-purple-300 dark:border-purple-800/50 px-2 py-0.5 text-[10px] font-bold text-purple-700 dark:text-purple-300"
                        >
                          {ev}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3.5 text-center">
                    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 dark:bg-emerald-500/10 border border-emerald-300 dark:border-emerald-500/30 px-2.5 py-0.5 text-[10px] font-bold text-emerald-700 dark:text-emerald-400">
                      <CheckCircle2 className="h-3 w-3" /> Active
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-center font-mono font-bold text-emerald-600 dark:text-emerald-400">
                    {wh.lastDelivery}
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <button
                      type="button"
                      onClick={() => handleRunTestWebhook(wh)}
                      className="inline-flex items-center gap-1 rounded-md border border-neutral-300 dark:border-neutral-700 bg-neutral-100 dark:bg-neutral-900 px-3 py-1 text-xs font-semibold text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-800 hover:text-neutral-900 dark:hover:text-white"
                    >
                      <Send className="h-3 w-3 text-blue-600 dark:text-blue-400" />
                      <span>Test Payload</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. API Keys & Credentials Manager */}
      <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <div>
            <h2 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <Key className="h-4 w-4 text-amber-600 dark:text-amber-400" />
              <span>API Credentials & Access Control (PRD Section 8 & 9)</span>
            </h2>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">
              Role-restricted API keys for automated lead ingestion, dialer synchronization, and CRM webhooks.
            </p>
          </div>
        </div>

        <div className="w-full overflow-x-auto rounded-lg border border-neutral-200 dark:border-neutral-800">
          <table className="w-full min-w-[700px] border-collapse text-xs text-left">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-800 bg-neutral-100 dark:bg-neutral-950 text-neutral-600 dark:text-neutral-400 font-bold uppercase tracking-wider text-[11px]">
                <th className="px-4 py-3">Key Name</th>
                <th className="px-4 py-3">Key Prefix</th>
                <th className="px-4 py-3">Role Scope</th>
                <th className="px-4 py-3">Created</th>
                <th className="px-4 py-3">Last Used</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/70 bg-white dark:bg-[#0d0d0d]">
              {apiKeys.map((k) => (
                <tr key={k.id} className="transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900/50">
                  <td className="px-4 py-3.5 font-bold text-neutral-900 dark:text-white">{k.name}</td>
                  <td className="px-4 py-3.5 font-mono text-amber-600 dark:text-amber-400 font-bold">
                    {k.prefix}
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="rounded-full bg-blue-100 dark:bg-blue-950/60 border border-blue-300 dark:border-blue-800/50 px-2.5 py-0.5 text-[10px] font-bold text-blue-700 dark:text-blue-300">
                      {k.role}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-neutral-500 dark:text-neutral-400">{k.created}</td>
                  <td className="px-4 py-3.5 text-neutral-700 dark:text-neutral-300 font-medium">
                    {k.lastUsed}
                  </td>
                  <td className="px-4 py-3.5 text-right">
                    <button
                      type="button"
                      onClick={() =>
                        setApiKeys((prev) => prev.filter((item) => item.id !== k.id))
                      }
                      className="text-neutral-400 hover:text-rose-600 dark:hover:text-rose-400 p-1 transition-colors"
                      title="Revoke API Key"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 6. CREATE API KEY MODAL (PRD Section 8) */}
      {isKeyModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#121214] p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-3 mb-4">
              <h3 className="text-base font-bold text-neutral-900 dark:text-white">Create New API Key</h3>
              <button
                onClick={handleCloseKeyModal}
                className="text-neutral-400 hover:text-neutral-700 dark:hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleCreateApiKey} className="flex flex-col gap-4 text-xs">
              <div>
                <label className="block font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                  Key Description / Application Name
                </label>
                <input
                  type="text"
                  required
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  placeholder="e.g. Lead Vendor Ingestion Key"
                  className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-2 text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                />
              </div>

              <div>
                <label className="block font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                  Role Permission Scope (PRD Section 4)
                </label>
                <select
                  value={newKeyRole}
                  onChange={(e) => setNewKeyRole(e.target.value)}
                  className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] px-3 py-2 text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                >
                  <option value="Lead Import Only">Lead Import Only</option>
                  <option value="Campaign Manager">Campaign Manager</option>
                  <option value="Reporting User">Reporting User</option>
                  <option value="Master Admin">Master Admin</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-neutral-200 dark:border-neutral-800 mt-2">
                <button
                  type="button"
                  onClick={handleCloseKeyModal}
                  className="rounded-md px-3 py-1.5 text-neutral-500 hover:text-neutral-800 dark:text-neutral-400 dark:hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-md bg-blue-600 px-4 py-1.5 font-bold text-white hover:bg-blue-700"
                >
                  Generate Key
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 7. TEST WEBHOOK PAYLOAD MODAL (PRD Section 10) */}
      {isTestModalOpen && testWebhook && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs">
          <div className="w-full max-w-lg rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#121214] p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <Send className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                <h3 className="text-base font-bold text-neutral-900 dark:text-white">
                  Test Webhook Event Trigger
                </h3>
              </div>
              <button
                onClick={() => setIsTestModalOpen(false)}
                className="text-neutral-400 hover:text-neutral-700 dark:hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="flex flex-col gap-3 text-xs">
              <div>
                <span className="text-neutral-500 dark:text-neutral-400">Target Endpoint:</span>
                <div className="mt-1 rounded-md border border-neutral-200 dark:border-neutral-800 bg-neutral-100 dark:bg-[#18181b] p-2 font-mono text-[11px] text-neutral-900 dark:text-white">
                  {testWebhook.url}
                </div>
              </div>

              {!testResponse && (
                <button
                  type="button"
                  disabled={isTesting}
                  onClick={executeWebhookTest}
                  className="w-full rounded-md bg-blue-600 py-2.5 font-bold text-white hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Send className={`h-3.5 w-3.5 ${isTesting ? "animate-pulse" : ""}`} />
                  <span>{isTesting ? "Sending Test Payload..." : "Send Test Payload (lead.qualified)"}</span>
                </button>
              )}

              {testResponse && (
                <div className="flex flex-col gap-2 rounded-lg border border-emerald-300 dark:border-emerald-900/60 bg-emerald-50 dark:bg-emerald-950/20 p-3 mt-2">
                  <div className="flex items-center justify-between border-b border-emerald-200 dark:border-emerald-900/60 pb-2">
                    <span className="font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                      <CheckCircle2 className="h-4 w-4" /> Response: {testResponse.status} {testResponse.statusText}
                    </span>
                    <span className="text-[10px] text-emerald-600 dark:text-emerald-500 font-mono">
                      {testResponse.latency}
                    </span>
                  </div>
                  <pre className="mt-1 overflow-x-auto rounded-md bg-neutral-100 dark:bg-[#0a0a0c] p-2.5 font-mono text-[10px] text-neutral-800 dark:text-neutral-300">
                    {JSON.stringify(testResponse.payload, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <div className="border-t border-neutral-200 dark:border-neutral-800 pt-4 mt-4 text-right">
              <button
                type="button"
                onClick={() => setIsTestModalOpen(false)}
                className="rounded-md bg-neutral-200 dark:bg-neutral-800 px-4 py-1.5 font-bold text-neutral-800 dark:text-white hover:bg-neutral-300 dark:hover:bg-neutral-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
