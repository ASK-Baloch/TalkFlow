"use client";

export default function CampaignRoutingForm({ campaign }) {
  return (
    <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-6 shadow-xs flex flex-col gap-6">
      <div>
        <h3 className="text-base font-bold text-neutral-900 dark:text-white">
          Inbound & DID Routing
        </h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left border-collapse">
          <thead>
            <tr className="border-b border-neutral-200 dark:border-neutral-800 text-neutral-500 uppercase text-[11px]">
              <th className="py-2.5 px-3">Mapped DID</th>
              <th className="py-2.5 px-3">Target Inbound Queue</th>
              <th className="py-2.5 px-3">Fallback Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/60">
            {(campaign.routing?.didMappings || []).map((map, idx) => (
              <tr key={idx}>
                <td className="py-3 px-3 font-mono font-bold text-blue-600">{map.did}</td>
                <td className="py-3 px-3 font-bold">{map.queue}</td>
                <td className="py-3 px-3 text-neutral-500">{map.fallback}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}