"use client";

export default function CampaignTransferRules({ campaign }) {
  return (
    <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-6 shadow-xs flex flex-col gap-6">
      <div>
        <h3 className="text-base font-bold text-neutral-900 dark:text-white">
          Verifier Pool & Transfer Rules
        </h3>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
        <div className="flex flex-col gap-1 bg-neutral-50 dark:bg-[#151518] p-4 rounded-lg border border-neutral-200 dark:border-neutral-800">
          <span className="font-semibold text-neutral-500">Target Verifier Pool</span>
          <span className="text-sm font-bold">{campaign.transfer?.verifierPool || "Licensed QA Verifier Pool"}</span>
        </div>
        <div className="flex flex-col gap-1 bg-neutral-50 dark:bg-[#151518] p-4 rounded-lg border border-neutral-200 dark:border-neutral-800">
          <span className="font-semibold text-neutral-500">Transfer Mode</span>
          <span className="text-sm font-bold text-blue-600">{campaign.transfer?.transferRules || "Warm Transfer"}</span>
        </div>
      </div>
    </div>
  );
}