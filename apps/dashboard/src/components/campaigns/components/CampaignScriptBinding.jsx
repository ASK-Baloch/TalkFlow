"use client";

export default function CampaignScriptBinding({ campaign }) {
  return (
    <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-6 shadow-xs flex flex-col gap-6">
      <div>
        <h3 className="text-base font-bold text-neutral-900 dark:text-white">
          Active Script Binding
        </h3>
      </div>

      <div className="bg-blue-50 dark:bg-blue-950/40 p-4 rounded-xl border border-blue-200 dark:border-blue-800 flex items-center justify-between text-xs">
        <div className="flex flex-col gap-0.5">
          <span className="font-bold text-blue-700 dark:text-blue-300 text-sm">
            {campaign.script?.activeScript || "Medical Qualification Script v3"}
          </span>
          <span className="text-neutral-500">
            Bound Version: {campaign.script?.version || "v3.2.0"}
          </span>
        </div>
        <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-700 font-bold border border-emerald-300">
          ACTIVE_IN_DIALER
        </span>
      </div>
    </div>
  );
}