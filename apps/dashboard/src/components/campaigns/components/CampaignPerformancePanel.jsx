"use client";

export default function CampaignPerformancePanel({ campaign }) {
  return (
    <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-6 shadow-xs flex flex-col gap-6">
      <div>
        <h3 className="text-base font-bold text-neutral-900 dark:text-white">
          Campaign Analytics
        </h3>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
        <div className="flex flex-col gap-1 bg-neutral-50 dark:bg-[#151518] p-4 rounded-lg border border-neutral-200 dark:border-neutral-800">
          <span className="text-neutral-500">Total Dialed Calls</span>
          <span className="text-xl font-extrabold">{campaign.performance?.callsDialed || "45,210"}</span>
        </div>
        <div className="flex flex-col gap-1 bg-neutral-50 dark:bg-[#151518] p-4 rounded-lg border border-neutral-200 dark:border-neutral-800">
          <span className="text-neutral-500">Contact Rate</span>
          <span className="text-xl font-extrabold text-emerald-600">{campaign.performance?.contactRate || "70.0%"}</span>
        </div>
        <div className="flex flex-col gap-1 bg-neutral-50 dark:bg-[#151518] p-4 rounded-lg border border-neutral-200 dark:border-neutral-800">
          <span className="text-neutral-500">Conversions</span>
          <span className="text-xl font-extrabold text-blue-600">{campaign.performance?.conversions || "5,410"}</span>
        </div>
        <div className="flex flex-col gap-1 bg-neutral-50 dark:bg-[#151518] p-4 rounded-lg border border-neutral-200 dark:border-neutral-800">
          <span className="text-neutral-500">Avg Handle Time</span>
          <span className="text-xl font-extrabold">{campaign.performance?.avgDuration || "4m 12s"}</span>
        </div>
      </div>
    </div>
  );
}