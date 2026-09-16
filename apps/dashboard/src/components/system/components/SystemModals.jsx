"use client";

import { XCircle, KeyRound, Zap, AlertTriangle, RefreshCw } from "lucide-react";

export default function SystemModals({
  selectedAlert,
  onCloseAlert,
  onAcknowledge,
  onResolve,
  isKeyModalOpen,
  onCloseKey,
  newKeyName,
  onNewKeyName,
  newKeyRole,
  onNewKeyRole,
  onKeySubmit,
  isTestModalOpen,
  onCloseTest,
  testWebhook,
  testResponse,
  isTesting,
  onRunTest,
}) {
  return (
    <>
      {/* Alert Detail Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#121214] p-6 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-3">
              <h3 className="text-base font-bold tracking-tight">Alert Details - {selectedAlert.id}</h3>
              <button onClick={onCloseAlert} className="text-neutral-400 hover:text-white">
                <XCircle className="h-5 w-5" />
              </button>
            </div>

            <div className="flex flex-col gap-3 text-xs">
              <div className="flex flex-col gap-1 p-3 bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 rounded-lg">
                <span className="font-bold text-rose-700 dark:text-rose-400 text-sm">{selectedAlert.title}</span>
                <span className="text-neutral-600 dark:text-neutral-400">Source: {selectedAlert.service}</span>
                <span className="font-mono text-neutral-500">{selectedAlert.timestamp}</span>
              </div>
              <div><span className="font-bold">Severity:</span> {selectedAlert.severity}</div>
              <div><span className="font-bold">Status:</span> {selectedAlert.status}</div>
              {selectedAlert.acknowledgedBy && (
                <div><span className="font-bold">Acknowledged By:</span> {selectedAlert.acknowledgedBy}</div>
              )}
              {selectedAlert.resolvedAt && (
                <div><span className="font-bold">Resolved At:</span> {selectedAlert.resolvedAt}</div>
              )}
              <p className="text-neutral-600 dark:text-neutral-400 leading-relaxed">{selectedAlert.message}</p>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-neutral-200 dark:border-neutral-800">
              {selectedAlert.status === "ACTIVE" && (
                <button
                  type="button"
                  onClick={() => onAcknowledge(selectedAlert.id)}
                  className="px-4 py-1.5 text-xs font-bold text-amber-700 bg-amber-50 rounded-md border border-amber-200 hover:bg-amber-100"
                >
                  Acknowledge Incident
                </button>
              )}
              {selectedAlert.status !== "RESOLVED" && (
                <button
                  type="button"
                  onClick={() => onResolve(selectedAlert.id)}
                  className="px-4 py-1.5 text-xs font-bold text-white bg-emerald-600 rounded-md hover:bg-emerald-700"
                >
                  Mark Resolved
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Create API Key Modal */}
      {isKeyModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#121214] p-6 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-3">
              <h3 className="text-base font-bold flex items-center gap-2">
                <KeyRound className="h-5 w-5 text-blue-500" />
                Create API Key
              </h3>
              <button onClick={onCloseKey} className="text-neutral-400 hover:text-white">
                <XCircle className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={onKeySubmit} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold">Key Name</label>
                <input
                  type="text"
                  value={newKeyName}
                  onChange={(e) => onNewKeyName(e.target.value)}
                  placeholder="e.g. Analytics Sandbox Data Feed"
                  className="w-full rounded-md border border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-[#0d0d0d] px-3 py-2 text-sm outline-none focus:border-blue-500"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-bold">Role / Scoped Access</label>
                <select
                  value={newKeyRole}
                  onChange={(e) => onNewKeyRole(e.target.value)}
                  className="w-full rounded-md border border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-[#0d0d0d] px-3 py-2 text-sm outline-none focus:border-blue-500"
                >
                  <option>Lead Import Only</option>
                  <option>Read-Only CDR Analytics</option>
                  <option>Webhook Event Subscriber</option>
                  <option>Full Studio Pipeline Admin</option>
                </select>
              </div>
              <div className="flex justify-end gap-2 pt-2 border-t border-neutral-200 dark:border-neutral-800">
                <button
                  type="button"
                  onClick={onCloseKey}
                  className="px-4 py-2 text-xs font-bold text-neutral-600 bg-neutral-100 rounded-md"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700"
                >
                  Create Key
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Webhook Test Modal */}
      {isTestModalOpen && testWebhook && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#121214] p-6 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-3">
              <div className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-purple-500" />
                <h3 className="text-base font-bold">Webhook Endpoint Test</h3>
              </div>
              <button onClick={onCloseTest} className="text-neutral-400 hover:text-white">
                <XCircle className="h-5 w-5" />
              </button>
            </div>

            <div className="flex flex-col gap-2 text-xs">
              <div className="font-mono text-blue-600 dark:text-blue-400 break-all">{testWebhook.url}</div>
              <div className="flex flex-wrap gap-1">
                {testWebhook.events.map((evt) => (
                  <span key={evt} className="px-1.5 py-0.5 bg-neutral-100 dark:bg-neutral-800 rounded text-[10px] font-bold text-neutral-600 dark:text-neutral-300">
                    {evt}
                  </span>
                ))}
              </div>
            </div>

            {testResponse ? (
              <div className="flex flex-col gap-2 p-3 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5 font-bold text-emerald-700 dark:text-emerald-400">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    Delivery Succeeded - {testResponse.status} {testResponse.statusText}
                  </span>
                  <span className="font-mono text-[11px] text-emerald-600">{testResponse.latency}</span>
                </div>
                <pre className="text-[10px] font-mono text-neutral-600 dark:text-neutral-400 overflow-x-auto whitespace-pre-wrap">
                  {JSON.stringify(testResponse.payload, null, 2)}
                </pre>
              </div>
            ) : (
              !isTesting && (
                <div className="p-3 bg-neutral-50 dark:bg-[#151518] text-xs text-neutral-500 rounded-lg border border-neutral-200 dark:border-neutral-800">
                  Click “Send Test Ping” to deliver a sample <strong>system.health_ping</strong> event to this endpoint.
                </div>
              )
            )}

            <div className="flex justify-end gap-2 pt-3 border-t border-neutral-200 dark:border-neutral-800">
              {isTesting ? (
                <span className="inline-flex items-center gap-2 text-xs font-bold text-purple-600 px-4 py-2">
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Sending test payload...
                </span>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={onCloseTest}
                    className="px-4 py-2 text-xs font-bold text-neutral-600 bg-neutral-100 rounded-md"
                  >
                    Close
                  </button>
                  <button
                    type="button"
                    onClick={onRunTest}
                    className="px-4 py-2 text-xs font-bold text-white bg-purple-600 rounded-md hover:bg-purple-700"
                  >
                    Send Test Ping
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}