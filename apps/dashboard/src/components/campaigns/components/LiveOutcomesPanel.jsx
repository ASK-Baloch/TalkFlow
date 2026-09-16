"use client";

export default function LiveOutcomesPanel({ liveOutcomes }) {
  return (
    <div className="flex flex-col gap-5">
      <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
        <div className="w-full overflow-x-auto">
          <table className="w-full min-w-[850px] border-collapse text-xs text-left">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-400 font-semibold uppercase text-[11px]">
                <th className="px-4 py-3">Time</th>
                <th className="px-4 py-3">Campaign</th>
                <th className="px-4 py-3">Agent</th>
                <th className="px-4 py-3">Customer Phone</th>
                <th className="px-4 py-3">Disposition</th>
                <th className="px-4 py-3">Duration</th>
                <th className="px-4 py-3">AMD Result</th>
                <th className="px-4 py-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/60">
              {liveOutcomes.map((out) => (
                <tr key={out.id} className="transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900/50">
                  <td className="px-4 py-4 font-bold text-neutral-900 dark:text-white">{out.time}</td>
                  <td className="px-4 py-4 font-semibold text-neutral-800 dark:text-neutral-200">{out.campaignName}</td>
                  <td className="px-4 py-4 text-neutral-700">{out.agentName}</td>
                  <td className="px-4 py-4 font-mono text-neutral-500">{out.customer}</td>
                  <td className="px-4 py-4 font-bold text-blue-600">{out.disposition}</td>
                  <td className="px-4 py-4 text-neutral-500">{out.duration}</td>
                  <td className="px-4 py-4 font-semibold">{out.amdResult}</td>
                  <td className="px-4 py-4 text-right font-bold text-emerald-600">{out.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}