"use client";

import { CAMPAIGN_PERFORMANCE_METRICS } from "@/data";

export default function CampaignMetricsGrid() {
  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs flex flex-col gap-1">
          <span className="text-xs font-medium text-neutral-500 dark:text-neutral-400">
            Total Dialed Calls
          </span>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-2xl font-extrabold text-neutral-900 dark:text-white">
              {CAMPAIGN_PERFORMANCE_METRICS.kpis.totalCalls}
            </span>
            <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800/60">
              +12.4%
            </span>
          </div>
        </div>

        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs flex flex-col gap-1">
          <span className="text-xs font-medium text-neutral-500 dark:text-neutral-400">
            Avg Contact Rate
          </span>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-2xl font-extrabold text-neutral-900 dark:text-white">
              {CAMPAIGN_PERFORMANCE_METRICS.kpis.contactRate}
            </span>
            <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800/60">
              +3.1%
            </span>
          </div>
        </div>

        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs flex flex-col gap-1">
          <span className="text-xs font-medium text-neutral-500 dark:text-neutral-400">
            Avg Conversion Rate
          </span>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-2xl font-extrabold text-blue-600 dark:text-blue-400">
              {CAMPAIGN_PERFORMANCE_METRICS.kpis.conversionRate}
            </span>
            <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800/60">
              +5.8%
            </span>
          </div>
        </div>

        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs flex flex-col gap-1">
          <span className="text-xs font-medium text-neutral-500 dark:text-neutral-400">
            Avg Handle Time (AHT)
          </span>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-2xl font-extrabold text-neutral-900 dark:text-white">
              {CAMPAIGN_PERFORMANCE_METRICS.kpis.avgHandleTime}
            </span>
            <span className="text-xs font-bold text-neutral-600 dark:text-neutral-400 bg-neutral-100 dark:bg-neutral-800 px-2 py-0.5 rounded-full">
              Optimal
            </span>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4">
        <h3 className="text-base font-bold text-neutral-900 dark:text-white">
          Campaign Conversion & Contact Breakdown
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[850px] border-collapse text-xs text-left">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-400 font-semibold uppercase tracking-wider text-[11px]">
                <th className="px-4 py-3">Campaign</th>
                <th className="px-4 py-3">Calls Dialed</th>
                <th className="px-4 py-3">Answered</th>
                <th className="px-4 py-3">Contact Rate</th>
                <th className="px-4 py-3">Conversions</th>
                <th className="px-4 py-3">Conv. Rate</th>
                <th className="px-4 py-3">Avg Duration</th>
                <th className="px-4 py-3">Drop %</th>
                <th className="px-4 py-3">Trend</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/60">
              {CAMPAIGN_PERFORMANCE_METRICS.rows.map((row) => (
                <tr key={row.id} className="transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900/50">
                  <td className="px-4 py-3.5 font-bold text-neutral-900 dark:text-white">{row.campaignName}</td>
                  <td className="px-4 py-3.5 font-mono">{row.callsDialed.toLocaleString()}</td>
                  <td className="px-4 py-3.5 font-mono">{row.answered.toLocaleString()}</td>
                  <td className="px-4 py-3.5 font-semibold">{row.contactRate}</td>
                  <td className="px-4 py-3.5 font-bold text-emerald-600 font-mono">{row.conversions.toLocaleString()}</td>
                  <td className="px-4 py-3.5 font-extrabold text-blue-600">{row.conversionRate}</td>
                  <td className="px-4 py-3.5 text-neutral-500">{row.avgDuration}</td>
                  <td className="px-4 py-3.5 font-mono text-amber-600">{row.dropRate}</td>
                  <td className="px-4 py-3.5">
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-bold ${row.trend.startsWith("+") ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700"}`}>
                      {row.trend}
                    </span>
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