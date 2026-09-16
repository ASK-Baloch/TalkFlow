"use client";

import { ArrowLeft } from "lucide-react";

export default function SystemAlertsView({
  filteredAlerts,
  severityFilter,
  alertStatusFilter,
  onSeverityFilterChange,
  onAlertStatusFilterChange,
  onSelectAlert,
  onAcknowledge,
  onResolve,
  onOpenDetails,
}) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-4">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => onSelectAlert(null)}
            className="p-1.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-neutral-600 hover:text-neutral-900"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            <h2 className="text-xl font-bold text-neutral-900 dark:text-white">
              Active & Historical Infrastructure Alerts
            </h2>
            <p className="text-xs text-neutral-500">
              Real-time incident alerts, PRD §13 transfer-failure warnings, trunk jitter alerts, and operational audit log.
            </p>
          </div>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <span className="font-bold text-neutral-500">Filter Severity:</span>
          <select
            value={severityFilter}
            onChange={(e) => onSeverityFilterChange(e.target.value)}
            className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] px-3 py-1.5 outline-none font-semibold"
          >
            <option value="all">All Severities</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="WARNING">WARNING</option>
            <option value="INFO">INFO</option>
          </select>

          <span className="font-bold text-neutral-500 ml-2">Status:</span>
          <select
            value={alertStatusFilter}
            onChange={(e) => onAlertStatusFilterChange(e.target.value)}
            className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] px-3 py-1.5 outline-none font-semibold"
          >
            <option value="all">All Statuses</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
            <option value="RESOLVED">RESOLVED</option>
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[850px] text-xs text-left border-collapse">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-800 text-neutral-500 uppercase text-[11px]">
                <th className="py-2.5 px-3">Severity</th>
                <th className="py-2.5 px-3">Incident Title</th>
                <th className="py-2.5 px-3">Source Subsystem</th>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3 text-right">Incident Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/60">
              {filteredAlerts.map((alt) => (
                <tr
                  key={alt.id}
                  onClick={() => onSelectAlert(alt)}
                  className="hover:bg-neutral-50 dark:hover:bg-neutral-900/50 cursor-pointer"
                >
                  <td className="py-3.5 px-3">
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                      alt.severity === "CRITICAL"
                        ? "bg-rose-100 text-rose-700 border border-rose-300 dark:bg-rose-950/60 dark:text-rose-400 dark:border-rose-800"
                        : alt.severity === "WARNING"
                        ? "bg-amber-100 text-amber-700 border border-amber-300 dark:bg-amber-950/60 dark:text-amber-400 dark:border-amber-800"
                        : "bg-blue-100 text-blue-700 border border-blue-300 dark:bg-blue-950/60 dark:text-blue-400 dark:border-blue-800"
                    }`}>
                      {alt.severity}
                    </span>
                  </td>
                  <td className="py-3.5 px-3 font-bold text-neutral-900 dark:text-white max-w-xs truncate">
                    {alt.title}
                  </td>
                  <td className="py-3.5 px-3 text-neutral-500 font-semibold">{alt.service}</td>
                  <td className="py-3.5 px-3 font-mono text-neutral-500">{alt.timestamp}</td>
                  <td className="py-3.5 px-3">
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                      alt.status === "ACTIVE"
                        ? "bg-rose-100 text-rose-700"
                        : alt.status === "ACKNOWLEDGED"
                        ? "bg-amber-100 text-amber-700"
                        : "bg-emerald-100 text-emerald-700"
                    }`}>
                      {alt.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-3 text-right" onClick={(e) => e.stopPropagation()}>
                    <div className="flex items-center justify-end gap-1.5">
                      {alt.status === "ACTIVE" && (
                        <button
                          type="button"
                          onClick={() => onAcknowledge(alt.id)}
                          className="px-2.5 py-1 text-[11px] font-bold text-amber-700 bg-amber-50 rounded border border-amber-200 hover:bg-amber-100"
                        >
                          Acknowledge
                        </button>
                      )}
                      {alt.status !== "RESOLVED" && (
                        <button
                          type="button"
                          onClick={() => onResolve(alt.id)}
                          className="px-2.5 py-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 rounded border border-emerald-200 hover:bg-emerald-100"
                        >
                          Resolve
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => onOpenDetails(alt)}
                        className="px-2.5 py-1 text-[11px] font-bold text-neutral-600 bg-neutral-100 rounded hover:bg-neutral-200 dark:bg-neutral-800 dark:text-neutral-300"
                      >
                        Details
                      </button>
                    </div>
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