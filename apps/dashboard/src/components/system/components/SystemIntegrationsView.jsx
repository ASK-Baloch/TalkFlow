"use client";

import { ArrowLeft, CheckCircle2, Plug, RefreshCw, KeyRound, Send, Zap, XCircle } from "lucide-react";

export default function SystemIntegrationsView({
  integrations,
  onToggleIntegration,
  failureQueue,
  onRetryPush,
  webhooks,
  onTestWebhook,
  onOpenCreateKey,
}) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-4">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => onToggleIntegration(null)}
            className="p-1.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-neutral-600 hover:text-neutral-900"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            <h2 className="text-xl font-bold text-neutral-900 dark:text-white">
              External Service Integrations
            </h2>
            <p className="text-xs text-neutral-500">
              Carrier, AI, Analytics, and Webhook provider integrations with API key management.
            </p>
          </div>
        </div>
      </div>

      {/* Connected Integrations Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {integrations.map((item) => (
          <div
            key={item.id}
            className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4"
          >
            <div className="flex items-center justify-between">
              <IconDynamic name={item.name} />
              <span
                className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[10px] font-bold border ${
                  item.status === "connected"
                    ? "bg-emerald-100 text-emerald-700 border-emerald-300 dark:bg-emerald-950/50 dark:text-emerald-400 dark:border-emerald-800"
                    : "bg-neutral-100 text-neutral-600 border-neutral-300 dark:bg-neutral-800 dark:text-neutral-400"
                }`}
              >
                {item.status === "connected" ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                {item.status.toUpperCase()}
              </span>
            </div>
            <div>
              <h3 className="text-sm font-bold text-neutral-900 dark:text-white">{item.name}</h3>
              <p className="text-xs text-neutral-500 leading-relaxed mt-1">{item.description}</p>
            </div>
            <div className="flex flex-col gap-1.5 text-[11px] bg-neutral-50 dark:bg-[#121215] p-3 rounded-lg border border-neutral-200 dark:border-neutral-800">
              <div className="flex justify-between">
                <span className="text-neutral-500">Scope / Type:</span>
                <span className="font-semibold">{item.scope}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-500">Region:</span>
                <span className="font-semibold">{item.region}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-500">API Version:</span>
                <span className="font-mono font-semibold">{item.apiVersion}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-500">Enabled On:</span>
                <span className="font-mono text-neutral-400">{item.enabledAt}</span>
              </div>
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-neutral-200 dark:border-neutral-800">
              <span className="text-[11px] text-neutral-500">
                Coordinator: <strong className="text-neutral-800 dark:text-neutral-200">{item.coordinator}</strong>
              </span>
              <button
                type="button"
                onClick={() => onToggleIntegration(item.id)}
                className={`text-[11px] font-bold px-3 py-1.5 rounded-md ${
                  item.status === "connected"
                    ? "bg-neutral-800 text-white hover:bg-neutral-700"
                    : "bg-emerald-600 text-white hover:bg-emerald-700"
                }`}
              >
                {item.status === "connected" ? "Disconnect" : "Reconnect"}
              </button>
            </div>
          </div>
        ))}

        {/* API Keys Card */}
        <div className="rounded-xl border border-dashed border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-[#0d0d0d] p-5 flex flex-col justify-center items-center text-center gap-3">
          <div className="flex items-center gap-2 text-sm font-bold text-neutral-800 dark:text-white">
            <KeyRound className="h-4 w-4 text-blue-500" />
            <span>API Keys & Secrets Manager</span>
          </div>
          <p className="text-xs text-neutral-500">Create scoped live/public API keys for external data feeds.</p>
          <button
            type="button"
            onClick={onOpenCreateKey}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            <KeyRound className="h-4 w-4" />
            Create API Key
          </button>
        </div>
      </div>

      {/* Failure Queue */}
      <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
        <h3 className="text-sm font-bold mb-4 flex items-center gap-2">
          <RefreshCw className="h-4 w-4 text-rose-500" />
          Integration Push Failure Queue
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px] text-xs text-left border-collapse">
            <thead>
              <tr className="text-neutral-500 uppercase text-[11px] border-b border-neutral-200 dark:border-neutral-800">
                <th className="py-2.5 px-3">Message ID</th>
                <th className="py-2.5 px-3">Target / Endpoint</th>
                <th className="py-2.5 px-3">Attempts</th>
                <th className="py-2.5 px-3">Last Attempt</th>
                <th className="py-2.5 px-3">Failure Reason</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/60">
              {failureQueue.map((item) => (
                <tr key={item.id}>
                  <td className="py-3 px-3 font-mono font-bold text-blue-600 dark:text-blue-400">{item.id}</td>
                  <td className="py-3 px-3 font-semibold max-w-xs truncate">{item.target}</td>
                  <td className="py-3 px-3 font-mono text-neutral-500">{item.attempts}</td>
                  <td className="py-3 px-3 font-mono text-neutral-500">{item.lastAttemptAt}</td>
                  <td className="py-3 px-3 text-rose-600 dark:text-rose-400 font-semibold max-w-xs truncate">{item.reason}</td>
                  <td className="py-3 px-3 text-right">
                    <button
                      type="button"
                      onClick={() => onRetryPush(item.id)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-bold text-blue-700 bg-blue-50 rounded border border-blue-200 hover:bg-blue-100"
                    >
                      <RefreshCw className="h-3 w-3" />
                      Retry Push
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Webhooks Table */}
      <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
        <h3 className="text-sm font-bold mb-4">Registered Webhooks & Event Subscriptions</h3>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[600px] text-xs text-left border-collapse">
            <thead>
              <tr className="text-neutral-500 uppercase text-[11px] border-b border-neutral-200 dark:border-neutral-800">
                <th className="py-2.5 px-3">Webhook Endpoint</th>
                <th className="py-2.5 px-3">Events</th>
                <th className="py-2.5 px-3">Secret Enabled</th>
                <th className="py-2.5 px-3">Deliveries</th>
                <th className="py-2.5 px-3 text-right">Test</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/60">
              {webhooks.map((webhook) => (
                <tr key={webhook.id}>
                  <td className="py-3 px-3 font-mono text-xs text-blue-600 dark:text-blue-400 max-w-xs truncate">
                    {webhook.url}
                  </td>
                  <td className="py-3 px-3 flex flex-wrap gap-1">
                    {webhook.events.map((evt) => (
                      <span key={evt} className="px-1.5 py-0.5 bg-neutral-100 dark:bg-neutral-800 rounded text-[10px] font-bold text-neutral-600 dark:text-neutral-300">
                        {evt}
                      </span>
                    ))}
                  </td>
                  <td className="py-3 px-3 font-semibold">{webhook.secretEnabled ? "Yes" : "No"}</td>
                  <td className="py-3 px-3 font-mono text-neutral-500">{webhook.deliveries}</td>
                  <td className="py-3 px-3 text-right">
                    <button
                      type="button"
                      onClick={() => onTestWebhook(webhook)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-bold text-purple-700 bg-purple-50 rounded border border-purple-200 hover:bg-purple-100"
                    >
                      <Zap className="h-3 w-3" />
                      Test Webhook
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function IconDynamic({ name }) {
  return (
    <div className="p-2 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center">
      <Plug className="h-4 w-4 text-neutral-500" />
    </div>
  );
}