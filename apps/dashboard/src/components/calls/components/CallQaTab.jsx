"use client";

export default function CallQaTab({ call }) {
  return (
    <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-6 shadow-xs flex flex-col gap-6 max-w-3xl">
      <div>
        <h3 className="text-base font-bold">Quality Audit & Agent Performance Notes</h3>
      </div>

      <div className="flex flex-col gap-4 text-xs">
        <div className="flex items-center justify-between p-4 bg-emerald-50 dark:bg-emerald-950/30 rounded-xl border border-emerald-200 dark:border-emerald-800">
          <div>
            <span className="font-bold text-emerald-800 dark:text-emerald-300">QA Score Approved</span>
            <p className="text-neutral-600 dark:text-neutral-400 mt-0.5">{call.qaStatus}</p>
          </div>
          <span className="text-2xl font-extrabold text-emerald-600">{call.qaScore}%</span>
        </div>

        <div className="flex flex-col gap-2">
          <label className="font-bold text-neutral-800 dark:text-neutral-200">
            Supervisor / Evaluator Notes
          </label>
          <textarea
            rows={4}
            defaultValue={call.notes}
            className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] p-3 text-xs outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex justify-end pt-2 border-t border-neutral-200 dark:border-neutral-800">
          <button
            type="button"
            className="px-4 py-2 bg-blue-600 text-white font-bold rounded-md hover:bg-blue-700"
          >
            Save QA Audit
          </button>
        </div>
      </div>
    </div>
  );
}