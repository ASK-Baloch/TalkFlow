"use client";

import { useState } from "react";
import { Eye, X } from "lucide-react";

export default function ActiveScriptsPanel({ activeScripts }) {
  const [previewScript, setPreviewScript] = useState(null);

  return (
    <>
      <div className="flex flex-col gap-5">
        <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
          <div className="w-full overflow-x-auto">
            <table className="w-full min-w-[800px] border-collapse text-xs text-left">
              <thead>
                <tr className="border-b border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-400 font-semibold uppercase text-[11px]">
                  <th className="px-4 py-3">Campaign</th>
                  <th className="px-4 py-3">Active Script Title</th>
                  <th className="px-4 py-3">Version</th>
                  <th className="px-4 py-3">Dialer Status</th>
                  <th className="px-4 py-3">Compliance Check</th>
                  <th className="px-4 py-3">Last Modified</th>
                  <th className="px-4 py-3">Author</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/60">
                {activeScripts.map((scr) => (
                  <tr key={scr.id} className="transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900/50">
                    <td className="px-4 py-4 font-bold text-neutral-900 dark:text-white">{scr.campaignName}</td>
                    <td className="px-4 py-4 font-semibold text-neutral-800 dark:text-neutral-200">{scr.scriptTitle}</td>
                    <td className="px-4 py-4 font-mono">
                      <span className="rounded bg-neutral-100 dark:bg-neutral-800 px-2 py-0.5 text-xs font-bold border border-neutral-200 dark:border-neutral-700">
                        {scr.version}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-300 bg-emerald-50 px-2.5 py-0.5 text-xs font-bold text-emerald-700">
                        Active in Dialer
                      </span>
                    </td>
                    <td className="px-4 py-4 text-emerald-600 font-semibold">{scr.complianceCheck}</td>
                    <td className="px-4 py-4 text-neutral-500">{scr.lastUpdated}</td>
                    <td className="px-4 py-4 text-neutral-700">{scr.author}</td>
                    <td className="px-4 py-4 text-right">
                      <button
                        type="button"
                        onClick={() => setPreviewScript(scr)}
                        className="inline-flex items-center gap-1 rounded-md border border-neutral-300 dark:border-neutral-700 px-2.5 py-1 text-xs font-semibold text-neutral-700 dark:text-neutral-200 hover:bg-neutral-100"
                      >
                        <Eye className="h-3.5 w-3.5" />
                        <span>Preview</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {previewScript && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="w-full max-w-lg rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#121214] p-6 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-3">
              <div>
                <h3 className="text-base font-bold">{previewScript.scriptTitle}</h3>
                <span className="text-xs text-neutral-500">Bound to: {previewScript.campaignName} ({previewScript.version})</span>
              </div>
              <button onClick={() => setPreviewScript(null)} className="text-neutral-400 hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="flex flex-col gap-3 max-h-80 overflow-y-auto bg-neutral-50 dark:bg-[#18181b] p-4 rounded-lg text-xs leading-relaxed">
              <p className="font-bold text-blue-600">[Opening Greeting]</p>
              <p>&quot;Hello, my name is [Agent Name] calling on behalf of [Company]. How are you doing today?&quot;</p>
              <p className="font-bold text-blue-600">[Qualification Check]</p>
              <p>&quot;I am reaching out to confirm your recent request regarding our services.&quot;</p>
            </div>
            <div className="flex justify-end pt-3 border-t border-neutral-200 dark:border-neutral-800">
              <button type="button" onClick={() => setPreviewScript(null)} className="px-4 py-1.5 text-xs font-bold bg-blue-600 text-white rounded-md">
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}