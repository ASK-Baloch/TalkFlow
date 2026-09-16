"use client";

import { Search, Activity } from "lucide-react";

export default function CallHistoryView({
  totalCallsCount,
  passedCount,
  liveCount,
  searchQuery,
  onSearchChange,
  dispositionFilter,
  onDispositionFilterChange,
  filteredCalls,
  onOpenLive,
  onOpenCall,
}) {
  return (
    <div className="flex flex-col gap-6">
      {/* Header Title & Navigation Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-200 dark:border-neutral-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-white tracking-tight">
              Call History & CDR Records
            </h1>
            <span className="rounded-full bg-emerald-100 dark:bg-emerald-950/80 border border-emerald-300 dark:border-emerald-800 px-2.5 py-0.5 text-[10px] font-bold text-emerald-700 dark:text-emerald-400">
              {totalCallsCount} Total Logged
            </span>
          </div>
          <p className="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
            Detailed call detail records, transcripts, disposition logs, and audio recordings.
          </p>
        </div>

        <button
          type="button"
          onClick={onOpenLive}
          className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-xs font-bold text-white shadow-xs hover:bg-emerald-700 transition-colors"
        >
          <Activity className="h-4 w-4 animate-pulse" />
          <span>Live Call Monitoring</span>
          <span className="ml-1 rounded-full bg-white/20 px-2 py-0.2 text-[10px]">
            {liveCount} Active
          </span>
        </button>
      </div>

      {/* Quick Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs">
          <span className="text-xs text-neutral-500 font-medium">Total Calls Logged</span>
          <div className="text-2xl font-extrabold text-neutral-900 dark:text-white mt-1">
            {totalCallsCount}
          </div>
        </div>
        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs">
          <span className="text-xs text-neutral-500 font-medium">Qualified Sales</span>
          <div className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1">
            {passedCount}
          </div>
        </div>
        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs">
          <span className="text-xs text-neutral-500 font-medium">Avg Handle Time</span>
          <div className="text-2xl font-extrabold text-blue-600 dark:text-blue-400 mt-1">
            02:15
          </div>
        </div>
        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs">
          <span className="text-xs text-neutral-500 font-medium">QA Audit Pass Rate</span>
          <div className="text-2xl font-extrabold text-purple-600 dark:text-purple-400 mt-1">
            96.4%
          </div>
        </div>
      </div>

      {/* Search & Disposition Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-neutral-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search Call ID, lead name, phone, agent..."
            className="w-full rounded-lg border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] py-2 pl-9 pr-3 text-xs text-neutral-900 dark:text-white outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center rounded-lg border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-1 text-xs shadow-xs">
          {[
            { id: "all", label: "All Calls" },
            { id: "sale", label: "Sales" },
            { id: "raxfer", label: "Warm Transfer" },
            { id: "dnc", label: "DNC / Opt-Out" },
          ].map((filter) => (
            <button
              key={filter.id}
              type="button"
              onClick={() => onDispositionFilterChange(filter.id)}
              className={`rounded-md px-3 py-1 font-semibold text-[11px] transition-colors ${
                dispositionFilter === filter.id
                  ? "bg-blue-600 text-white shadow-xs"
                  : "text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main CDR Table */}
      <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] border-collapse text-xs text-left">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-400 font-semibold uppercase tracking-wider text-[11px]">
                <th className="px-4 py-3">Call ID</th>
                <th className="px-4 py-3">Customer / Phone</th>
                <th className="px-4 py-3">Campaign</th>
                <th className="px-4 py-3">Disposition</th>
                <th className="px-4 py-3">Duration</th>
                <th className="px-4 py-3">Agent</th>
                <th className="px-4 py-3">QA Score</th>
                <th className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/60">
              {filteredCalls.map((call) => (
                <tr
                  key={call.id}
                  onClick={() => onOpenCall(call.id)}
                  className="cursor-pointer transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900/50"
                >
                  <td className="px-4 py-4 font-mono font-bold text-blue-600 dark:text-blue-400 hover:underline">
                    {call.callId}
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex flex-col">
                      <span className="font-bold text-neutral-900 dark:text-white">
                        {call.leadName}
                      </span>
                      <span className="font-mono text-[11px] text-neutral-500">
                        {call.phone}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-4 font-semibold text-neutral-800 dark:text-neutral-200">
                    {call.campaign}
                  </td>
                  <td className="px-4 py-4">
                    {call.disposition.includes("SALE") && (
                      <span className="inline-flex items-center gap-1 rounded-full border border-emerald-300 bg-emerald-50 px-2.5 py-0.5 text-xs font-bold text-emerald-700">
                        {call.disposition}
                      </span>
                    )}
                    {call.disposition.includes("RAXFER") && (
                      <span className="inline-flex items-center gap-1 rounded-full border border-blue-300 bg-blue-50 px-2.5 py-0.5 text-xs font-bold text-blue-700">
                        {call.disposition}
                      </span>
                    )}
                    {call.disposition.includes("DNC") && (
                      <span className="inline-flex items-center gap-1 rounded-full border border-rose-300 bg-rose-50 px-2.5 py-0.5 text-xs font-bold text-rose-700">
                        {call.disposition}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-4 font-mono text-neutral-600 dark:text-neutral-400">
                    {call.duration}
                  </td>
                  <td className="px-4 py-4 text-neutral-700 dark:text-neutral-300 font-medium">
                    {call.agent}
                  </td>
                  <td className="px-4 py-4 font-bold text-emerald-600">
                    {call.qaScore}%
                  </td>
                  <td className="px-4 py-4 text-right">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onOpenCall(call.id);
                      }}
                      className="inline-flex items-center gap-1 rounded-md border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 px-3 py-1 text-xs font-semibold hover:bg-neutral-100"
                    >
                      <span>View Detail</span>
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