"use client";

import { ShieldAlert } from "lucide-react";

export default function SuppressionListView({ suppressionList, onAddDnc }) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-neutral-900 dark:text-white">
            DNC & Opt-Out Suppression Lists
          </h3>
          <p className="text-xs text-neutral-500 dark:text-neutral-400">
            Scrubbed phone numbers automatically blocked from auto-dialers and outreach campaigns
          </p>
        </div>

        <button
          type="button"
          onClick={onAddDnc}
          className="inline-flex items-center gap-1.5 rounded-md bg-rose-600 hover:bg-rose-700 text-white px-3.5 py-1.5 text-xs font-bold shadow-xs transition-colors"
        >
          <ShieldAlert className="h-4 w-4" />
          <span>Add Phone to DNC</span>
        </button>
      </div>

      <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
        <div className="w-full overflow-x-auto">
          <table className="w-full min-w-[800px] border-collapse text-xs text-left">
            <thead>
              <tr className="border-b border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-400 font-semibold uppercase text-[11px]">
                <th className="px-4 py-3">Phone Number</th>
                <th className="px-4 py-3">Suppression Reason</th>
                <th className="px-4 py-3">Added By</th>
                <th className="px-4 py-3">Source</th>
                <th className="px-4 py-3">Date Added</th>
                <th className="px-4 py-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/60">
              {suppressionList.map((dnc) => (
                <tr
                  key={dnc.id}
                  className="transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900/50"
                >
                  <td className="px-4 py-4 font-mono font-bold text-rose-600 dark:text-rose-400">
                    {dnc.phone}
                  </td>
                  <td className="px-4 py-4 font-semibold text-neutral-800 dark:text-neutral-200">
                    {dnc.reason}
                  </td>
                  <td className="px-4 py-4 text-neutral-700 dark:text-neutral-300">
                    {dnc.addedBy}
                  </td>
                  <td className="px-4 py-4 text-neutral-500 dark:text-neutral-400">
                    {dnc.source}
                  </td>
                  <td className="px-4 py-4 text-neutral-500 dark:text-neutral-400">
                    {dnc.dateAdded}
                  </td>
                  <td className="px-4 py-4 text-right">
                    <span className="inline-flex items-center gap-1 rounded-full bg-rose-50 dark:bg-rose-950/80 px-2.5 py-0.5 text-xs font-bold text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-800">
                      <ShieldAlert className="h-3 w-3" />
                      {dnc.status}
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