"use client";

export default function CampaignDialingForm({ campaign }) {
  return (
    <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-6 shadow-xs flex flex-col gap-6">
      <div>
        <h3 className="text-base font-bold text-neutral-900 dark:text-white">
          Dialing Settings
        </h3>
        <p className="text-xs text-neutral-500 dark:text-neutral-400">
          Configure calling hours, retries, caller ID pool, and pacing multiplier
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
        <div className="flex flex-col gap-1 bg-neutral-50 dark:bg-[#151518] p-4 rounded-lg border border-neutral-200 dark:border-neutral-800">
          <span className="font-semibold text-neutral-500">Active Calling Hours</span>
          <span className="text-sm font-bold">{campaign.dialing?.hours || "09:00 - 18:00 EST"}</span>
        </div>
        <div className="flex flex-col gap-1 bg-neutral-50 dark:bg-[#151518] p-4 rounded-lg border border-neutral-200 dark:border-neutral-800">
          <span className="font-semibold text-neutral-500">Max Lead Dial Retries</span>
          <span className="text-sm font-bold">{campaign.dialing?.maxRetries || 5} Attempts</span>
        </div>
        <div className="flex flex-col gap-1 bg-neutral-50 dark:bg-[#151518] p-4 rounded-lg border border-neutral-200 dark:border-neutral-800">
          <span className="font-semibold text-neutral-500">Dialer Pacing Ratio</span>
          <span className="text-sm font-bold text-blue-600">{campaign.dialing?.pacing || "Ratio 2.5x"}</span>
        </div>
        <div className="flex flex-col gap-1 bg-neutral-50 dark:bg-[#151518] p-4 rounded-lg border border-neutral-200 dark:border-neutral-800">
          <span className="font-semibold text-neutral-500">Drop Call Timeout</span>
          <span className="text-sm font-bold text-amber-600">{campaign.dialing?.dropTimeout || "3.0s"}</span>
        </div>
      </div>
    </div>
  );
}